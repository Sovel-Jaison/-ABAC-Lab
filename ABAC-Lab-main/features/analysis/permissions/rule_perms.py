from PyQt5.QtWidgets import QFileDialog, QComboBox, QMessageBox, QVBoxLayout, QLabel, QFrame, QInputDialog, QWidget, QPushButton, QScrollArea, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
import os
import re
from core.rule import RuleManager

# Initialize cache in the app object
def initialize_permstats_cache(app):
    """Initialize the permissions statistics cache"""
    app.permstats_cache = {}

# Precompute all permstats data when files are loaded
def precompute_permstats(app):
    """Precompute permissions statistics for all ABAC files"""
    if not hasattr(app, 'permstats_cache'):
        initialize_permstats_cache(app)
    
    for file_path in app.abac_data.keys():
        if file_path not in app.permstats_cache:
            app.permstats_cache[file_path] = generate_permstats_data(app, file_path)

def generate_permstats_data(app, file_path):
    """
    Generate and return the permissions statistics data without creating UI elements
    Returns a list of dictionaries containing rule data and permissions
    """
    user_mgr, res_mgr, rule_mgr = app.abac_data[file_path]
    cached_data = []
    
    # Read the ABAC file to extract rules exactly as they appear
    with open(file_path, 'r') as file:
        lines = file.readlines()

    rule_idx = 0  # Track the rule index
    for line in lines:
        line = line.strip()
        if line.startswith('rule('):
            rule = rule_mgr.rules[rule_idx]
            rule_idx += 1
            
            # Calculate permissions for this rule
            permissions_count = 0
            permissions_list = []
            
            for user_name, user in user_mgr.users.items():
                for resource_name, resource in res_mgr.resources.items():
                    for action in rule.acts:
                        if rule.evaluate(user, resource, action):
                            permissions_count += 1
                            permissions_list.append(
                                f"User: {user_name}, Resource: {resource_name}, Action: {action}"
                            )
            
            # Store the data for this rule
            cached_data.append({
                'rule_text': line,
                'permissions_count': permissions_count,
                'permissions_list': permissions_list
            })
    
    return cached_data

