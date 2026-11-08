from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QGridLayout, QMessageBox, QSizePolicy, QCompleter, QComboBox, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
import os
import re
import time

def show_manual_check(app):
    """
    Displays the manual check interface for testing permissions.
    Restores the previously selected file if available.
    """
    if not app.abac_data:
        QMessageBox.warning(app, "Warning", "Please upload an ABAC file first.")
        return
    
    app.clear_results_container()
    container = QWidget()
    container.setStyleSheet("background-color: white;")
    layout = QVBoxLayout(container)

    title_label = QLabel("Manual Check")
    title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
    layout.addWidget(title_label, alignment=Qt.AlignTop | Qt.AlignCenter)
    
    layout.addStretch()

    # Add a label above the input fields
    input_label = QLabel(
        "To check permissions, fill in one or more of the fields below:\n"
        "1. Enter a user to check permissions for a specific user.\n"
        "2. Enter a resource to check permissions for a specific resource.\n"
        "3. Enter an action to check permissions for a specific action.\n"\
        "4. Enter two fields to check for permissions for the specific fields.\n"
        "5. Enter three fields to check if a request is permitted or denied. \n"
        "You can fill in one, two, or all three fields to refine your search."
    )
    input_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: black;")
    input_label.setWordWrap(True)  # Ensure the text wraps if it's too long
    layout.addWidget(input_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

    layout.addStretch()

    # Top bar layout for dropdown menu
    top_bar_layout = QHBoxLayout()
    dropdown_label = QLabel("Policy:")
    dropdown_label.setStyleSheet("font-size: 30px; color: black; border: none;")
    dropdown_label.setAlignment(Qt.AlignRight)
    app.file_dropdown = QComboBox()
    app.file_dropdown.setFixedSize(200, 40)
    app.file_dropdown.setStyleSheet("font-size: 16px; color: black; border: 2px solid black;")
    if len(app.abac_data) > 0:
        for abac_path in app.abac_data.keys():
            app.file_dropdown.addItem(os.path.basename(abac_path), abac_path)
    app.file_dropdown.currentTextChanged.connect(
        lambda: on_manual_check_dropdown_changed(app)
    )
    top_bar_layout.addWidget(dropdown_label, alignment=Qt.AlignRight)
    top_bar_layout.addWidget(app.file_dropdown, alignment=Qt.AlignLeft)
    top_bar_layout.setAlignment(Qt.AlignCenter)
    layout.addLayout(top_bar_layout)

    # layout.addStretch()

    # Input fields layout (always shown if there is at least one file)
    app.input_container = QWidget()
    input_layout = QHBoxLayout(app.input_container)  # Restore side-by-side layout
    app.user_input = QLineEdit()
    app.user_input.setPlaceholderText("Enter user")
    app.user_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }                                       
        """)
    app.resource_input = QLineEdit()
    app.resource_input.setPlaceholderText("Enter resource")
    app.resource_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }                                       
        """)
    app.action_input = QLineEdit()
    app.action_input.setPlaceholderText("Enter action")
    app.action_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }                                       
        """)

    input_layout.addWidget(app.user_input)
    input_layout.addWidget(app.resource_input)
    input_layout.addWidget(app.action_input)

    # Search button (always shown if there is at least one file)
    app.search_btn = QPushButton("Search")
    app.search_btn.setFixedSize(100, 40)
    app.search_btn.setStyleSheet("""
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
    app.search_btn.clicked.connect(lambda: manual_check_search(app))
    input_layout.addWidget(app.search_btn)

    # Add the input container to the layout
    layout.addWidget(app.input_container)
    layout.addStretch()

    # Bottom bar layout for the Back button
    bottom_bar_layout = QHBoxLayout()    
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
    
    layout.addLayout(bottom_bar_layout)

    # Add container to the results layout
    app.results_layout.addWidget(container)
    app.scroll_area.show()

    app.file_dropdown.setCurrentIndex(app.uploaded_files.index(app.current_abac_path))
    populate_manual_check_fields(app, app.current_abac_path)

