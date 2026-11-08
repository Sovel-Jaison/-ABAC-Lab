import re
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QGridLayout,
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QSizePolicy, QInputDialog
)
from PyQt5.QtCore import Qt
from core.myabac import process_request

def show_permissions(app):
    """
    Allows the user to upload multiple request files and associate them with ABAC files.
    Displays the permissions results for the selected request files.
    If the user cancels the file association, the function exits and returns to the Permissions Choices page.
    """
    app.stats_widget.hide()
    app.perm_widget.hide()
    app.bar_graph_widget.hide()
    app.heat_map_widget.hide()
    app.rule_widget.hide()
    app.rule_perm_lbl.hide()
    app.rule_perm_btn.hide()
    app.heat_map_lbl.hide()
    app.heatmap_btn_page2.hide()
    app.perm_btn.hide()
    app.permissions_lbl.hide()
    app.bar_graph_btn.hide()
    app.bar_grph_lbl.hide()
    app.stats_container.hide()
    app.page2_label.hide()

    if not app.abac_data:
        QMessageBox.warning(app, "Warning", "Please upload an ABAC file first.")
        return

    # If only one ABAC file is uploaded, skip the association dialog
    if len(app.abac_data) == 1:
        abac_file = list(app.abac_data.keys())[0]
        
        # Allow users to select multiple request files
        options = QFileDialog.Options()
        request_files, _ = QFileDialog.getOpenFileNames(
            app, "Select Permissions Request Files", "",
            "Text Files (*.txt);;All Files (*)", options=options
        )

        # If no files are selected or the user cancels, return to the Permissions Choices page
        if not request_files:
            app.show_permissions_choice()  # Go back to the Permissions Choices page
            return

        # Automatically associate all request files with the single ABAC file
        app.request_abac_associations = {request_file: abac_file for request_file in request_files}

    else:
        # Allow users to select multiple request files
        options = QFileDialog.Options()
        request_files, _ = QFileDialog.getOpenFileNames(
            app, "Select Permissions Request Files", "",
            "Text Files (*.txt);;All Files (*)", options=options
        )

        # If no files are selected or the user cancels, return to the Permissions Choices page
        if not request_files:
            app.show_permissions_choice()  # Go back to the Permissions Choices page
            return

        # Create a dictionary to store the associations between request files and ABAC files
        app.request_abac_associations = {}

        # Prompt the user to associate each request file with an ABAC file
        for request_file in request_files:
            abac_files = list(app.abac_data.keys())
            abac_file, ok = QInputDialog.getItem(
                app, "Associate ABAC File",
                f"Which ABAC file should be associated with {os.path.basename(request_file)}?",
                [os.path.basename(f) for f in abac_files], 0, False
            )

            # If the user cancels the association dialog, return to the Permissions Choices page
            if not ok or not abac_file:
                app.show_permissions_choice()  # Go back to the Permissions Choices page
                return

            # Associate the request file with the selected ABAC file
            app.request_abac_associations[request_file] = abac_files[[os.path.basename(f) for f in abac_files].index(abac_file)]

    # Process each request file and store the results
    app.permissions_results = {}
    for request_file, abac_file in app.request_abac_associations.items():
        user_mgr, res_mgr, rule_mgr = app.abac_data[abac_file]
        results = set()  # Use a set to store unique results
        with open(request_file, 'r') as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Validate the line format
                if not re.match(r'^[^,]+,[^,]+,[^,]+$', line):
                    QMessageBox.critical(app, "Error", f"Invalid format in file '{os.path.basename(request_file)}'\nline {line_number}: {line}\nExpected format: user,resource,action")
                    return
                
                decision = process_request(line, user_mgr, res_mgr, rule_mgr)
                results.add(f"{line}: {decision}")  # Add to set to avoid duplicates
        app.permissions_results[request_file] = list(results)  # Convert set to list for display

    # Display the results with file-switch buttons
    display_permissions_results(app)

