# Code Structure of `conv.py`

## **Overview**

This module provides utilities for converting ABAC policy files to CSV format and vice versa. It also includes a drag-and-drop file upload widget for ABAC files and integrates with the PyQt5 GUI for user interaction.

## Key Features

- Extracts user and resource attributes from ABAC files
- Converts ABAC files to CSV (with multi-value attribute handling)
- Converts CSV files back to ABAC format
- Provides a drag-and-drop and click-to-upload widget for ABAC files
- Integrates with PyQt5 dialogs for file selection and error handling

## Imports

#### **Standard Library Imports**

- `re`: Regular expressions for parsing ABAC lines
- `csv`: Reading and writing CSV files
- `os`, `sys`: File path and system operations

#### **PyQt5 Imports**

- **`QtWidgets`**:
  - `QWidget`, `QLabel`, `QHBoxLayout`, `QFileDialog`, `QMessageBox`
- **`QtCore`**:
  - `Qt`: Alignment and event handling

## Functions

### `extract_attributes(lines)`

**Purpose**:  
Parses ABAC lines to extract user and resource attribute names, including multi-value attributes.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| lines | list | List of ABAC policy lines |

**Return Value**:  
Tuple of four elements:

- List of user attribute names
- List of resource attribute names
- Set of multi-value user attribute names
- Set of multi-value resource attribute names

---

### `abac_to_csv(...)`

**Purpose**:  
Converts ABAC policy lines to a combined CSV file and a separate rules file.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| lines | list | ABAC policy lines |
| user_attributes | list | User attribute names |
| resource_attributes | list | Resource attribute names |
| multi_value_user_attributes | set | Multi-value user attributes |
| multi_value_resource_attributes | set | Multi-value resource attributes |
| combined_csv_path | str | Output CSV file path |
| rule_ouput_path | str | Output rules file path |

**Behavior**:

- Writes CSV with prefixed headers (`U-`, `R-`)
- Handles multi-value attributes with `*` marker and `|` separator
- Writes rules to a separate text file

---

### `csv_to_abac(combined_csv_path, abac_output_path)`

**Purpose**:  
Converts a combined CSV file back to ABAC format.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| combined_csv_path | str | Path to input CSV file |
| abac_output_path | str | Path to output ABAC file |

**Behavior**:

- Reads CSV and reconstructs `userAttrib` and `resourceAttrib` lines
- Handles multi-value and empty attributes

---

### `SingleFileUpload(QWidget)`

**Purpose**:  
A PyQt5 widget for uploading ABAC files via drag-and-drop or file dialog.

**Key Features**:

- Custom styling and icon
- Accepts only `.abac` files
- Calls `upload_abac_file` on successful upload

---

### `convert_uploaded_file(app)`

**Purpose**:  
Converts a selected ABAC file (from the GUI) to CSV and rules files.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| app | QMainWindow | Main application instance |

**Behavior**:

- Prompts user for output file location
- Handles errors and user cancellation

---

### `upload_abac_file(app, file_name)`

**Purpose**:  
Handles uploading and conversion of an ABAC file to CSV and rules files.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| app | QMainWindow | Main application instance |
| file_name | str | Path to ABAC file |

**Behavior**:

- Prompts user for output file location
- Handles errors and user cancellation

---
