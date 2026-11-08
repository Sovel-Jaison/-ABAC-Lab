import csv
import os
import random
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox
)
from core.res import ResourceManager
from core.rule import RuleManager
from core.user import UserManager

def generate_logs(app):
    # Get the selected policy file
    selected_file = app.page4_current_uploaded_files.currentText()
    if not selected_file:
        QMessageBox.warning(app, "Warning", "No policy file selected.")
        return
    
    # Validate the input numbers
    try:
        num_logs = int(app.page4_integer_text_edit.text())
        if num_logs <= 0:
            raise ValueError("Number of logs must be greater than zero.")
    except ValueError as e:
        QMessageBox.warning(app, "Invalid Input", str(e))
        return

    try:
        percentage_permits = int(app.page4_percentage_text_edit.text()) if app.page4_percentage_text_edit.text() else None
        if percentage_permits is not None and not (0 <= percentage_permits <= 100):
            raise ValueError("Percentage of permits must be between 0 and 100.")
    except ValueError as e:
        QMessageBox.warning(app, "Invalid Input", str(e))
        return
    
    try:
        percentage_overpermits = int(app.page4_over_percentage_text_edit.text()) if app.page4_over_percentage_text_edit.text() else 0
        if not (0 <= percentage_overpermits <= 100):
            raise ValueError("Percentage of overpermits must be between 0 and 100.")
    except ValueError as e:
        QMessageBox.warning(app, "Invalid Input", str(e))
        return

    try:
        percentage_underpermits = int(app.page4_under_percentage_text_edit.text()) if app.page4_under_percentage_text_edit.text() else 0
        if not (0 <= percentage_underpermits <= 100):
            raise ValueError("Percentage of underpermits must be between 0 and 100.")
    except ValueError as e:
        QMessageBox.warning(app, "Invalid Input", str(e))
        return

    if percentage_overpermits + percentage_underpermits > 100:
        QMessageBox.warning(app, "Invalid Input", "The sum of overpermits and underpermits cannot exceed 100%.")
        return
    
    # Check that percentage_overpermits does not exceed percentage_permits
    if percentage_permits is not None and percentage_overpermits > percentage_permits:
        QMessageBox.warning(app, "Invalid Input", "Percentage of overpermits cannot exceed the percentage of permits.")
        return

    # Check that percentage_underpermits does not exceed the percentage of denies (100 - percentage_permits)
    if percentage_permits is not None and percentage_underpermits > (100 - percentage_permits):
        QMessageBox.warning(app, "Invalid Input", "Percentage of underpermits cannot exceed the percentage of denies.")
        return
    
    file_path = None
    for path in app.uploaded_files:
        if os.path.basename(path) == selected_file:
            file_path = path
            break

    if not file_path:
        QMessageBox.warning(app, "Warning", "Selected file not found.")
        return

    # Get the ABAC data for the selected file
    user_mgr, res_mgr, rule_mgr = app.abac_data[file_path]

    # Collect all valid users, resources, and actions
    users = list(user_mgr.users.values())
    resources = list(res_mgr.resources.values())
    actions = set()
    for rule in rule_mgr.rules:
        actions.update(rule.acts)
    actions = list(actions)

    if not users or not resources or not actions:
        QMessageBox.warning(app, "Warning", "The policy file does not contain valid users, resources, or actions.")
        return

    # Generate logs
    logs = []
    if percentage_permits is not None:
        num_permits = int((percentage_permits / 100) * num_logs)
        num_denies = num_logs - num_permits

        # Calculate overpermits and underpermits
        num_overpermits = int((percentage_overpermits / 100) * num_logs)
        num_underpermits = int((percentage_underpermits / 100) * num_logs)

        permits_generated = 0
        denies_generated = 0
        overpermits_generated = 0
        underpermits_generated = 0

        while (
            permits_generated < num_permits - num_overpermits
            or denies_generated < num_denies - num_underpermits
            or overpermits_generated < num_overpermits
            or underpermits_generated < num_underpermits
        ):
            user = random.choice(users)
            resource = random.choice(resources)
            action = random.choice(actions)
            decision = "Permit" if any(rule.evaluate(user, resource, action) for rule in rule_mgr.rules) else "Deny"

            if decision == "Permit":
                if underpermits_generated < num_underpermits:
                    # Generate an underpermit (should permit but deny)
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Deny", 1])
                    underpermits_generated += 1
                elif permits_generated < num_permits - num_overpermits:
                    # Generate a normal permit
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Permit", 0])
                    permits_generated += 1
            elif decision == "Deny":
                if overpermits_generated < num_overpermits:
                    # Generate an overpermit (should deny but permit)
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Permit", 1])
                    overpermits_generated += 1
                elif denies_generated < num_denies - num_underpermits:
                    # Generate a normal deny
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Deny", 0])
                    denies_generated += 1
    else:
        num_overpermits = int((percentage_overpermits / 100) * num_logs)
        num_underpermits = int((percentage_underpermits / 100) * num_logs)

        overpermits_generated = 0
        underpermits_generated = 0
        normal_logs_generated = 0

        while (
            overpermits_generated < num_overpermits
            or underpermits_generated < num_underpermits
            or normal_logs_generated < num_logs - num_overpermits - num_underpermits
        ):
            user = random.choice(users)
            resource = random.choice(resources)
            action = random.choice(actions)
            decision = "Permit" if any(rule.evaluate(user, resource, action) for rule in rule_mgr.rules) else "Deny"

            if decision == "Permit":
                if underpermits_generated < num_underpermits:
                    # Generate an underpermit (should permit but deny)
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Deny", 1])
                    underpermits_generated += 1
                elif normal_logs_generated < num_logs - num_overpermits - num_underpermits:
                    # Generate a normal permit
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Permit", 0])
                    normal_logs_generated += 1
            elif decision == "Deny":
                if overpermits_generated < num_overpermits:
                    # Generate an overpermit (should deny but permit)
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Permit", 1])
                    overpermits_generated += 1
                elif normal_logs_generated < num_logs - num_overpermits - num_underpermits:
                    # Generate a normal deny
                    logs.append([user.get_attribute("uid"), resource.get_attribute("rid"), action, "Deny", 0])
                    normal_logs_generated += 1

    # Shuffle the logs to mix permits and denies
    random.shuffle(logs)

    # Export logs as a CSV file
    save_file_name, _ = QFileDialog.getSaveFileName(
        app,
        "Save Generated Logs",
        "",
        "CSV Files (*.csv);;All Files (*)",
        options=QFileDialog.Options(),
    )
    if save_file_name:
        try:
            with open(save_file_name, 'w', newline='') as csvfile:
                log_writer = csv.writer(csvfile)
                log_writer.writerow(["User", "Resource", "Action", "Decision", "Flag"])
                log_writer.writerows(logs)
            QMessageBox.information(app, "Success", f"Logs generated and saved successfully.\nSaved as {save_file_name}")
        except Exception as e:
            QMessageBox.critical(app, "Error", f"Failed to save logs:\n{str(e)}")
    else:
        QMessageBox.warning(app, "Warning", "No output file selected for saving logs. Generation cancelled.")