def display_permissions_results(app):
    """
    Displays the permissions results with file-switch buttons and a container for the results.
    """
    app.clear_results_container()
    container = QWidget()
    app.results_layout.addWidget(container)
    layout = QVBoxLayout(container)

    app.results_display_widget = QWidget()
    app.results_display_layout = QVBoxLayout(app.results_display_widget)
    layout.addWidget(app.results_display_widget)

    first_request_file = list(app.request_abac_associations.keys())[0]
    show_permissions_for_file(app, first_request_file)

    app.scroll_area.show()

def show_permissions_for_file(app, request_file):
    """
    Displays the permissions results for a specific request file with search, filter, sort, stats, and save options.
    """
    while app.results_layout.count():
        item = app.results_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    results = app.permissions_results[request_file]
    app.original_results = results.copy()  # Store the original results

    main_container = QWidget()
    main_container.setStyleSheet("background-color: white;")
    main_layout = QVBoxLayout(main_container)

    # Add evaluation info at the very top
    policy_name = os.path.basename(app.request_abac_associations[request_file])
    evaluation_label = QLabel(
        f"Evaluating request file {os.path.basename(request_file)} "
        f"for policy {policy_name}"
    )
    evaluation_label.setStyleSheet("""
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        color: black;
    """)
    evaluation_label.setTextFormat(Qt.RichText)  # This enables HTML formatting
    evaluation_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(evaluation_label)

    # Add the description label below the evaluation info
    description_label = QLabel(
        "This page allows you to view and manage permissions results. You can switch between request files, "
        "search for specific results, filter by permits or denies, sort by user or resource, and save the results to a file. "
        "Use the dropdowns and search bar to customize your view."
    )
    description_label.setStyleSheet("font-size: 16px; padding: 10px; color: black;")
    description_label.setWordWrap(True)
    description_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    main_layout.addWidget(description_label)

    top_bar_widget = QWidget()
    top_bar_layout = QHBoxLayout(top_bar_widget)

    app.file_dropdown = QComboBox()
    for file in app.request_abac_associations.keys():
        app.file_dropdown.addItem(os.path.basename(file))
    app.file_dropdown.setCurrentText(os.path.basename(request_file))
    app.file_dropdown.currentTextChanged.connect(lambda: app.on_file_dropdown_changed(app.file_dropdown.currentText()))
    top_bar_layout.addWidget(app.file_dropdown)

    app.sort_dropdown = QComboBox()
    app.sort_dropdown.setFixedWidth(150)
    app.sort_dropdown.addItems(["Default Order", "Sort by User", "Sort by Resource"])
    app.sort_dropdown.currentIndexChanged.connect(lambda: app.update_displayed_results(results))
    top_bar_layout.addWidget(app.sort_dropdown)

    app.filter_dropdown = QComboBox()
    app.filter_dropdown.setFixedWidth(150)
    app.filter_dropdown.addItems(["Show All", "Show Only Permits", "Show Only Denies"])
    app.filter_dropdown.currentIndexChanged.connect(lambda: app.update_displayed_results(results))
    top_bar_layout.addWidget(app.filter_dropdown)

    app.search_bar = QLineEdit()
    app.search_bar.setPlaceholderText("Search...")
    app.search_bar.setStyleSheet("color: black;")
    app.search_bar.textChanged.connect(lambda: app.update_displayed_results(results))
    top_bar_layout.addWidget(app.search_bar)

    app.save_button = QPushButton("Save Results")
    app.save_button.setFixedSize(120, 40)
    app.save_button.setStyleSheet("""
        QPushButton {
            background-color: #005F9E;
            color: white;
            border-radius: 5px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #003366;
        }
    """)
    app.save_button.clicked.connect(lambda: app.save_permissions_to_file(request_file))
    top_bar_layout.addWidget(app.save_button)

    main_layout.addWidget(top_bar_widget)

    results_container_widget = QWidget()
    app.results_grid_layout = QGridLayout(results_container_widget)

    for index, result in enumerate(results):
        result_label = QLabel(result)
        result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        result_label.setMaximumHeight(80)
        result_label.setWordWrap(True)
        result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if "Permit" in result:
            result_label.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                color: black;
                padding: 10px;
                margin: 5px;
                border-radius: 10px;
                background-color: rgba(144, 238, 144, 150);
            """)
        elif "Deny" in result:
            result_label.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                color: black;
                margin: 5px;
                border-radius: 10px;
                background-color: rgba(255, 182, 193, 150);
            """)

        row = index // 2
        col = index % 2
        app.results_grid_layout.addWidget(result_label, row, col)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(results_container_widget)
    main_layout.addWidget(scroll_area)

    bottom_bar_widget = QWidget()
    bottom_bar_layout = QHBoxLayout(bottom_bar_widget)

    app.stat_widget = QWidget()
    stat_layout = QHBoxLayout(app.stat_widget)
    stat_layout.setAlignment(Qt.AlignLeft)

    total_permits = sum(1 for result in results if "Permit" in result)
    total_denies = sum(1 for result in results if "Deny" in result)
    app.permits_label = QLabel(f"Permits: {total_permits}")
    app.denies_label = QLabel(f"Denies: {total_denies}")

    app.permits_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
    app.denies_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")

    stat_layout.addWidget(app.permits_label)
    stat_layout.addWidget(app.denies_label)
    app.stat_widget.setLayout(stat_layout)
    bottom_bar_layout.addWidget(app.stat_widget)

    bottom_bar_layout.addStretch()

    back_btn = QPushButton("Back")
    back_btn.setFixedSize(100, 40)
    back_btn.setStyleSheet("""
    QPushButton {
        background-color: #005F9E;
        color: white;
        border-radius: 5px;
        font-size: 16px;
    }
    QPushButton:hover {
        background-color: #003366;
    }
    """)

    back_btn.clicked.connect(app.show_permissions_choice)
    bottom_bar_layout.addWidget(back_btn)

    main_layout.addWidget(bottom_bar_widget)

    app.results_layout.addWidget(main_container)
    app.scroll_area.show()

