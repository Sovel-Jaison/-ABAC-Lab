# Code Structure of `serialization.py`

## **Overview**

This module provides serialization and deserialization utilities for ABAC policy data. It allows exporting ABAC data as a Python dictionary (pickled) alongside a text file with the rules in the policy.

## Key Features

- Serializes user, resource, and rule data to a pickle file
- Exports a pretty-printed text version of the data
- Integrates with PyQt5 dialogs for file selection and error handling
- Supports deserialization for later use

## Imports

#### **Standard Library Imports**

- `pickle`: For binary serialization
- `pprint`: For pretty-printing dictionaries
- `os`: File path operations

#### **PyQt5 Imports**

- `QMessageBox`, `QFileDialog`: For user interaction

#### **Core Imports**

- `ResourceManager`, `RuleManager`, `UserManager`: ABAC data structures

## Functions

### `export_as_python_dict(app)`

**Purpose**:  
Exports the selected ABAC policy data as a serialized Python dictionary.

**Parameters**:
| Parameter | Type | Description |
|-----------|-------------|----------------------------------|
| app | QMainWindow | Main application instance |

**Behavior**:

- Prompts user for output file location
- Calls `process_and_serialize_abac_data` to serialize data
- Handles errors and user cancellation

---

### `process_and_serialize_abac_data(abac_data, file_path)`

**Purpose**:  
Processes and serializes ABAC data to a pickle file and a text file.

**Parameters**:
| Parameter | Type | Description |
|-----------|-------|--------------------------------------------------------------------|
| abac_data | tuple | (UserManager, ResourceManager, RuleManager) |
| file_path | str | Output file path (without extension) |

**Behavior**:

- Extracts user, resource, and rule attributes
- Serializes to a `.pkl` file
- Writes a pretty-printed text version to a `.txt` file

---

### `deserialize_data(file_path)`

**Purpose**:  
Deserializes data from a pickle file.

**Parameters**:
| Parameter | Type | Description |
|-----------|------|---------------------------|
| file_path | str | Path to pickle file |

**Return Value**:  
Deserialized data as a dictionary.

---
