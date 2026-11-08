# Code Structure of `rule_perms.py`

## **Overview**

This module provides functionality to analyze and visualize permissions granted by ABAC rules, showing detailed statistics about which rules grant access to which user-resource-action combinations.

## Key Features
- Precomputes and caches permissions statistics for efficient display
- Paginated display of rule permissions for large datasets
- Interactive interface with file selection dropdown
- Save functionality for both full results and current page
- Detailed visualization of rule coverage and permissions

## Imports
#### **Standard Library Imports**
- `os`: For file path manipulation
- `re`: For regular expression pattern matching

#### **PyQt5 Imports**
- **`QtWidgets`**:
  - `QFileDialog`: File selection dialogs
  - `QComboBox`: Dropdown selection widget
  - `QMessageBox`: Pre-built dialog boxes
  - `QVBoxLayout/QHBoxLayout`: Layout managers
  - `QLabel`: Text display widget
  - `QFrame`: Separator lines
  - `QInputDialog`: Input prompt dialogs
  - `QWidget`: Base UI container
  - `QPushButton`: Interactive buttons
  - `QScrollArea`: Scrollable container
  - `QLineEdit`: Text input field

- **`QtCore`**:
  - `Qt`: Core Qt enums and flags

- **`QtGui`**:
  - `QIntValidator`: Input validation for page numbers

#### **Core Import**
- `RuleManager`: From core.rule for parsing and evaluating ABAC rules

## Permstats Functions: functions for rule permissions feature


### `initialize_permstats_cache(app)`
**Purpose**:  
Initializes the cache dictionary for storing precomputed permissions statistics.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | The main application instance   |

**Behavior**:
1. Creates a `permstats_cache` dictionary attribute on the app object

---

### `precompute_permstats(app)`
**Purpose**:  
Precomputes permissions statistics for all loaded ABAC policies.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | The main application instance   |

**Behavior**:
1. Ensures cache is initialized
2. Iterates through all ABAC files
3. Calls `generate_permstats_data()` for each uncached file
4. Stores results in `app.permstats_cache`

---

### `generate_permstats_data(app, file_path)`
**Purpose**:  
Generates permissions statistics data for a single ABAC policy file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Path to the ABAC policy file     |

**Return Value**:
Returns a list of dictionaries containing:
```python
[
    {
        'rule_text': str,           # Original rule text
        'permissions_count': int,   # Total permissions granted
        'permissions_list': List[str]  # Detailed permissions
    },
    ...
]
```

**Algorithm**:
1. Reads the ABAC file line by line
2. For each rule:
   - Evaluates against all user-resource-action combinations
   - Counts successful accesses
   - Stores detailed permission strings

---

### `show_permstats(app)`
**Purpose**:  
Main interface function that sets up and displays the permissions statistics widget.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**UI Components**:
1. **Top Bar**:
   - Back button
   - Policy selection dropdown
2. **Main Display Area**:
   - Scrollable list of rules and permissions
3. **Bottom Bar**:
   - Pagination controls
   - Save buttons

**Behavior**:
1. Hides other application widgets
2. Initializes display with first policy's data
3. Sets up pagination controls
4. Shows scrollable results area

---

### `display_permstats(app, file_path)`
**Purpose**:  
Displays paginated permissions statistics for a specific policy file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Path to the ABAC policy file     |

**Pagination Features**:
1. Tracks current page and positions within rules
2. Smart continuation markers for split rules
3. Page number input with validation
4. First/Last page navigation
5. Centered page number display

**Visualization**:
1. Rule text with syntax highlighting
2. Permission counts
3. Detailed permission listings
4. Continuation indicators for split displays

---

### `on_permstats_page_input(app, file_path)`
**Purpose**:  
Handles manual page number input for navigation with validation.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Current policy file path         |

**Behavior**:
1. Retrieves input text from page number field
2. Validates input is numeric and within page bounds
3. Shows appropriate warning messages for invalid input
4. Calls `set_permstats_page()` with valid page numbers

---

### `set_permstats_page(app, file_path, page)`
**Purpose**:  
Sets the current page and updates the display with proper position tracking.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Policy file path                 |
| page      | int       | Page number to display           |

**Navigation Logic**:
1. For forward navigation:
   - Continues from last recorded positions in rules
   - Tracks how many permissions were shown from each rule