def on_file_dropdown_changed(app, selected_file_name):
    """
    Handles the file dropdown menu change and switches the displayed file.
    """
    for file_path in app.request_abac_associations.keys():
        if os.path.basename(file_path) == selected_file_name:
            show_permissions_for_file(app, file_path)
            break

def update_displayed_results(app, results):
    """
    Updates the displayed results based on the current search, filter, and sort settings.
    """
    while app.results_grid_layout.count():
        item = app.results_grid_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    search_query = app.search_bar.text().strip().lower()
    filtered_results = [r for r in results if search_query in r.lower()] if search_query else results

    filter_option = app.filter_dropdown.currentText()
    if filter_option == "Show Only Permits":
        filtered_results = [r for r in filtered_results if "Permit" in r]
    elif filter_option == "Show Only Denies":
        filtered_results = [r for r in filtered_results if "Deny" in r]

    sort_option = app.sort_dropdown.currentText()
    if sort_option == "Sort by User":
        filtered_results.sort(key=lambda x: x.split(",")[0].strip())
    elif sort_option == "Sort by Resource":
        filtered_results.sort(key=lambda x: x.split(",")[1].strip())
    elif sort_option == "Default Order":
        # Restore the original order
        filtered_results = [r for r in app.original_results if r in filtered_results]

    for index, result in enumerate(filtered_results):
        result_label = QLabel(result)
        result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        result_label.setMaximumHeight(80)
        result_label.setWordWrap(True)
        result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        if search_query:
            highlighted_text = re.sub(
                f"({re.escape(search_query)})",  
                r'<span style="background-color: yellow; font-weight: bold; color: black;">\1</span>',
                result, flags=re.IGNORECASE
            )
        else:
            highlighted_text = result

        result_label.setText(f'<html><body style="color: black; font-size:20px; font-weight:bold; max-width: 100%; word-wrap: break-word;">{highlighted_text}</body></html>')

        if "Permit" in result:
            result_label.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                margin: 5px;
                border-radius: 10px;
                color: black;
                background-color: rgba(144, 238, 144, 150);
            """)
        elif "Deny" in result:
            result_label.setStyleSheet("""
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                color: black;
                margin: 5px;
                border-radius: 10px;
                background-color: rgba(255, 182, 193, 150);
            """)

        row = index // 2
        col = index % 2
        app.results_grid_layout.addWidget(result_label, row, col)

def save_permissions_to_file(app, request_file):
    """
    Saves the currently displayed results (after filtering, sorting, and searching) to a text file.
    Removes any HTML tags from the text before saving.
    """
    displayed_results = []
    for i in range(app.results_grid_layout.count()):
        widget = app.results_grid_layout.itemAt(i).widget()
        if isinstance(widget, QLabel):
            # Remove HTML tags from the text
            text = re.sub(r'<[^>]+>', '', widget.text())
            displayed_results.append(text)

    if not displayed_results:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(
        app, "Save Results", f"permissions-{os.path.basename(request_file)}", "Text Files (*.txt);;All Files (*)", options=options
    )

    if save_path:
        try:
            with open(save_path, "w") as f:
                for result in displayed_results:
                    f.write(result + "\n")
            QMessageBox.information(app, "Success", f"Results saved to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(app, "Error", f"Failed to save file:\n{str(e)}")

def compute_abac_stats(app):
    """
    Compute general statistics for ABAC policies, ensuring accurate Permit/Deny counts
    based on actual processed requests.
    """
    if not (app.user_mgr and app.res_mgr and app.rule_mgr):
        return {}

    total_users = len(app.user_mgr.users)
    total_resources = len(app.res_mgr.resources)
    total_rules = len(app.rule_mgr.rules)

    total_permits = sum(1 for result in app.original_results if "Permit" in result)
    total_denies = sum(1 for result in app.original_results if "Deny" in result)

    return {
        "Users": total_users,
        "Resources": total_resources,
        "Rules": total_rules,
        "Permits": total_permits,
        "Denies": total_denies
    }

def update_sorted_permissions(app, results):
    """ Sort and update the displayed permissions results into two columns. """
    if not results:
        return

    sorting_option = app.sort_dropdown.currentText()
    filter_option = app.filter_dropdown.currentText()
    search_query = app.search_bar.text().strip().lower()
    
    unique_results = list(set(results))

    if sorting_option == "Default Order":
        sorted_results = sorted(unique_results, key=lambda x: results.index(x))
    elif sorting_option == "Sort by User":
        sorted_results = sorted(unique_results, key=lambda x: x.split(",")[0])
    else:
        sorted_results = sorted(unique_results, key=lambda x: x.split(",")[1])

    if filter_option == "Show Only Permits":
        sorted_results = [r for r in sorted_results if "Permit" in r]
    elif filter_option == "Show Only Denies":
        sorted_results = [r for r in sorted_results if "Deny" in r]

    if search_query:
        sorted_results = [r for r in sorted_results if search_query.lower() in r.lower()]

    for i in reversed(range(app.results_layout.count())):
        app.results_layout.itemAt(i).widget().setParent(None)

    container_widget = QWidget()
    grid_layout = QGridLayout()
    container_widget.setLayout(grid_layout)

    num_results = len(sorted_results)
    mid_index = (num_results + 1) // 2  

    for index, result in enumerate(sorted_results):
        result_label = QLabel()
        result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        result_label.setMaximumHeight(80)
        result_label.setWordWrap(True)
        
        result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if search_query:
            highlighted_text = re.sub(
                f"({re.escape(search_query)})",  
                r'<span style="background-color: yellow; font-weight: bold;">\1</span>',
                result, flags=re.IGNORECASE
            )
        else:
            highlighted_text = result

        result_label.setText(f'<html><body style="font-size:24px; font-weight:bold; max-width: 100%; word-wrap: break-word;">{highlighted_text}</body></html>')

        result_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            margin: 5px;
            border-radius: 10px;
            background-color: white;
            min-width: 300px;
            max-width: 500px;
        """)

        if "Permit" in result:
            result_label.setStyleSheet(result_label.styleSheet() + "background-color: rgba(144, 238, 144, 150);")  
        elif "Deny" in result:
            result_label.setStyleSheet(result_label.styleSheet() + "background-color: rgba(255, 182, 193, 150);")

        col = 0 if index < mid_index else 1
        row = index % mid_index
        grid_layout.addWidget(result_label, row, col)

    app.results_layout.addWidget(container_widget)
    app.results_area.setLayout(app.results_layout)