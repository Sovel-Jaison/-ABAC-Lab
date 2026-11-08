from PyQt5.QtWidgets import QLabel, QSizePolicy, QHBoxLayout, QComboBox, QMessageBox, QPushButton, QFileDialog, QWidget, QLabel, QGridLayout
from PyQt5.QtCore import Qt
import os

def precompute_all_stats(app):
    """
    Precomputes statistics for all uploaded ABAC files and stores them in app.abac_stats
    """
    app.abac_stats = {}  # Dictionary to store precomputed stats
    for abac_path in app.abac_data.keys():
        app.abac_stats[abac_path] = get_abac_stats(app, abac_path)

def show_stats(app):
    """
    Displays the statistics for the uploaded ABAC files.
    Uses precomputed stats for quick display.
    """
    # Clear previous stats from the stats container
    while app.stats_container_layout.count():
        item = app.stats_container_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            while item.layout().count():
                sub_item = item.layout().takeAt(0)
                if sub_item.widget():
                    sub_item.widget().deleteLater()
            item.layout().deleteLater()

    # If no files are uploaded, display a message and return
    if not app.uploaded_files:
        no_files_label = QLabel("No files uploaded. Please upload files to view statistics.")
        no_files_label.setStyleSheet("font-size: 14px; color: black; border: none;")
        no_files_label.setAlignment(Qt.AlignCenter)
        app.stats_container_layout.addWidget(no_files_label)
        return
    
    # Create a dropdown menu to select files
    app.file_dropdown = QComboBox()
    file_paths = list(app.abac_data.keys())
    app.file_dropdown.addItems([os.path.basename(path) for path in file_paths])
    app.file_dropdown.currentIndexChanged.connect(lambda index: display_stats(app, file_paths[index]))
    app.file_dropdown.setStyleSheet("font-size: 16px; color: black; border: 2px solid black;")
    app.file_dropdown.setFixedSize(200, 40)

    dropdown_label = QLabel("Policy:")
    dropdown_label.setStyleSheet("font-size: 30px; color: black; border: none;")
    dropdown_label.setAlignment(Qt.AlignRight)

    # Layout for dropdown and Save button
    top_bar_layout = QHBoxLayout()
    top_bar_layout.addWidget(dropdown_label, alignment=Qt.AlignRight)
    top_bar_layout.addWidget(app.file_dropdown, alignment=Qt.AlignLeft)
    top_bar_layout.setAlignment(Qt.AlignCenter)

    # Add the top bar layout to the stats container
    app.stats_container_layout.addLayout(top_bar_layout)
    
    # Display stats for the first file by default
    if app.current_abac_path:
        app.file_dropdown.setCurrentIndex(file_paths.index(app.current_abac_path))
        display_stats(app, app.current_abac_path)
    else:
        app.current_abac_path = file_paths[0]
        display_stats(app, file_paths[0])

def get_abac_stats(app, abac_path):
    """
    Compute statistics from the ABAC data.
    Ensures that duplicate permissions (user, resource, action) are not counted.
    """
    user_mgr, res_mgr, rule_mgr = app.abac_data[abac_path]
    total_users = len(user_mgr.users)
    total_resources = len(res_mgr.resources)

    # Gather unique user attributes
    user_attrs = set()
    for user in user_mgr.users.values():
        user_attrs.update(user.attributes.keys())
    total_user_attrs = len(user_attrs)

    # Gather unique resource attributes
    resource_attrs = set()
    for resource in res_mgr.resources.values():
        resource_attrs.update(resource.attributes.keys())
    total_resource_attrs = len(resource_attrs)

    total_rules = len(rule_mgr.rules)

    # Use a set to track unique permissions
    unique_permissions = set()

    # Calculate total permissions granted, ensuring no duplicates
    for rule in rule_mgr.rules:
        for action in rule.acts:
            for user_name, user in user_mgr.users.items():
                for resource_name, resource in res_mgr.resources.items():
                    if rule.evaluate(user, resource, action):
                        # Create a permission key (user_name, resource_name, action)
                        permission_key = (user_name, resource_name, action)
                        unique_permissions.add(permission_key)

    # Total unique permissions
    total_permissions = len(unique_permissions)

    stats = {
        "Total Users": total_users,
        "Total Resources": total_resources,
        "Total User Attributes": total_user_attrs,
        "Total Resource Attributes": total_resource_attrs,
        "Total Rules": total_rules,
        "Total Permissions Granted": total_permissions
    }
    return stats

def display_stats(app, abac_path):
    """
    Displays the precomputed statistics for the specified ABAC file.
    """
    # Store the current ABAC path for saving
    app.current_abac_path = abac_path

    # Get precomputed stats
    stats = app.abac_stats.get(abac_path, {})

    # Clear previous stats content (except dropdown and Save button)
    while app.stats_container_layout.count() > 1:
        item = app.stats_container_layout.takeAt(1)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
    
    # Create a grid layout for the stats
    stats_layout = QGridLayout()
    stats_layout.setContentsMargins(10, 10, 10, 10)
    stats_layout.setSpacing(10)

    # Add stats to the grid layout
    for row, (key, value) in enumerate(stats.items()):
        # Create a label for the key (aligned left)
        key_label = QLabel(key)
        key_label.setStyleSheet("font-size: 16px; color: black; border: none;")
        key_label.setAlignment(Qt.AlignLeft)
        key_label.setFixedHeight(20)

        # Create a label for the value (aligned right)
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-size: 16px; color: black; border: none;")
        value_label.setAlignment(Qt.AlignRight)
        value_label.setFixedHeight(20)

        # Add the labels to the grid layout
        stats_layout.addWidget(key_label, row, 0)  # Key in the first column
        stats_layout.addWidget(value_label, row, 1)  # Value in the second column

    # Create a QWidget to hold the grid layout
    stats_widget = QWidget()
    stats_widget.setLayout(stats_layout)

    # Add the stats label to the stats container layout
    app.stats_container_layout.addWidget(stats_widget, alignment=Qt.AlignTop)

def save_abac_stats(app, abac_path):
    """
    Saves the ABAC statistics for the specified file to a .txt file.
    Adds the ABAC file name as the first line in the file.
    """
    if not app.current_abac_path:
        QMessageBox.warning(app, "Warning", "Please upload an ABAC file first.")
        return
    
    # Get the precomputed statistics
    stats = app.abac_stats.get(abac_path, {})
    stats_text = "\n".join(f"{key}: {value}" for key, value in stats.items())

    # Extract the ABAC file name from the path
    abac_name = os.path.basename(abac_path)

    # Prepend the ABAC file name to the stats text
    stats_text_with_name = f"ABAC File: {abac_name}\n\n{stats_text}"

    # Open a file dialog to choose the save location
    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(app, "Save Statistics", "", "Text Files (*.txt);;All Files (*)", options=options)

    if save_path:
        try:
            with open(save_path, 'w') as file:
                file.write(stats_text_with_name)  # Write the modified text
            QMessageBox.information(app, "Success", "Statistics saved successfully.")
        except Exception as e:
            QMessageBox.warning(app, "Error", f"Failed to save statistics: {str(e)}")