def show_permstats(app):
    """Display the permissions statistics interface using cached data"""
    if not app.abac_data:
        QMessageBox.warning(app, "Warning", "Please upload an ABAC file first.")
        return

    # First check if we have cached data, if not precompute it
    if not hasattr(app, 'permstats_cache') or not app.permstats_cache:
        precompute_permstats(app)
    
    # If still no cached data (empty files case), show error
    if not app.permstats_cache:
        QMessageBox.warning(app, "Warning", "No valid permissions data available.")
        return

    # Initialize pagination if not exists
    if not hasattr(app, 'permstats_pagination'):
        app.permstats_pagination = {}

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
    app.results_area_container.show()
    
    # Create container
    container = QWidget()
    container.setStyleSheet("background-color: white;")
    layout = QVBoxLayout(container)

    # Rule Permissions label
    rule_permissions_label = QLabel("Rule Permissions")
    rule_permissions_label.setStyleSheet(
        "font-size: 30px; font-weight: bold; color: white; "
        "background-color: #003366; padding: 5px; border-radius: 5px;"
    )
    layout.addWidget(rule_permissions_label, alignment=Qt.AlignTop | Qt.AlignCenter)

    # Top bar with dropdown
    top_bar = QWidget()
    top_bar_layout = QHBoxLayout(top_bar)
    top_bar_layout.addStretch()
    
    policy_label = QLabel("Policy:")
    policy_label.setStyleSheet("font-size: 30px; color: black;")
    top_bar_layout.addWidget(policy_label)

    app.permstats_file_dropdown = QComboBox()
    app.permstats_file_dropdown.setFixedSize(200, 40)
    app.permstats_file_dropdown.setStyleSheet(
        "font-size: 16px; color: black; border: 2px solid black;"
    )
    
    # Populate dropdown with cached files
    for file_path in app.permstats_cache.keys():
        app.permstats_file_dropdown.addItem(os.path.basename(file_path))
        
    app.permstats_file_dropdown.currentTextChanged.connect(
        lambda text: on_permstats_file_dropdown_changed(app, text)
    )
    top_bar_layout.addWidget(app.permstats_file_dropdown)
    top_bar_layout.addStretch()
    layout.addWidget(top_bar)

    # Scroll area for rules
    app.permstats_scroll_area = QScrollArea()
    app.permstats_scroll_area.setWidgetResizable(True)
    app.permstats_scroll_area_widget = QWidget()
    app.permstats_scroll_area_layout = QVBoxLayout(app.permstats_scroll_area_widget)
    app.permstats_scroll_area.setWidget(app.permstats_scroll_area_widget)
    layout.addWidget(app.permstats_scroll_area)

    # Bottom bar with buttons and pagination
    bottom_bar = QWidget()
    bottom_bar_layout = QHBoxLayout(bottom_bar)
    bottom_bar_layout.setContentsMargins(0, 10, 0, 10)
    
    # Left side - Back button
    app.back_btn = QPushButton("Back")
    app.back_btn.setFixedSize(100, 40)
    app.back_btn.setStyleSheet("""
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
    app.back_btn.clicked.connect(app.show_rule_choices)
    bottom_bar_layout.addWidget(app.back_btn)
    
    # Middle - Pagination controls (will be updated in display_permstats)
    app.permstats_pagination_widget = QWidget()
    app.permstats_pagination_layout = QHBoxLayout(app.permstats_pagination_widget)
    app.permstats_pagination_layout.setContentsMargins(0, 0, 0, 0)
    bottom_bar_layout.addWidget(app.permstats_pagination_widget, 1)  # Add stretch factor
    
    # Right side - Save button
    app.save_btn_permstats = QPushButton("Save All")
    app.save_btn_permstats.setFixedSize(100, 40)
    app.save_btn_permstats.setStyleSheet("""
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
    app.save_btn_permstats.clicked.connect(lambda: save_permstats_results(app))
    bottom_bar_layout.addWidget(app.save_btn_permstats)
    
    layout.addWidget(bottom_bar)

    app.results_layout.addWidget(container)
    app.scroll_area.show()

    # Display first file's data from cache
    current_file = list(app.permstats_cache.keys())[0]
    if app.current_abac_path and app.current_abac_path in app.permstats_cache:
        current_file = app.current_abac_path
        
    display_permstats(app, current_file)

def display_permstats(app, file_path):
    """Display permissions statistics from cached data with enhanced pagination"""
    # Clear previous display
    while app.permstats_scroll_area_layout.count():
        item = app.permstats_scroll_area_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
    
    # Clear previous pagination controls
    while app.permstats_pagination_layout.count():
        item = app.permstats_pagination_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()
    
    cached_data = app.permstats_cache[file_path]

    # Update current ABAC path and dropdown selection
    app.current_abac_path = file_path
    if hasattr(app, 'permstats_file_dropdown'):
        index = app.permstats_file_dropdown.findText(os.path.basename(file_path))
        if index >= 0:
            app.permstats_file_dropdown.setCurrentIndex(index)
    
    # Initialize pagination state if not exists
    if not hasattr(app, 'permstats_pagination'):
        app.permstats_pagination = {}
    if file_path not in app.permstats_pagination:
        app.permstats_pagination[file_path] = {
            'current_page': 1,
            'per_page': 100,
            'rule_positions': [],
            'total_pages': 0  # Initialize total_pages
        }
    
    pagination = app.permstats_pagination[file_path]
    current_page = pagination['current_page']
    per_page = pagination['per_page']
    
    # Calculate total permissions across all rules
    total_permissions = sum(len(rule['permissions_list']) for rule in cached_data)
    total_pages = max(1, (total_permissions - 1) // per_page + 1)
    pagination['total_pages'] = total_pages  # Store total_pages
    
    # Only show pagination if there are multiple pages
    if total_pages > 1:
        # Create a container for pagination controls to ensure proper centering
        pagination_container = QWidget()
        pagination_container_layout = QHBoxLayout(pagination_container)
        pagination_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add stretch to center the controls
        pagination_container_layout.addStretch()

        # Add First Page Button
        first_button = QPushButton("First")
        first_button.setFixedSize(80, 30)
        first_button.setEnabled(current_page > 1)
        first_button.clicked.connect(lambda: set_permstats_page(app, file_path, 1))
        first_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background-color: #005F9E;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        pagination_container_layout.addWidget(first_button)

        # Add some spacing
        pagination_container_layout.addSpacing(10)

        # Calculate page range to display (max 5 pages centered around current)
        max_pages_to_show = 5
        start_page = max(1, current_page - max_pages_to_show // 2)
        end_page = min(total_pages, start_page + max_pages_to_show - 1)
        
        # Adjust if we're at the start or end
        if end_page - start_page + 1 < max_pages_to_show:
            if current_page < total_pages // 2:
                end_page = min(total_pages, start_page + max_pages_to_show - 1)
            else:
                start_page = max(1, end_page - max_pages_to_show + 1)

        # Add page number buttons
        for page in range(start_page, end_page + 1):
            page_button = QPushButton(str(page))
            page_button.setFixedSize(30, 30)
            if page == current_page:
                page_button.setStyleSheet("""
                    QPushButton {
                        font-size: 12px;
                        font-weight: bold;
                        background-color: #003366;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                    }
                """)
            else:
                page_button.setStyleSheet("""
                    QPushButton {
                        font-size: 12px;
                        background-color: #005F9E;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #003366;
                    }
                """)
            page_button.clicked.connect(lambda _, p=page: set_permstats_page(app, file_path, p))
            pagination_container_layout.addWidget(page_button)

        # Add page number input
        page_input_label = QLabel("Pg #")
        page_input_label.setStyleSheet("font-size: 12px; color: black;")
        pagination_container_layout.addWidget(page_input_label)
        
        app.permstats_page_input = QLineEdit()
        app.permstats_page_input.setFixedSize(50, 30)
        app.permstats_page_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                border: 1px solid #005F9E;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        app.permstats_page_input.setValidator(QIntValidator(1, total_pages))
        app.permstats_page_input.returnPressed.connect(
            lambda: on_permstats_page_input(app, file_path)
        )
        pagination_container_layout.addWidget(app.permstats_page_input)
        
        # Add Go button
        go_button = QPushButton("Go")
        go_button.setFixedSize(50, 30)
        go_button.clicked.connect(lambda: on_permstats_page_input(app, file_path))
        go_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background-color: #005F9E;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)
        pagination_container_layout.addWidget(go_button)

        # Add some spacing
        pagination_container_layout.addSpacing(10)

        # Add Last Page Button
        last_button = QPushButton("Last")
        last_button.setFixedSize(80, 30)
        last_button.setEnabled(current_page < total_pages)
        last_button.clicked.connect(lambda: set_permstats_page(app, file_path, total_pages))
        last_button.setStyleSheet(first_button.styleSheet())
        pagination_container_layout.addWidget(last_button)

        # Add stretch to center the controls
        pagination_container_layout.addStretch()

        # Add Save Page button
        save_page_button = QPushButton("Save Page")
        save_page_button.setFixedSize(100, 40)
        save_page_button.clicked.connect(lambda: save_permstats_page_results(app, file_path))
        save_page_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #005F9E;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)
        pagination_container_layout.addWidget(save_page_button)

        # Add the pagination container to the main layout
        app.permstats_pagination_layout.addWidget(pagination_container)

    # Calculate how many permissions we can show on this page
    remaining_permissions = per_page
    page_rules = []
    
    # Determine which rules and how many of their permissions to show on this page
    for rule_idx, rule_data in enumerate(cached_data):
        if remaining_permissions <= 0:
            break
            
        rule_permissions = rule_data['permissions_list']
        start_idx = 0
        
        # If we've shown part of this rule before, find where we left off
        if rule_idx < len(pagination['rule_positions']):
            start_idx = pagination['rule_positions'][rule_idx]
        
        # Calculate how many permissions we can show from this rule
        show_count = min(len(rule_permissions) - start_idx, remaining_permissions)
        
        if show_count > 0:
            page_rules.append({
                'rule_idx': rule_idx,
                'rule_data': rule_data,
                'start_idx': start_idx,
                'show_count': show_count,
                'is_continuation': start_idx > 0,
                'has_more': (start_idx + show_count) < len(rule_permissions)
            })
            remaining_permissions -= show_count
    
    # Create UI elements for the current page
    for rule_info in page_rules:
        rule_idx = rule_info['rule_idx']
        rule_data = rule_info['rule_data']
        start_idx = rule_info['start_idx']
        show_count = rule_info['show_count']
        
        rule_container = QWidget()
        rule_layout = QVBoxLayout(rule_container)

        # Rule text
        rule_label = QLabel(f"Rule {rule_idx+1}: {rule_data['rule_text']}")
        rule_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        rule_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        rule_layout.addWidget(rule_label)

        # Permissions count (show total count, not just this page)
        count_label = QLabel(f"Permissions Granted: {rule_data['permissions_count']}")
        count_label.setStyleSheet("font-size: 16px; color: black;")
        count_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        rule_layout.addWidget(count_label)

        # Permissions list
        if rule_data['permissions_list']:
            permissions_label = QLabel("Permissions:")
            permissions_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
            permissions_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            rule_layout.addWidget(permissions_label)
            
            # Show continuation notice if this is a continuation
            if rule_info['is_continuation']:
                cont_label = QLabel("(continued from previous page)")
                cont_label.setStyleSheet("font-size: 14px; font-style: italic; color: #666;")
                rule_layout.addWidget(cont_label)
            
            # Show the permissions for this page
            for permission in rule_data['permissions_list'][start_idx:start_idx+show_count]:
                permission_label = QLabel(permission)
                permission_label.setStyleSheet("font-size: 14px; color: black;")
                permission_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                rule_layout.addWidget(permission_label)
            
            # Show continuation notice if there are more permissions
            if rule_info['has_more']:
                more_label = QLabel(f"(showing {show_count} of {len(rule_data['permissions_list'])} permissions)")
                more_label.setStyleSheet("font-size: 14px; font-style: italic; color: #666;")
                rule_layout.addWidget(more_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        rule_layout.addWidget(separator)

        app.permstats_scroll_area_layout.addWidget(rule_container)

def on_permstats_page_input(app, file_path):
    """Handle page number input"""
    if not hasattr(app, 'permstats_page_input') or not app.permstats_page_input:
        return
    
    try:
        page_text = app.permstats_page_input.text().strip()
        if not page_text:
            return
            
        page = int(page_text)
        if file_path not in app.permstats_pagination:
            return
            
        pagination = app.permstats_pagination[file_path]
        total_pages = pagination.get('total_pages', 1)
        
        if 1 <= page <= total_pages:
            set_permstats_page(app, file_path, page)
        else:
            QMessageBox.warning(app, "Invalid Page", 
                              f"Please enter a page number between 1 and {total_pages}")
    except ValueError:
        QMessageBox.warning(app, "Invalid Input", "Please enter a valid page number")


def set_permstats_page(app, file_path, page):
    """Set the current page for permstats display with proper position tracking"""
    if not hasattr(app, 'permstats_pagination'):
        app.permstats_pagination = {}
    if file_path not in app.permstats_pagination:
        app.permstats_pagination[file_path] = {
            'current_page': 1,
            'per_page': 100,
            'rule_positions': [],
            'total_pages': 1,
            'last_direction': None  # Track navigation direction
        }
    
    pagination = app.permstats_pagination[file_path]
    prev_page = pagination['current_page']
    pagination['current_page'] = page
    
    # Determine navigation direction
    direction = 'forward' if page > prev_page else 'backward'
    pagination['last_direction'] = direction
    
    # Calculate rule positions based on direction
    if direction == 'forward':
        # Moving forward - continue from last positions
        remaining_permissions = pagination['per_page']
        new_rule_positions = []
        
        for rule_idx, rule_data in enumerate(app.permstats_cache[file_path]):
            if rule_idx < len(pagination['rule_positions']):
                start_idx = pagination['rule_positions'][rule_idx]
            else:
                start_idx = 0
                
            rule_permissions = rule_data['permissions_list']
            show_count = min(len(rule_permissions) - start_idx, remaining_permissions)
            
            if show_count > 0:
                new_rule_positions.append(start_idx + show_count)
                remaining_permissions -= show_count
            else:
                new_rule_positions.append(start_idx)
                
            if remaining_permissions <= 0:
                # Fill remaining positions
                while len(new_rule_positions) < len(app.permstats_cache[file_path]):
                    if len(pagination['rule_positions']) > len(new_rule_positions):
                        new_rule_positions.append(pagination['rule_positions'][len(new_rule_positions)])
                    else:
                        new_rule_positions.append(0)
                break
    else:
        # Moving backward - need to recalculate positions from start
        target_permissions = (page - 1) * pagination['per_page']
        new_rule_positions = [0] * len(app.permstats_cache[file_path])
        remaining_permissions = target_permissions
        
        for rule_idx, rule_data in enumerate(app.permstats_cache[file_path]):
            if remaining_permissions <= 0:
                break
                
            rule_permissions = rule_data['permissions_list']
            take = min(len(rule_permissions), remaining_permissions)
            new_rule_positions[rule_idx] = take
            remaining_permissions -= take
    
    pagination['rule_positions'] = new_rule_positions
    
    # Redisplay the stats
    display_permstats(app, file_path)
    
    # Scroll to top
    app.permstats_scroll_area.verticalScrollBar().setValue(0)

def on_permstats_file_dropdown_changed(app, selected_file_name):
    """Handle file dropdown changes using cached data"""
    for file_path in app.abac_data.keys():
        if os.path.basename(file_path) == selected_file_name:
            app.current_abac_path = file_path
            display_permstats(app, file_path)
            break

def show_rulevu(app):
    """
    Allows the user to upload multiple text files containing rules and associate them with ABAC files.
    Displays the rules, number of permissions granted, and the permissions in a layout similar to the rule permissions page.
    Immediately shows the first file after file associations are done.
    """
    if not app.abac_data:
        QMessageBox.warning(app, "Warning", "Please upload an ABAC file first.")
        return

    # Initialize pagination state
    if not hasattr(app, 'rulevu_pagination'):
        app.rulevu_pagination = {}

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
    app.clear_results_container()
    app.results_area_container.show()

    # Prompt the user to upload rule files
    options = QFileDialog.Options()
    rule_files, _ = QFileDialog.getOpenFileNames(
        app, "Select Rule Files", "", "Text Files (*.txt);;All Files (*)", options=options
    )

    # If no files are selected or the user cancels, return to the Rule Choices page
    if not rule_files:
        app.show_rule_choices()  # Go back to the Rule Choices page
        return

    rule_pattern = re.compile(r'^rule\([^;]*;[^;]*;[^;]*;[^;]*\)$')
    for rule_file in rule_files:
        with open(rule_file, 'r') as file:
            lines = file.readlines()
        for line_number, line in enumerate(lines, start=1):
            line = line.strip()
            if line.startswith("rule("):
                if not rule_pattern.match(line):
                    QMessageBox.critical(app, "Error", f"Invalid format in file {os.path.basename(rule_file)} at line {line_number}\n{line}\nExpected: rule(*;*;*;*)")
                    app.show_rule_choices()
                    return
            elif line:  # Check for lines that are not empty and do not start with "rule("
                QMessageBox.critical(app, "Error", f"Invalid format in file {os.path.basename(rule_file)} at line {line_number}\n{line}\nExpected: rule(*;*;*;*)")
                app.show_rule_choices()
                return

    # Create a dictionary to store the associations between rule files and ABAC files
    rule_abac_associations = {}

    # Prompt the user to associate each rule file with an ABAC file
    for rule_file in rule_files:
        abac_files = list(app.abac_data.keys())
        abac_file, ok = QInputDialog.getItem(
            app, "Associate ABAC File",
            f"Which ABAC file should be associated with {os.path.basename(rule_file)}?",
            [os.path.basename(f) for f in abac_files] + ["No Association"], 0, False
        )

        # If the user cancels the association dialog or chooses "No Association", skip this file
        if not ok or abac_file == "No Association":
            continue

        # Associate the rule file with the selected ABAC file
        rule_abac_associations[rule_file] = abac_files[[os.path.basename(f) for f in abac_files].index(abac_file)]

    # If no rule files are associated with any ABAC file, return to the Rule Choices page
    if not rule_abac_associations:
        QMessageBox.information(app, "Information", "No rule files were associated with an ABAC file.")
        app.show_rule_choices()
        return

    # Create a container for the results
    container = QWidget()
    container.setStyleSheet("background-color: white;")
    layout = QVBoxLayout(container)

    # Informational label above the dropdown
    info_label = QLabel()
    info_label.setStyleSheet("""
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
    """)
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setTextFormat(Qt.RichText)

    # Set initial text using the first associated rule file and its ABAC file
    first_rule_file = list(rule_abac_associations.keys())[0]
    first_abac_file = rule_abac_associations[first_rule_file]
    info_label.setText(
        f"Evaluating rules for {os.path.basename(first_rule_file)} "
        f"with policy {os.path.basename(first_abac_file)}"
    )
    layout.addWidget(info_label)

    # Create a dropdown to switch between rule files
    rule_file_dropdown = QComboBox()
    rule_file_dropdown.setFixedWidth(200)
    rule_file_dropdown.setStyleSheet("font-size: 16px; color: black; border: 2px solid black;")
    for rule_file in rule_abac_associations.keys():
        rule_file_dropdown.addItem(os.path.basename(rule_file))
    rule_file_dropdown.currentTextChanged.connect(
        lambda selected: on_rule_file_dropdown_changed(app, rule_file_dropdown, rule_abac_associations, selected, info_label)
    )
    layout.addWidget(rule_file_dropdown, alignment=Qt.AlignCenter)

    # Create a scroll area for the rules and permissions
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area_widget = QWidget()
    scroll_area_layout = QVBoxLayout(scroll_area_widget)
    scroll_area.setWidget(scroll_area_widget)
    app.rulevu_scroll_area_widget = scroll_area_widget
    layout.addWidget(scroll_area)

    # Create a bottom bar for navigation controls
    bottom_bar = QWidget()
    bottom_bar_layout = QHBoxLayout(bottom_bar)
    bottom_bar_layout.setContentsMargins(0, 10, 0, 10)

    # Back button on left
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
    back_btn.clicked.connect(app.show_rule_choices)
    bottom_bar_layout.addWidget(back_btn)

    # Pagination controls in center (will be populated when needed)
    app.rulevu_pagination_widget = QWidget()
    app.rulevu_pagination_layout = QHBoxLayout(app.rulevu_pagination_widget)
    app.rulevu_pagination_layout.setContentsMargins(0, 0, 0, 0)
    bottom_bar_layout.addWidget(app.rulevu_pagination_widget, 1)  # Add stretch factor

    # Add Save Page button before the main Save button
    save_page_btn = QPushButton("Save Page")
    save_page_btn.setFixedSize(100, 40)
    save_page_btn.setStyleSheet("""
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
    save_page_btn.clicked.connect(lambda: save_rulevu_page_results(app, rule_abac_associations))
    bottom_bar_layout.addWidget(save_page_btn)

    # Save button on right
    save_btn = QPushButton("Save All")
    save_btn.setFixedSize(100, 40)
    save_btn.setStyleSheet("""
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
    save_btn.clicked.connect(lambda: save_rulevu_results(app, rule_abac_associations))
    bottom_bar_layout.addWidget(save_btn)

    layout.addWidget(bottom_bar)
    app.results_layout.addWidget(container)
    app.scroll_area.show()

    # Immediately display the first file's rules and permissions
    on_rule_file_dropdown_changed(app, rule_file_dropdown, rule_abac_associations, os.path.basename(first_rule_file), info_label)

def on_rule_file_dropdown_changed(app, rule_file_dropdown, rule_abac_associations, selected_file_name=None, info_label=None):
    """Handle file dropdown changes with pagination"""
    if not selected_file_name:
        selected_file_name = rule_file_dropdown.currentText()

    selected_rule_file = next((f for f in rule_abac_associations.keys() 
                             if os.path.basename(f) == selected_file_name), None)
    if not selected_rule_file:
        return

    # Update info label if provided
    if info_label:
        abac_file = rule_abac_associations[selected_rule_file]
        info_label.setText(f"Evaluating rules for {os.path.basename(selected_rule_file)} for policy {os.path.basename(abac_file)}")

    # Clear previous results
    scroll_area_layout = app.rulevu_scroll_area_widget.layout()
    while scroll_area_layout.count():
        item = scroll_area_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

    # Clear previous pagination controls
    while app.rulevu_pagination_layout.count():
        item = app.rulevu_pagination_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

    # Read the selected rule file
    with open(selected_rule_file, 'r') as file:
        lines = file.readlines()
    
    # Get ABAC data
    abac_file = rule_abac_associations[selected_rule_file]
    user_mgr, res_mgr, _ = app.abac_data[abac_file]
    
    # Initialize pagination for this file if not exists
    if selected_rule_file not in app.rulevu_pagination:
        app.rulevu_pagination[selected_rule_file] = {
            'current_page': 1,
            'per_page': 100,
            'rule_positions': [],
            'total_pages': 1
        }
    
    pagination = app.rulevu_pagination[selected_rule_file]
    
    # Process rules with pagination
    remaining_permissions = pagination['per_page']
    current_rule_idx = 0
    total_permissions = 0
    rules_with_permissions = []

    # First pass to calculate total permissions
    for line in lines:
        line = line.strip()
        if line.startswith("rule("):
            rule_manager = RuleManager()
            rule_manager.parse_rule(line)
            rule = rule_manager.rules[0]
            
            permissions = []
            for user_name, user in user_mgr.users.items():
                for resource_name, resource in res_mgr.resources.items():
                    for action in rule.acts:
                        if rule.evaluate(user, resource, action):
                            permissions.append(
                                f"User: {user_name}, Resource: {resource_name}, Action: {action}"
                            )
            
            total_permissions += len(permissions)
            rules_with_permissions.append((line, permissions))

    # Calculate total pages
    total_pages = max(1, (total_permissions - 1) // pagination['per_page'] + 1)
    
    # Only show pagination if there are multiple pages
    if total_pages > 1:
        page_label = QLabel(f"Page {pagination['current_page'] + 1} of {total_pages}")
        page_label.setStyleSheet("font-size: 14px; color: black;")
        
        prev_btn = QPushButton("Previous")
        prev_btn.setFixedSize(100, 30)
        prev_btn.setEnabled(pagination['current_page'] > 0)
        prev_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background-color: #005F9E;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        prev_btn.clicked.connect(lambda: change_rulevu_page(app, selected_rule_file, -1, rule_abac_associations, info_label))
        
        next_btn = QPushButton("Next")
        next_btn.setFixedSize(100, 30)
        next_btn.setEnabled(pagination['current_page'] + 1 < total_pages)
        next_btn.setStyleSheet(prev_btn.styleSheet())
        next_btn.clicked.connect(lambda: change_rulevu_page(app, selected_rule_file, 1, rule_abac_associations, info_label))
        
        app.rulevu_pagination_layout.addStretch()
        app.rulevu_pagination_layout.addWidget(prev_btn)
        app.rulevu_pagination_layout.addWidget(page_label)
        app.rulevu_pagination_layout.addWidget(next_btn)
        app.rulevu_pagination_layout.addStretch()

    # Second pass to display the current page's content
    remaining_permissions = pagination['per_page']
    current_rule_idx = 0
    
    for line, permissions in rules_with_permissions:
        if remaining_permissions <= 0:
            break
            
        # Determine what to show on this page
        start_idx = 0
        if current_rule_idx < len(pagination['rule_positions']):
            start_idx = pagination['rule_positions'][current_rule_idx]
        
        show_count = min(len(permissions) - start_idx, remaining_permissions)
        
        if show_count > 0:
            # Create rule container
            rule_container = QWidget()
            rule_layout = QVBoxLayout(rule_container)

            # Rule header
            rule_label = QLabel(f"<b>Rule {current_rule_idx+1}: {line}</b>")
            rule_label.setStyleSheet("font-size: 16px; color: black;")
            rule_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            rule_layout.addWidget(rule_label)

            # Total permissions count
            count_label = QLabel(f"Total Permissions Granted: {len(permissions)}")
            count_label.setStyleSheet("font-size: 14px; color: black;")
            count_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            rule_layout.addWidget(count_label)

            # Permissions list
            if permissions:
                permissions_label = QLabel("Permissions:")
                permissions_label.setStyleSheet("font-size: 14px; font-weight: bold; color: black;")
                permissions_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                rule_layout.addWidget(permissions_label)
                
                # Continuation notice if needed
                if start_idx > 0:
                    cont_label = QLabel("(continued from previous page)")
                    cont_label.setStyleSheet("font-size: 14px; font-style: italic; color: #666;")
                    rule_layout.addWidget(cont_label)
                
                # Show permissions for this page
                for permission in permissions[start_idx:start_idx+show_count]:
                    permission_label = QLabel(permission)
                    permission_label.setStyleSheet("font-size: 12px; color: black;")
                    permission_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    rule_layout.addWidget(permission_label)
                
                # More available notice if needed
                if (start_idx + show_count) < len(permissions):
                    more_label = QLabel(f"(showing {show_count} of {len(permissions)} permissions)")
                    more_label.setStyleSheet("font-size: 14px; font-style: italic; color: #666;")
                    rule_layout.addWidget(more_label)
            
            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            rule_layout.addWidget(separator)

            scroll_area_layout.addWidget(rule_container)
            
            remaining_permissions -= show_count
            current_rule_idx += 1

    scroll_area_layout.addStretch()

def change_rulevu_page(app, rule_file, direction, rule_abac_associations, info_label):
    """Change page for rulevu display with proper position tracking"""
    if rule_file not in app.rulevu_pagination:
        app.rulevu_pagination[rule_file] = {
            'current_page': 1,
            'per_page': 100,
            'rule_positions': [],
            'total_pages': 1
        }
    
    pagination = app.rulevu_pagination[rule_file]
    pagination['current_page'] += direction
    
    # Update rule positions for next/previous page
    if direction > 0:
        # For next page, track where we left off in each rule
        remaining = pagination['per_page']
        new_positions = []
        
        with open(rule_file, 'r') as f:
            rules = [l.strip() for l in f if l.startswith("rule(")]
        
        abac_file = rule_abac_associations[rule_file]
        user_mgr, res_mgr, _ = app.abac_data[abac_file]
        
        for i, rule_text in enumerate(rules):
            rule_manager = RuleManager()
            rule_manager.parse_rule(rule_text)
            rule = rule_manager.rules[0]
            
            permissions = []
            for user_name, user in user_mgr.users.items():
                for resource_name, resource in res_mgr.resources.items():
                    for action in rule.acts:
                        if rule.evaluate(user, resource, action):
                            permissions.append(
                                f"User: {user_name}, Resource: {resource_name}, Action: {action}"
                            )
            
            if i < len(pagination['rule_positions']):
                start = pagination['rule_positions'][i]
            else:
                start = 0
                
            take = min(len(permissions) - start, remaining)
            new_positions.append(start + take)
            remaining -= take
            
            if remaining <= 0:
                # Fill remaining positions
                new_positions.extend([0] * (len(rules) - len(new_positions)))
                break
        
        pagination['rule_positions'] = new_positions
    else:
        # For previous page, reconstruct positions
        target = pagination['current_page'] * pagination['per_page']
        new_positions = []
        remaining = target
        
        with open(rule_file, 'r') as f:
            rules = [l.strip() for l in f if l.startswith("rule(")][::-1]  # Process in reverse
        
        abac_file = rule_abac_associations[rule_file]
        user_mgr, res_mgr, _ = app.abac_data[abac_file]
        
        for rule_text in rules:
            rule_manager = RuleManager()
            rule_manager.parse_rule(rule_text)
            rule = rule_manager.rules[0]
            
            permissions = []
            for user_name, user in user_mgr.users.items():
                for resource_name, resource in res_mgr.resources.items():
                    for action in rule.acts:
                        if rule.evaluate(user, resource, action):
                            permissions.append(
                                f"User: {user_name}, Resource: {resource_name}, Action: {action}"
                            )
            
            take = min(len(permissions), remaining)
            new_positions.insert(0, take)  # Add to beginning since we're processing in reverse
            remaining -= take
            
            if remaining <= 0:
                break
        
        # Fill any remaining positions with 0
        new_positions = new_positions + [0] * (len(rules) - len(new_positions))
        pagination['rule_positions'] = new_positions
    
    # Refresh the display
    on_rule_file_dropdown_changed(app, None, rule_abac_associations, os.path.basename(rule_file), info_label)
    
    # Scroll to top
    app.rulevu_scroll_area.verticalScrollBar().setValue(0)

def get_permissions_for_rule(rule_text, user_mgr, res_mgr):
    """Helper function to count permissions for a rule"""
    rule_manager = RuleManager()
    rule_manager.parse_rule(rule_text)
    rule = rule_manager.rules[0]
    
    permissions = []
    for user_name, user in user_mgr.users.items():
        for resource_name, resource in res_mgr.resources.items():
            for action in rule.acts:
                if rule.evaluate(user, resource, action):
                    permissions.append(
                        f"User: {user_name}, Resource: {resource_name}, Action: {action}"
                    )
    return permissions

def strip_html_tags(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def save_permstats_results(app):
    """
    Saves the permissions statistics results to a .txt file.
    """
    # Get the current file path from the dropdown
    current_file_name = app.permstats_file_dropdown.currentText()
    current_file_path = None
    for file_path in app.abac_data.keys():
        if os.path.basename(file_path) == current_file_name:
            current_file_path = file_path
            break

    if not current_file_path:
        QMessageBox.warning(app, "Warning", "No file selected.")
        return

    # Collect the results from the scroll area
    results = []
    for i in range(app.permstats_scroll_area_layout.count()):
        item = app.permstats_scroll_area_layout.itemAt(i)
        widget = item.widget()
        if widget:
            for child in widget.children():
                if isinstance(child, QLabel):
                    results.append(strip_html_tags(child.text()))  # Strip HTML tags

    # Add the filename to the first line of the results
    results.insert(0, f"Results for file: {current_file_name}\n")

    # Save the results to a .txt file
    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(app, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
    if save_path:
        with open(save_path, 'w') as file:
            file.write("\n".join(results))
        QMessageBox.information(app, "Success", "Results saved successfully.")

def save_rulevu_results(app, rule_abac_associations):
    """
    Saves the rulevu results to a .txt file.
    """
    # Get the current rule file from the dropdown
    # Updated the index to 1 because index 0 now holds the info label
    current_rule_file_name = app.results_layout.itemAt(0).widget().layout().itemAt(1).widget().currentText()
    current_rule_file = None
    for rule_file in rule_abac_associations.keys():
        if os.path.basename(rule_file) == current_rule_file_name:
            current_rule_file = rule_file
            break

    if not current_rule_file:
        QMessageBox.warning(app, "Warning", "No rule file selected.")
        return

    # Collect the results from the scroll area
    scroll_area_widget = app.results_layout.itemAt(0).widget().layout().itemAt(2).widget().widget()
    scroll_area_layout = scroll_area_widget.layout()
    results = []
    for i in range(scroll_area_layout.count()):
        item = scroll_area_layout.itemAt(i)
        widget = item.widget()
        if widget:
            for child in widget.children():
                if isinstance(child, QLabel):
                    results.append(strip_html_tags(child.text()))  # Strip HTML tags

    # Add the filename to the first line of the results
    results.insert(0, f"Results for file: {current_rule_file_name}\n")

    # Save the results to a .txt file
    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(app, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
    if save_path:
        with open(save_path, 'w') as file:
            file.write("\n".join(results))
        QMessageBox.information(app, "Success", "Results saved successfully.")

def save_permstats_page_results(app, file_path):
    """Save only the current page of results"""
    # Get the current page data
    pagination = app.permstats_pagination[file_path]
    current_page = pagination['current_page']
    
    # Collect all the results from the current page display
    results = []
    for i in range(app.permstats_scroll_area_layout.count()):
        item = app.permstats_scroll_area_layout.itemAt(i)
        widget = item.widget()
        if widget:
            for child in widget.children():
                if isinstance(child, QLabel):
                    results.append(strip_html_tags(child.text()))
    
    # Add header with file and page info
    results.insert(0, f"Results for {os.path.basename(file_path)} - Page {current_page}")
    results.insert(1, "="*50)
    
    # Save to file
    options = QFileDialog.Options()
    default_filename = f"{os.path.basename(file_path)}_page_{current_page}.txt"
    save_path, _ = QFileDialog.getSaveFileName(
        app, "Save Current Page", default_filename, 
        "Text Files (*.txt);;All Files (*)", options=options
    )
    
    if save_path:
        try:
            with open(save_path, 'w') as file:
                file.write("\n".join(results))
            QMessageBox.information(app, "Success", "Current page saved successfully.")
        except Exception as e:
            QMessageBox.warning(app, "Error", f"Failed to save page: {str(e)}")

def save_rulevu_page_results(app, rule_abac_associations):
    """
    Save only the current page of RuleVu results to a file
    """
    # Get the current rule file from the dropdown
    current_rule_file_name = app.results_layout.itemAt(0).widget().layout().itemAt(1).widget().currentText()
    current_rule_file = next((f for f in rule_abac_associations.keys() 
                            if os.path.basename(f) == current_rule_file_name), None)
    
    if not current_rule_file:
        QMessageBox.warning(app, "Warning", "No rule file selected.")
        return

    # Get the current page number
    pagination = app.rulevu_pagination.get(current_rule_file, {'current_page': 1})
    current_page = pagination['current_page']

    # Collect the results from the current page display
    scroll_area_widget = app.results_layout.itemAt(0).widget().layout().itemAt(2).widget().widget()
    scroll_area_layout = scroll_area_widget.layout()
    
    results = []
    for i in range(scroll_area_layout.count()):
        item = scroll_area_layout.itemAt(i)
        widget = item.widget()
        if widget:
            for child in widget.children():
                if isinstance(child, QLabel):
                    results.append(strip_html_tags(child.text()))

    # Add header information
    abac_file = rule_abac_associations[current_rule_file]
    results.insert(0, f"Rule File: {os.path.basename(current_rule_file)}")
    results.insert(1, f"ABAC Policy: {os.path.basename(abac_file)}")
    results.insert(2, f"Page: {current_page}")
    results.insert(3, "="*50)

    # Save to file
    options = QFileDialog.Options()
    default_filename = f"{os.path.basename(current_rule_file)}_page_{current_page}.txt"
    save_path, _ = QFileDialog.getSaveFileName(
        app, "Save Current Page", default_filename, 
        "Text Files (*.txt);;All Files (*)", options=options
    )
    
    if save_path:
        try:
            with open(save_path, 'w') as file:
                file.write("\n".join(results))
            QMessageBox.information(app, "Success", "Current page saved successfully.")
        except Exception as e:
            QMessageBox.warning(app, "Error", f"Failed to save page: {str(e)}")