import re
import csv
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QFileDialog, QMessageBox
)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def extract_attributes(lines):
    """
    Given an abac file, identify all attributes for the first line of a csv

    Args:
        lines (list): list of every resource and user line in abac policy file

    Returns:
        tuple: two lists, one containing the user attributes and the other resource attributes,
               and two sets containing multi-value user attributes and multi-value resource attributes
    """
    user_pattern = re.compile(r'userAttrib\((\w+), (.*?)\)')
    resource_pattern = re.compile(r'resourceAttrib\((\w+), (.*?)\)')

    user_attributes = set()
    resource_attributes = set()
    multi_value_user_attributes = set()
    multi_value_resource_attributes = set()

    for line in lines:
        user_match = user_pattern.match(line)
        resource_match = resource_pattern.match(line)

        if user_match:
            attributes = user_match.group(2).split(', ')
            for attrib in attributes:
                key, value = attrib.split('=')
                user_attributes.add(key)
                if '{' in value:
                    multi_value_user_attributes.add(key)
        elif resource_match:
            attributes = resource_match.group(2).split(', ')
            for attrib in attributes:
                key, value = attrib.split('=')
                resource_attributes.add(key)
                if '{' in value:
                    multi_value_resource_attributes.add(key)

    user_attributes = sorted(user_attributes)
    resource_attributes = sorted(resource_attributes)

    return user_attributes, resource_attributes, multi_value_user_attributes, multi_value_resource_attributes

def abac_to_csv(lines, user_attributes, resource_attributes,
                multi_value_user_attributes, multi_value_resource_attributes,
                combined_csv_path, rule_ouput_path):
    user_pattern = re.compile(r'userAttrib\((\w+), (.*?)\)')
    resource_pattern = re.compile(r'resourceAttrib\((\w+), (.*?)\)')
    rule_pattern = re.compile(r'rule\((.*?)\)')

    rules = []
    
    with open(combined_csv_path, 'w', newline='', encoding="UTF-8") as combined_csv:
        writer = csv.writer(combined_csv)

        # Write first line schema headers with prefixes and markers for multi-value attributes
        user_headers = [f"U-{attr}*" if attr in multi_value_user_attributes else f"U-{attr}" for attr in user_attributes]
        resource_headers = [f"R-{attr}*" if attr in multi_value_resource_attributes else f"R-{attr}" for attr in resource_attributes]
        writer.writerow(['id'] + user_headers + resource_headers)

        for line in lines:
            user_match = user_pattern.match(line)
            resource_match = resource_pattern.match(line)
            rule_match = rule_pattern.match(line)

            if user_match:
                user = user_match.group(1)
                attributes = {}
                for attrib in user_match.group(2).split(', '):
                    value = attrib.split('=')[1]
                    if value == "{}":
                        attributes[f"U-{attrib.split('=')[0]}"] = "|"
                    elif "{" in value and " " in value:
                        attributes[f"U-{attrib.split('=')[0]}"] = value.strip("{}").replace(' ', '|')
                        continue
                    elif "{" in value:
                        attributes[f"U-{attrib.split('=')[0]}"] = value.strip("{}")
                    else:
                        attributes[f"U-{attrib.split('=')[0]}"] = value
                row = [user] + [attributes.get(f"U-{attr}", '') for attr in user_attributes] + ['' for _ in resource_attributes]
                writer.writerow(row)
            elif resource_match:
                resource = resource_match.group(1)
                attributes = {f"R-{attrib.split('=')[0]}": attrib.split('=')[1].strip('{}').replace(' ', '|') for attrib in resource_match.group(2).split(', ')}
                row = [resource] + ['' for _ in user_attributes] + [attributes.get(f"R-{attr}", '') for attr in resource_attributes]
                writer.writerow(row)
            elif rule_match:
                rules.append(line)
    
    with open(rule_ouput_path, 'w', encoding="UTF-8") as rules_txt:
        for rule in rules:
            rules_txt.write(rule + '\n')


def csv_to_abac(combined_csv_path, abac_output_path):
    with open(combined_csv_path, 'r', encoding="UTF-8") as combined_csv, open(abac_output_path, 'w', encoding="UTF-8") as abac_output:
        reader = csv.DictReader(combined_csv)

        for row in reader:
            entry_id = row.pop('id')
            user_attributes = {key[2:]: value for key, value in row.items() if key.startswith('U-') and value}
            resource_attributes = {key[2:]: value for key, value in row.items() if key.startswith('R-') and value}

            if user_attributes:
                attributes = []
                for key, value in user_attributes.items():
                    clean_key = key[:-1] if key.endswith('*') else key  # Remove the '*' marker
                    if value == "|":
                        # Handle empty multi-value attribute
                        attributes.append(f"{clean_key}={{}}")
                    elif '|' in value:
                        # Handle multi-value attribute with multiple values
                        attributes.append(f"{clean_key}={{{value.replace('|', ' ')}}}")
                    else:
                        # Handle single-value attribute
                        if key.endswith('*'):
                            attributes.append(f"{clean_key}={{{value}}}")
                        else:
                            attributes.append(f"{clean_key}={value}")
                attributes_str = ', '.join(attributes)
                abac_output.write(f"userAttrib({entry_id}, {attributes_str})\n")
            elif resource_attributes:
                attributes = []
                for key, value in resource_attributes.items():
                    clean_key = key[:-1] if key.endswith('*') else key  # Remove the '*' marker
                    if value == "|":
                        # Handle empty multi-value attribute
                        attributes.append(f"{clean_key}={{}}")
                    elif '|' in value:
                        # Handle multi-value attribute with multiple values
                        attributes.append(f"{clean_key}={{{value.replace('|', ' ')}}}")
                    else:
                        # Handle single-value attribute
                        if key.endswith('*'):
                            attributes.append(f"{clean_key}={{{value}}}")
                        else:
                            attributes.append(f"{clean_key}={value}")
                attributes_str = ', '.join(attributes)
                abac_output.write(f"resourceAttrib({entry_id}, {attributes_str})\n")