2. For backward navigation:
   - Recalculates positions from start
   - Processes rules in reverse to find correct starting points

**Post-Navigation**:
1. Updates scroll position to top
2. Refreshes display with new page content

---

### `on_permstats_file_dropdown_changed(app, selected_file_name)`
**Purpose**:  
Handles file selection changes in the dropdown menu.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| selected_file_name | str | Name of the selected policy file |

**Behavior**:
1. Matches the displayed filename with cached file paths
2. Updates the current ABAC path in the app state
3. Triggers display refresh with new file's data

---

### `get_permissions_for_rule(rule_text, user_mgr, res_mgr)`
**Purpose**:  
Evaluates a rule against all user-resource combinations to determine granted permissions.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| rule_text | str       | The ABAC rule text to evaluate   |
| user_mgr  | UserManager | Manager containing all users    |
| res_mgr   | ResourceManager | Manager containing all resources |

**Return Value**:
Returns a list of permission strings in the format:
`"User: [username], Resource: [resourcename], Action: [action]"`

**Evaluation Process**:
1. Parses the rule using RuleManager
2. Iterates through all user-resource-action combinations
3. Records permissions where evaluation returns True

---

### `strip_html_tags(text)`
**Purpose**:  
Cleans HTML formatting from text for plain text file output.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| text      | str       | Text containing HTML tags        |

**Return Value**:
Returns clean text with all HTML tags removed

**Implementation**:
Uses regular expressions to remove all content between < and > characters

---

### `save_permstats_results(app)`
**Purpose**:  
Saves all permissions statistics for the current policy to a text file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Save Process**:
1. Identifies current policy from dropdown
2. Collects all displayed results
3. Presents file save dialog
4. Writes results with proper formatting
5. Shows success/error notification

---

### `save_permstats_page_results(app, file_path)`
**Purpose**:  
Saves only the currently displayed page of permissions statistics.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Policy file path being displayed |

**Features**:
1. Generates default filename with page number
2. Preserves exact current page display
3. Includes page information header
4. Handles file write errors gracefully

---

## RuleVu Functions: used for file check feature

### `show_rulevu(app)`
**Purpose**:  
Specialized interface for uploading and analyzing external rule files against ABAC policies.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Workflow**:
1. File selection dialog for rule files
2. Syntax validation of rule formats
3. Policy association dialogs
4. Paginated results display setup

**UI Components**:
1. File information header
2. Rule file dropdown selector
3. Paginated results area
4. Navigation controls

---

### `on_rule_file_dropdown_changed(app, rule_file_dropdown, rule_abac_associations, selected_file_name, info_label)`
**Purpose**:  
Handles rule file selection changes in the RuleVu interface.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| rule_file_dropdown | QComboBox | The dropdown widget            |
| rule_abac_associations | dict | Mapping of rule files to ABAC policies |
| selected_file_name | str | Name of selected rule file      |
| info_label | QLabel | Header label to update          |

**Behavior**:
1. Updates information header with new file context
2. Clears previous results
3. Initializes pagination for new file
4. Loads and displays first page of results

---

### `change_rulevu_page(app, rule_file, direction, rule_abac_associations, info_label)`
**Purpose**:  
Handles page navigation in the RuleVu interface.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| rule_file | str       | Path to current rule file        |
| direction | int       | Navigation direction (+1/-1)     |
| rule_abac_associations | dict | File association mapping       |
| info_label | QLabel | Header label for updates        |

**Navigation Logic**:
1. Updates current page number
2. For forward navigation:
   - Continues from last position in each rule
3. For backward navigation:
   - Processes rules in reverse to find start positions
4. Maintains scroll position consistency

---

### `save_rulevu_results(app, rule_abac_associations)`
**Purpose**:  
Saves all RuleVu evaluation results to a file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| rule_abac_associations | dict | File association mapping       |

**Features**:
1. Preserves rule and permission formatting
2. Includes association information in header
3. Handles large results sets efficiently

---

### `save_rulevu_page_results(app, rule_abac_associations)`
**Purpose**:  
Saves only the current page of RuleVu results.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| rule_abac_associations | dict | File association mapping       |

**Implementation**:
1. Generates informative header with page context
2. Preserves exact current display content
3. Uses page number in default filename
