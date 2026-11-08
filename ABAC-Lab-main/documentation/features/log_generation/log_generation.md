# Code Structure of `log_generation.py`

## **Overview**

This module generates synthetic access logs based on ABAC policy files. It allows the user to specify the number of logs, the percentage of permits, overpermits, and underpermits, and exports the logs as a CSV file.

## Key Features

- Generates logs with configurable permit/deny ratios
- Supports overpermit and underpermit injection for testing
- Randomizes user, resource, and action selection
- Integrates with PyQt5 dialogs for file selection and error handling

## Imports

#### **Standard Library Imports**

- `csv`: For writing logs to CSV
- `os`: File path operations
- `random`: Random selection for log generation

#### **PyQt5 Imports**

- `Qt`: Core enums
- `QFileDialog`, `QMessageBox`: For user interaction

#### **Core Imports**

- `ResourceManager`, `RuleManager`, `UserManager`: ABAC data structures

## Functions

### `generate_logs(app)`

**Purpose**:  
Generates synthetic access logs for a selected ABAC policy.

**Parameters**:
| Parameter | Type | Description |
|-----------|-------------|----------------------------------|
| app | QMainWindow | Main application instance |

**Behavior**:

1. Validates user input for log counts and percentages
2. Selects the ABAC policy and extracts users, resources, and actions
3. Randomly generates log entries as permit/deny, with optional over/underpermits
4. Shuffles logs for randomness
5. Prompts user to save the logs as a CSV file

**CSV Format**:

```
User, Resource, Action, Decision, Flag
alice, file1, read, Permit, 0
bob, file2, write, Deny, 1
...
```

- `Flag` is 1 for over/underpermits, 0 otherwise

**Error Handling**:

- Validates all user inputs and file selections
- Handles file write errors and user cancellation

---