def manual_check_search(self):
    """
    Performs a manual check for permissions based on the user, resource, or action inputs.
    Implements pagination to display results in smaller chunks.
    """
    # Ensure a file is selected
    if not hasattr(self, 'current_manual_abac') or not self.current_manual_abac:
        QMessageBox.warning(self, "Warning", "Please select a file first.")
        return

    # Retrieve search terms from the input fields
    user_query = self.user_input.text().strip()
    resource_query = self.resource_input.text().strip()
    action_query = self.action_input.text().strip()

    # Count the number of fields filled
    self.filled_fields = sum([
        1 if user_query else 0,
        1 if resource_query else 0,
        1 if action_query else 0
    ])

    if self.filled_fields == 0:
        QMessageBox.warning(self, "Warning", "Please fill in at least one field (user, resource, or action).")
        return

    # Get the ABAC data for the selected file
    abac_path = self.current_manual_abac
    user_mgr, res_mgr, rule_mgr = self.abac_data[abac_path]

    # Collect all valid users, resources, and actions
    valid_users = set(user_mgr.users.keys())
    valid_resources = set(res_mgr.resources.keys())
    valid_actions = set()
    for rule in rule_mgr.rules:
        valid_actions.update(rule.acts)

    # Check if the user exists
    if user_query and user_query not in valid_users:
        QMessageBox.warning(self, "Warning", f"User '{user_query}' does not exist.")
        return

    # Check if the resource exists
    if resource_query and resource_query not in valid_resources:
        QMessageBox.warning(self, "Warning", f"Resource '{resource_query}' does not exist.")
        return

    # Check if the action exists
    if action_query:
        actions = [action.strip() for action in action_query.split(",")]
        for action in actions:
            if action not in valid_actions:
                QMessageBox.warning(self, "Warning", f"Action '{action}' does not exist.")
                return
    else:
        actions = list(valid_actions)  # If no action query, use all valid actions

    # Filter users and resources based on the search queries
    users = [user for user in user_mgr.users.keys() if not user_query or user == user_query]
    resources = [resource for resource in res_mgr.resources.keys() if not resource_query or resource == resource_query]

    # Evaluate permissions for the filtered combinations
    manual_results = []
    self.permit_count = 0
    for user_name in users:
        user_obj = user_mgr.users[user_name]
        for resource_name in resources:
            resource_obj = res_mgr.resources[resource_name]
            for action in actions:
                permitted = False
                for rule in rule_mgr.rules:
                    if rule.evaluate(user_obj, resource_obj, action):
                        permitted = True
                        break
                # Only include results with 'Permit' if 1 or 2 fields are used for the search
                if self.filled_fields in [1, 2]:
                    if permitted:
                        manual_results.append(f"User: {user_name}, Resource: {resource_name}, Action: {action} -> Permit")
                        self.permit_count += 1  # Increment permit count
                else:
                        manual_results.append(f"User: {user_name}, Resource: {resource_name}, Action: {action} -> {'Permit' if permitted else 'Deny'}")
          
    # Store results and initialize pagination
    self.manual_results = manual_results
    self.manual_results_per_page = 100
    self.manual_current_page = 1
    self.manual_total_pages = (len(manual_results) + self.manual_results_per_page - 1) // self.manual_results_per_page

    # Render the first page
    manual_render_results_page(self)