class SingleFileUpload(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setFixedSize(500, 200)
        self.setStyleSheet(
            """
            background-color: transparent;
            color: black;
            border: 5px dashed black;
            border-radius: 5px;
            padding: 20px;
            font-size: 16px;
            text-align: center;
            """)
        layout = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: black;")
        image_upload = resource_path("res/upload_b.png")
        self.label.setText(
            f"""
            <div style="text-align: center;">
                <img src='{image_upload}' width='50' height='50'><br>
                <span style="font-size: 24px;">Upload File</span><br>
                <span style="font-size: 16px;">Click to browse or drag & drop a file here</span>
            </div>
            """)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.abac'):
                upload_abac_file(self.main_window, file_path)
            else:
                QMessageBox.warning(self.main_window, "Invalid File", "Please upload a .abac file.")


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Select ABAC Policy File",
                "",
                "Policy Files (*.abac);;All Files (*)",
                options=options,
            )
            if file_name:
                if file_name.endswith('.abac'):
                    upload_abac_file(self.main_window, file_name)
                else:
                    QMessageBox.warning(self.main_window, "Invalid File", "Please upload a .abac file.")
  
def convert_uploaded_file(app):
    selected_file = app.page3_current_uploaded_files.currentText()
    if not selected_file:
        QMessageBox.warning(app, "Warning", "No file selected for conversion.")
        return

    file_path = None
    for path in app.uploaded_files:
        if os.path.basename(path) == selected_file:
            file_path = path
            break

    if not file_path:
        QMessageBox.warning(app, "Warning", "Selected file not found.")
        return

    try:
        with open(file_path, "r", encoding="UTF-8") as abac_file:
            lines = [
                line.strip()
                for line in abac_file
                if line.strip() and not line.startswith("#")
            ]
            (
                user_attributes,
                resource_attributes,
                multi_value_user_attributes,
                multi_value_resource_attributes,
            ) = extract_attributes(lines)

            # Prompt the user to choose the output file location and name for CSV
            save_file_name, _ = QFileDialog.getSaveFileName(
                app,
                "Save CSV File",
                "",
                "CSV Files (*.csv);;All Files (*)",
                options=QFileDialog.Options(),
            )
            if save_file_name:
                # Automatically generate the rules file name by appending "_rules" to the CSV file name
                rules_file_name = os.path.splitext(save_file_name)[0] + "_rules.txt"
                abac_to_csv(lines, user_attributes, resource_attributes, multi_value_user_attributes, multi_value_resource_attributes, save_file_name, rules_file_name)
                QMessageBox.information(app, "Success", f"ABAC file converted to CSV successfully.\nSaved as {save_file_name}\nRules saved as {rules_file_name}")
            else:
                QMessageBox.warning(
                    app,
                    "Warning",
                    "No output file selected for CSV. Conversion cancelled.",
                )
    except Exception as e:
        QMessageBox.critical(app, "Error", f"Failed to convert ABAC file:\n{str(e)}")

def upload_abac_file(app, file_name):
    if file_name:
        try:
            with open(file_name, "r", encoding="UTF-8") as abac_file:
                lines = [
                    line.strip()
                    for line in abac_file
                    if line.strip() and not line.startswith("#")
                ]
                (
                    user_attributes,
                    resource_attributes,
                    multi_value_user_attributes,
                    multi_value_resource_attributes,
                ) = extract_attributes(lines)
                
                # Prompt the user to choose the output file location and name for CSV
                save_file_name, _ = QFileDialog.getSaveFileName(
                    app,
                    "Save CSV File",
                    "",
                    "CSV Files (*.csv);;All Files (*)",
                    options=QFileDialog.Options(),
                )
                if save_file_name:
                    # Automatically generate the rules file name by appending "_rules" to the CSV file name
                    rules_file_name = os.path.splitext(save_file_name)[0] + "_rules.txt"
                    abac_to_csv(lines, user_attributes, resource_attributes, multi_value_user_attributes, multi_value_resource_attributes, save_file_name, rules_file_name)
                    QMessageBox.information(app, "Success", f"ABAC file converted to CSV successfully.\nSaved as {save_file_name}\nRules saved as {rules_file_name}")
                else:
                    QMessageBox.warning(
                        app,
                        "Warning",
                        "No output file selected for CSV. Conversion cancelled.",
                    )
        except Exception as e:
            QMessageBox.critical(
                app, "Error", f"Failed to convert ABAC file:\n{str(e)}"
            )
