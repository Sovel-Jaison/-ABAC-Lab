from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QComboBox, QLabel
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def precompute_heatmaps(app):
    """
    Precomputes heatmap data for all uploaded ABAC files and stores it in the app's heatmap_cache.
    """
    for file_path in app.abac_data.keys():
        if file_path not in app.heatmap_cache:
            app.heatmap_cache[file_path] = generate_heatmap_data(app, file_path)

def generate_heatmap_data(app, file_path):
    """
    Generates and returns the heatmap data for a given ABAC file.
    """
    user_mgr, res_mgr, rule_mgr = app.abac_data[file_path]
    heatmap = {}
    all_actions = set()

    # Collect all actions from all rules
    for rule in rule_mgr.rules:
        all_actions.update(rule.acts)

    # Build the heatmap data
    for rule_idx, rule in enumerate(rule_mgr.rules):
        heatmap[rule_idx] = {}
        rule_attributes = rule.get_attributes()
        for attr in rule_attributes["user"]:
            heatmap[rule_idx][f"user.{attr}"] = 0
        for attr in rule_attributes["resource"]:
            heatmap[rule_idx][f"res.{attr}"] = 0
        for uid, user in user_mgr.users.items():
            for rid, resource in res_mgr.resources.items():
                for action in all_actions:
                    if rule.evaluate(user, resource, action):
                        for attr in rule_attributes["user"]:
                            if attr in user.attributes:
                                heatmap[rule_idx][f"user.{attr}"] += 1
                        for attr in rule_attributes["resource"]:
                            if attr in resource.attributes:
                                heatmap[rule_idx][f"res.{attr}"] += 1

    # Prepare sorted attributes and data matrix
    rules = list(heatmap.keys())
    attributes = list({attr for attrs in heatmap.values() for attr in attrs})
    user_attrs = sorted([attr for attr in attributes if attr.startswith("user.")])
    res_attrs = sorted([attr for attr in attributes if attr.startswith("res.")])
    sorted_attributes = user_attrs + res_attrs

    data = np.zeros((len(rules), len(sorted_attributes)), dtype=int)
    for rule_idx, attrs in heatmap.items():
        for attr, count in attrs.items():
            rule_pos = rules.index(rule_idx)
            attr_pos = sorted_attributes.index(attr)
            data[rule_pos, attr_pos] = count

    return {
        "data": data,
        "rules": rules,
        "attributes": sorted_attributes,
        "file_name": os.path.basename(file_path)
    }

def show_heatmap(app):
    """
    Displays the heatmap interface for visualizing policy coverage.
    """
    if not app.abac_data:
        QMessageBox.warning(app, "Warning", "Please upload an ABAC file first.")
        return

    # Hide other elements
    app.stats_widget.hide()
    app.perm_widget.hide()
    app.bar_graph_widget.hide()
    app.heat_map_widget.hide()
    app.rule_widget.hide()
    app.page2_label.hide()
    app.rule_perm_lbl.hide()
    app.rule_perm_btn.hide()
    app.heat_map_lbl.hide()
    app.heatmap_btn_page2.hide()
    app.perm_btn.hide()
    app.permissions_lbl.hide()
    app.bar_graph_btn.hide()
    app.bar_grph_lbl.hide()
    app.stats_container.hide()

    # Clear previous results
    app.clear_results_container()

    # Show the results area
    app.results_area_container.show()

    # Create a container for the heatmap
    container = QWidget()
    container.setStyleSheet("background-color: white;")
    container_layout = QVBoxLayout(container)

    # Create a top layout for the Back button and dropdown menu
    top_layout = QHBoxLayout()

    # Add the Back button to the top-left corner
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

    back_btn.clicked.connect(app.show_page2)
    top_layout.addWidget(back_btn, alignment=Qt.AlignLeft)

    # Add a dropdown menu for file selection, centered
    if len(app.abac_data) > 1:
        dropdown_layout = QHBoxLayout()

        policy_label = QLabel("Policy:")
        policy_label.setStyleSheet("font-size: 25px; color: black;")
        dropdown_layout.addWidget(policy_label)

        file_dropdown = QComboBox()
        file_dropdown.setFixedWidth(200)  # Set a fixed width for the dropdown
        file_dropdown.setStyleSheet("font-size: 16px; color: black; border: 2px solid black")
        for file_path in app.abac_data.keys():
            file_dropdown.addItem(os.path.basename(file_path))
        file_dropdown.currentIndexChanged.connect(lambda index: display_heatmap(app, list(app.abac_data.keys())[index]))
        dropdown_layout.addWidget(file_dropdown)

        # Add the dropdown to the top layout with centering
        top_layout.addStretch(5)
        top_layout.addLayout(dropdown_layout)
        top_layout.addStretch(6)

    # Add the top layout to the container layout
    container_layout.addLayout(top_layout)

    # Create a widget for the heatmap display
    app.heatmap_display = QWidget()
    app.heatmap_display_layout = QVBoxLayout(app.heatmap_display)
    container_layout.addWidget(app.heatmap_display)

    # Set the layout for the container
    container.setLayout(container_layout)

    # Add the container to the results layout
    app.results_layout.addWidget(container)

    # Show the scrollable area
    app.scroll_area.show()

    # Display the heatmap for the first file
    if app.current_abac_path and len(app.abac_data) > 1:
        file_dropdown.setCurrentIndex(app.uploaded_files.index(app.current_abac_path))
        display_heatmap(app, app.current_abac_path)
    else:
        first_file = list(app.abac_data.keys())[0]
        display_heatmap(app, first_file)

def display_heatmap(app, file_path):
    """
    Displays the heatmap for the given ABAC file using precomputed data.
    """
    # Clear previous heatmap display
    while app.heatmap_display_layout.count():
        item = app.heatmap_display_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    # Get precomputed heatmap data
    cached_data = app.heatmap_cache.get(file_path)
    if not cached_data:
        QMessageBox.warning(app, "Error", "Heatmap data not found in cache.")
        return

    data = cached_data["data"]
    rules = cached_data["rules"]
    attributes = cached_data["attributes"]
    file_name = cached_data["file_name"]

    # Create the heatmap figure
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.subplots_adjust(left=0.2, right=0.95, bottom=0.2, top=0.9)

    sns.heatmap(data, ax=ax, cmap="Blues", annot=True, fmt="d",
                xticklabels=attributes,
                yticklabels=[f"Rule {r + 1}" for r in rules],
                linewidths=0.5, linecolor="black")

    ax.set_xlabel("Attributes", fontsize=12)
    ax.set_ylabel("Rules", fontsize=12)
    ax.set_title(f"Policy Coverage Analysis Heatmap for {file_name}",
                 pad=10, fontsize=14)

    plt.xticks(rotation=50, ha='right', rotation_mode='anchor', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout(pad=2.0)

    # Add the heatmap to the display
    canvas = FigureCanvas(fig)
    nav_toolbar = NavigationToolbar(canvas, app)
    nav_toolbar.setStyleSheet("background-color: gray; color: white;")
    app.heatmap_display_layout.addWidget(nav_toolbar)
    app.heatmap_display_layout.addWidget(canvas)

    # Function to handle resize events
    def on_resize(event):
        fig.tight_layout(pad=2.0)
        canvas.draw()

    fig.canvas.mpl_connect('resize_event', on_resize)