def manual_render_results_page(self):
    """
    Renders the current page of results for the manual check feature.
    Hides pagination controls if there's only one page of results.
    """
    # Clear previous results
    self.clear_results_container()

    # Log the start time for rendering
    rendering_start_time = time.time()
    print(f"Rendering started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rendering_start_time))}")

    # Get the results for the current page
    start_index = (self.manual_current_page - 1) * self.manual_results_per_page
    end_index = min(start_index + self.manual_results_per_page, len(self.manual_results))
    page_results = self.manual_results[start_index:end_index]

    # Create the main container
    main_container = QWidget()
    main_container.setStyleSheet("background-color: white;")
    main_layout = QVBoxLayout(main_container)

    # Results container
    results_container = QWidget()
    results_layout = QGridLayout(results_container)

    # Display the results in a grid
    for index, result in enumerate(page_results):
        result_label = QLabel(result)
        result_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        result_label.setMaximumHeight(80)
        result_label.setWordWrap(True)
        result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Apply styling based on Permit/Deny
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
                margin: 5px;
                border-radius: 10px;
                color: black;
                background-color: rgba(255, 182, 193, 150);
            """)

        row = index // 2  # Two columns per row
        col = index % 2
        results_layout.addWidget(result_label, row, col)

    # Add results to a scroll area
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(results_container)
    main_layout.addWidget(scroll_area)

    # Only show pagination controls if there's more than one page
    if self.manual_total_pages > 1:
        # Pagination controls
        pagination_bar = QWidget()
        pagination_layout = QHBoxLayout(pagination_bar)
        pagination_layout.setContentsMargins(0, 10, 0, 10)

        # Add Back Button
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
        back_btn.clicked.connect(self.show_manual_check)
        pagination_layout.addWidget(back_btn)
        
        # Add Permit Count Label (only if not all three fields are filled)
        if self.filled_fields != 3:
            permit_count_label = QLabel(f"Permits: {self.permit_count}")
            permit_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
            pagination_layout.addWidget(permit_count_label)
        
        pagination_layout.addStretch()

        # Add First Page Button
        first_button = QPushButton("First")
        first_button.setEnabled(self.manual_current_page > 1)
        first_button.clicked.connect(lambda: self.set_manual_page(1))
        first_button.setFixedSize(80, 30)
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
        pagination_layout.addWidget(first_button)

        # Calculate page range to display (max 10 pages)
        max_pages_to_show = 10
        half_range = max_pages_to_show // 2
        start_page = max(1, self.manual_current_page - half_range)
        end_page = min(self.manual_total_pages, start_page + max_pages_to_show - 1)
        
        # Adjust if we're at the end
        if end_page - start_page + 1 < max_pages_to_show:
            start_page = max(1, end_page - max_pages_to_show + 1)

        # Add page number buttons
        for page in range(start_page, end_page + 1):
            page_button = QPushButton(str(page))
            page_button.setFixedSize(30, 30)
            if page == self.manual_current_page:
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
            page_button.clicked.connect(lambda _, p=page: self.set_manual_page(p))
            pagination_layout.addWidget(page_button)

        # Add page input controls if there are more pages than we're showing
        if end_page < self.manual_total_pages:
            # Add page input label
            page_input_label = QLabel("Pg #")
            page_input_label.setStyleSheet("font-size: 12px; color: black;")
            pagination_layout.addWidget(page_input_label)
            
            # Add page number input
            self.manual_page_input = QLineEdit()
            self.manual_page_input.setFixedSize(50, 30)
            self.manual_page_input.setStyleSheet("""
                QLineEdit {
                    font-size: 12px;
                    border: 1px solid #005F9E;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            self.manual_page_input.setValidator(QIntValidator(1, self.manual_total_pages))
            self.manual_page_input.returnPressed.connect(
                lambda: self.on_manual_page_input()
            )
            pagination_layout.addWidget(self.manual_page_input)
            
            # Add Go button
            go_button = QPushButton("Go")
            go_button.setFixedSize(50, 30)
            go_button.clicked.connect(lambda: self.on_manual_page_input())
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
            pagination_layout.addWidget(go_button)

        # Add Last Page Button
        last_button = QPushButton("Last")
        last_button.setEnabled(self.manual_current_page < self.manual_total_pages)
        last_button.clicked.connect(lambda: self.set_manual_page(self.manual_total_pages))
        last_button.setFixedSize(80, 30)
        last_button.setStyleSheet("""
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
        pagination_layout.addWidget(last_button)

        pagination_layout.addStretch()

        # Add Save Page Button
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
        save_page_btn.clicked.connect(lambda: self.save_manual_check_page_results())
        pagination_layout.addWidget(save_page_btn)

        # Add Save Button (on the right)
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
        save_btn.clicked.connect(lambda: self.save_manual_check_results())
        
        pagination_layout.addWidget(save_btn)
        
        main_layout.addWidget(pagination_bar)
    else:
        # Only show back and save buttons when there's only one page
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0, 10, 0, 10)
        
        # Add Back Button
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
        back_btn.clicked.connect(self.show_manual_check)
        bottom_layout.addWidget(back_btn)
        
        # Add Permit Count Label (only if not all three fields are filled)
        if self.filled_fields != 3:
            permit_count_label = QLabel(f"Permits: {self.permit_count}")
            permit_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
            bottom_layout.addWidget(permit_count_label)
        
        bottom_layout.addStretch()
        
        # Add Save Button
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
        save_btn.clicked.connect(lambda: self.save_manual_check_results())
        bottom_layout.addWidget(save_btn)
        
        main_layout.addWidget(bottom_bar)

    # Add the main container to the results layout
    self.results_layout.addWidget(main_container)

    # Show the scrollable area
    self.scroll_area.show()

    # Log the end time for rendering
    rendering_end_time = time.time()
    print(f"Rendering finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rendering_end_time))}")
    print(f"Rendering duration: {rendering_end_time - rendering_start_time:.2f} seconds")

def set_manual_page(self, page):
    """
    Sets the current page to the specified page number and refreshes the view.
    """
    self.manual_current_page = page
    manual_render_results_page(self)

def on_manual_page_input(self):
    """Handle manual page number input"""
    try:
        page = int(self.manual_page_input.text())
        if 1 <= page <= self.manual_total_pages:
            self.set_manual_page(page)
    except ValueError:
        QMessageBox.warning(self, "Invalid Input", "Please enter a valid page number")


def populate_manual_check_fields(app, abac_path):
    """
    Populates the completer fields for user, resource, and action inputs based on the selected ABAC file.
    Shows suggestions immediately when a user clicks on a search field.
    Resets the action field suggestions after each entry.
    """
    if not hasattr(app, 'user_input') or not app.user_input:
        return  # Ensure input fields exist

    # Get the ABAC data for the selected file
    user_mgr, res_mgr, rule_mgr = app.abac_data[abac_path]

    # Assume that the keys in user_mgr.users and res_mgr.resources are the names
    user_list = list(user_mgr.users.keys())
    resource_list = list(res_mgr.resources.keys())

    # Collect a list of actions
    action_set = set()
    for rule in rule_mgr.rules:
        action_set.update(rule.acts)
    action_list = list(action_set)

    # Create completers for each field
    user_completer = QCompleter(user_list)
    resource_completer = QCompleter(resource_list)
    action_completer = QCompleter(action_list)

    # Set the completers on the input fields
    app.user_input.setCompleter(user_completer)
    app.resource_input.setCompleter(resource_completer)
    app.action_input.setCompleter(action_completer)

    # Store the currently selected ABAC file for later use
    app.current_manual_abac = abac_path

    # Connect the clicked signal of the input fields to show suggestions
    app.user_input.mousePressEvent = lambda event: show_suggestions(app.user_input)
    app.resource_input.mousePressEvent = lambda event: show_suggestions(app.resource_input)

    # For the action field: reset suggestions after each input
    app.action_input.mousePressEvent = lambda event: reset_and_show_suggestions(app.action_input, action_list)


def show_suggestions(input_field):
    """
    Shows suggestions for the given input field when it is clicked.
    """
    if input_field.completer():
        input_field.completer().setCompletionMode(QCompleter.PopupCompletion)
        input_field.completer().complete()  # Show the popup


def reset_and_show_suggestions(input_field, original_list):
    """
    Resets the suggestions for the action field and shows them immediately on click.
    """
    if input_field.completer():
        # Reset the completer to the original list
        new_completer = QCompleter(original_list)
        input_field.setCompleter(new_completer)

        # Force the suggestions dropdown to show
        new_completer.setCompletionMode(QCompleter.PopupCompletion)
        new_completer.complete()

def on_manual_check_dropdown_changed(app):
    """
    Handles the file dropdown menu change in the manual check interface.
    Stores the selected file path and populates the input fields.
    """
    selected_abac_path = app.file_dropdown.currentData()
    if selected_abac_path:
        # Store the selected file path
        app.current_manual_abac = selected_abac_path
        # Populate the input fields for the selected file
        populate_manual_check_fields(app, selected_abac_path)

def strip_html_tags(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def save_manual_check_results(app):
    """
    Saves the manual check results to a .txt file.
    Adds the ABAC file name as the first line in the file.
    """
    # Ensure there are results to save
    if not hasattr(app, 'results_layout') or app.results_layout.count() == 0:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Get the main container widget from the results layout
    main_container = app.results_layout.itemAt(0).widget()
    if not main_container:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Get the scroll area from the main container
    scroll_area = main_container.findChild(QScrollArea)
    if not scroll_area:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Get the results container from the scroll area
    results_container = scroll_area.widget()
    if not results_container:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Collect the results from the results container
    results = []
    def collect_labels(layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel):
                    results.append(strip_html_tags(widget.text()))
                elif widget.layout():
                    collect_labels(widget.layout())
            elif item.layout():
                collect_labels(item.layout())

    collect_labels(results_container.layout())

    # Get the ABAC file name from the current_manual_abac path
    if hasattr(app, 'current_manual_abac') and app.current_manual_abac:
        abac_name = os.path.basename(app.current_manual_abac)
    else:
        abac_name = "Unknown ABAC File"

    # Prepend the ABAC file name to the results
    results_with_name = f"ABAC File: {abac_name}\n\n" + "\n".join(results)

    # Save the results to a .txt file
    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(app, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
    if save_path:
        try:
            with open(save_path, 'w') as file:
                file.write(results_with_name)  # Write the modified text
            QMessageBox.information(app, "Success", "Results saved successfully.")
        except Exception as e:
            QMessageBox.warning(app, "Error", f"Failed to save results: {str(e)}")

def save_manual_check_page_results(app):
    """
    Saves only the current page of manual check results to a .txt file.
    Includes the ABAC file name and page number in the filename.
    """
    # Ensure there are results to save
    if not hasattr(app, 'results_layout') or app.results_layout.count() == 0:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Get the main container widget from the results layout
    main_container = app.results_layout.itemAt(0).widget()
    if not main_container:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Get the scroll area from the main container
    scroll_area = main_container.findChild(QScrollArea)
    if not scroll_area:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Get the results container from the scroll area
    results_container = scroll_area.widget()
    if not results_container:
        QMessageBox.warning(app, "Warning", "No results to save.")
        return

    # Collect the results from the results container
    results = []
    def collect_labels(layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel):
                    results.append(strip_html_tags(widget.text()))
                elif widget.layout():
                    collect_labels(widget.layout())
            elif item.layout():
                collect_labels(item.layout())

    collect_labels(results_container.layout())

    # Get the ABAC file name from the current_manual_abac path
    if hasattr(app, 'current_manual_abac') and app.current_manual_abac:
        abac_name = os.path.basename(app.current_manual_abac)
    else:
        abac_name = "Unknown_ABAC_File"

    # Create default filename with ABAC name and page number
    default_filename = f"{abac_name}_page_{app.manual_current_page}.txt"

    # Save the results to a .txt file
    options = QFileDialog.Options()
    save_path, _ = QFileDialog.getSaveFileName(
        app, 
        "Save Current Page Results", 
        default_filename,  # Default filename
        "Text Files (*.txt);;All Files (*)", 
        options=options
    )
    
    if save_path:
        try:
            with open(save_path, 'w') as file:
                # Write header with ABAC file and page info
                file.write(f"ABAC File: {abac_name}\n")
                file.write(f"Page: {app.manual_current_page} of {app.manual_total_pages}\n\n")
                file.write("\n".join(results))
            QMessageBox.information(app, "Success", "Current page results saved successfully.")
        except Exception as e:
            QMessageBox.warning(app, "Error", f"Failed to save results: {str(e)}")