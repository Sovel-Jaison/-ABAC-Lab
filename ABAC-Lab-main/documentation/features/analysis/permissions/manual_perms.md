# Code Structure of `manual_check.py`

## **Overview**

This module provides functionality for manually checking permissions in ABAC policies by allowing users to input specific user, resource, and action combinations. It features intelligent autocomplete, paginated results display, and save capabilities.

## Key Features
- Interactive manual permission checking interface
- Smart autocomplete for user, resource, and action inputs
- Paginated display of results with color-coded permissions
- Save functionality for both full results and current page
- Detailed validation of input fields
- Performance optimized for large result sets

## Imports
#### **PyQt5 Imports**
- **`QtWidgets`**:
  - `QWidget`, `QVBoxLayout`, `QHBoxLayout`, `QGridLayout`: UI containers and layout managers
  - `QPushButton`: Interactive buttons
  - `QLabel`: Text display widgets  
  - `QScrollArea`: Scrollable container
  - `QMessageBox`: Dialog boxes for warnings/notifications
  - `QCompleter`, `QComboBox`: Autocomplete functionality
  - `QLineEdit`: Input fields
  - `QFileDialog`: File save dialogs

- **`QtCore`**:
  - `Qt`: Core Qt enums and flags

- **`QtGui`**:
  - `QIntValidator`: Input validation for page numbers

#### **Standard Library Imports**
- `os`: File path manipulation
- `re`: Regular expressions for text processing  
- `time`: Performance measurement

## Functions

### `show_manual_check(app)`
**Purpose**:  
Initializes and displays the manual check interface.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**UI Components**:
1. **Title Bar**: "Manual Check" label
2. **Input Section**:
   - File selection dropdown
   - User/resource/action input fields with autocomplete
   - Search button
3. **Results Area**: Scrollable grid of permission results
4. **Navigation Bar**: Back button and pagination controls

**Behavior**:
1. Validates ABAC data is loaded
2. Sets up input fields with autocomplete
3. Configures search functionality
4. Initializes results display area

---

### `manual_check_search(app)`
**Purpose**:  
Performs permission checks based on user inputs and displays results.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Validation**:
1. Verifies at least one input field is filled
2. Checks user/resource/action exist in policy
3. Validates action format (comma-separated)

**Algorithm**:
1. Filters users/resources based on input
2. Evaluates all rule combinations
3. Stores results with pagination tracking
4. Calls render function

**Output**:
- List of permission strings formatted as:
  `"User: X, Resource: Y, Action: Z -> Permit/Deny"`

---

### `manual_render_results_page(app)`
**Purpose**:  
Renders the current page of permission check results.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Display Features**:
1. **Grid Layout**: 2-column results display
2. **Color Coding**:
   - Green background for "Permit"
   - Pink background for "Deny"
3. **Pagination Controls**:
   - Page number buttons
   - First/Last navigation
   - Direct page input
4. **Performance Tracking**: Logs render timing

**Behavior**:
1. Calculates page range
2. Creates scrollable results grid
3. Adds navigation controls
4. Handles single-page vs multi-page cases

---

### `set_manual_page(app, page)`
**Purpose**:  
Updates current page and refreshes display.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| page      | int       | Page number to display           |

**Navigation**:
- Updates current page index
- Maintains scroll position
- Triggers re-render

---

### `on_manual_page_input(app)`
**Purpose**:  
Handles manual page number input.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Validation**:
1. Checks input is numeric
2. Verifies within page bounds
3. Shows error messages for invalid input

---

### `populate_manual_check_fields(app, abac_path)`
**Purpose**:  
Configures autocomplete for input fields based on policy data.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| abac_path | str       | Path to ABAC policy file         |

**Autocomplete Setup**:
1. Users: From UserManager
2. Resources: From ResourceManager  
3. Actions: Aggregated from all rules

**UI Behavior**:
- Shows suggestions on field click
- Resets action suggestions after input

---

### `show_suggestions(input_field)`
**Purpose**:  
Displays autocomplete suggestions for an input field.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| input_field | QLineEdit | Input field to show suggestions for |

---

### `reset_and_show_suggestions(input_field, original_list)`  
**Purpose**:  
Resets and shows autocomplete suggestions, used for action field.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| input_field | QLineEdit | Input field to update            |
| original_list | list    | Complete list of suggestions     |

---

### `on_manual_check_dropdown_changed(app)`
**Purpose**:  
Handles policy file selection changes.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Behavior**:
- Updates current policy reference
- Refreshes autocomplete data

---

### `save_manual_check_results(app)`
**Purpose**:  
Saves all permission check results to file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Features**:
- Includes ABAC filename header
- Preserves formatting
- Error handling for file operations
---

### `save_manual_check_page_results(app)`
**Purpose**:  
Saves only current page of results.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Features**:
- Auto-generates filename with page number
- Includes page information header
- Same formatting as full save
---

### `strip_html_tags(text)`
**Purpose**:  
Helper to clean HTML tags from text before saving.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| text      | str       | Text to clean                    |
