import pickle
import pprint
import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from core.res import ResourceManager
from core.rule import RuleManager
from core.user import UserManager

def export_as_python_dict(app):
    selected_file = app.page3_current_uploaded_files.currentText()
    if not selected_file:
        QMessageBox.warning(app, "Warning", "No file selected for export.")
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
        abac_data = app.abac_data[file_path]
        save_file_name, _ = QFileDialog.getSaveFileName(
            app,
            "Save Serialized Data",
            "",
            "Pickle Files (*.pkl);;All Files (*)",
            options=QFileDialog.Options(),
        )
        if save_file_name:
            process_and_serialize_abac_data(abac_data, save_file_name)
            QMessageBox.information(app, "Success", f"Data exported and serialized successfully.\nSaved as {save_file_name}")
        else:
            QMessageBox.warning(app, "Warning", "No output file selected for serialization. Export cancelled.")
    except Exception as e:
        QMessageBox.critical(app, "Error", f"Failed to export data:\n{str(e)}")

def process_and_serialize_abac_data(abac_data, file_path):
    """
    Process the given ABAC data to extract user, resource, and rule attributes,
    and serialize the processed data to a file.
    
    Args:
        abac_data (dict): Dictionary containing file paths as keys and tuples of UserManager, ResourceManager, and RuleManager as values.
        file_path (str): Path to the file where the data will be serialized.
    """
    
    user_mgr, res_mgr, rule_mgr = abac_data
    
    user_data = {uid: user.get_attributes() for uid, user in user_mgr.users.items()}
    resource_data = {rid: resource.get_attributes() for rid, resource in res_mgr.resources.items()}
    rule_data = [rule.get_attributes() for rule in rule_mgr.rules]
    
    processed_data = {
        "users": user_data,
        "res": resource_data,
        "rules": rule_data
    }
    
    with open(file_path, 'wb') as file:
        pickle.dump(processed_data, file)
        
    # deserialized = deserialize_data(file_path)
    
    with open(f"{file_path}_text.txt", "w") as file:
        pprint.pprint(processed_data, stream=file)


def deserialize_data(file_path):
    """
    Deserialize data from a file.
    
    Args:
        file_path (str): Path to the file from which the data will be deserialized.
    
    Returns:
        dict: Deserialized data.
    """
    with open(file_path, 'rb') as file:
        return pickle.load(file)
