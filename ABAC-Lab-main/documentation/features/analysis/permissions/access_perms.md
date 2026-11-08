# Code Structure of permissions.py
## **Overview**

This module provides comprehensive functionality for analyzing and visualizing ABAC policy permissions through request file processing. It features an interactive interface for viewing, filtering, and managing permission evaluation results.

## Key Features
- Multi-file request processing with ABAC policy association
- Interactive results display with color-coded permissions
- Advanced filtering and sorting capabilities
- Search functionality with highlighting
- Statistical analysis of permission outcomes
- Export capabilities for results

## Imports
#### **Standard Library Imports**
- `re`: Regular expression operations for text processing
- `os`: Operating system interfaces for file path manipulation

#### **PyQt5 Imports**
- **`QtWidgets`**:
  - `QWidget`, `QVBoxLayout`, `QHBoxLayout`, `QGridLayout`: UI containers and layout managers
  - `QPushButton`: Interactive buttons for navigation and actions
  - `QLabel`: Text display widgets with rich formatting
  - `QScrollArea`: Scrollable container for large result sets
  - `QComboBox`: Dropdown selectors for filtering and sorting
  - `QLineEdit`: Input field for search functionality
  - `QFileDialog`: File selection dialogs
  - `QMessageBox`: Pre-built dialog boxes for user feedback
  - `QInputDialog`: Input prompt dialogs

- **`QtCore`**:
  - `Qt`: Core Qt enums and flags for UI configuration

#### **Core Import**
- `process_request`: From core.myabac for ABAC policy evaluation

## Functions

### `show_permissions(app)`
**Purpose**:  
Main entry point for the permissions analysis interface.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Workflow**:
1. Validates ABAC data availability
2. Handles single/multiple policy file cases
3. Processes request files through file dialogs
4. Manages ABAC policy associations
5. Initiates results processing and display

**UI Components**:
- File selection dialogs
- Policy association interface
- Results processing pipeline

---

### `display_permissions_results(app)`
**Purpose**:  
Initializes and configures the results display container.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Behavior**:
1. Clears previous results
2. Sets up container widgets and layouts
3. Displays first request file's results
4. Configures scrollable area

---

### `show_permissions_for_file(app, request_file)`
**Purpose**:  
Comprehensive display of permission results for a specific request file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| request_file | str     | Path to the request file        |

**UI Structure**:
1. **Header Section**:
   - Evaluation information label
   - Description text
2. **Control Bar**:
   - File selector dropdown
   - Sort/filter dropdowns
   - Search field
   - Save button
3. **Results Grid**:
   - Two-column layout
   - Color-coded permission results
4. **Footer**:
   - Statistics display
   - Navigation buttons

**Features**:
- Responsive layout
- Text selection enabled
- Word wrapping for long results
- Visual distinction between Permit/Deny

---

### `on_file_dropdown_changed(app, selected_file_name)`
**Purpose**:  
Handles file selection changes in the dropdown menu.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| selected_file_name | str | Name of selected request file |

**Behavior**:
- Updates displayed results to show selected file's data
- Maintains current filter/sort/search settings

---

### `update_displayed_results(app, results)`
**Purpose**:  
Dynamically updates results display based on user interactions.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| results   | list      | Current set of results to display |

**Filter/Sort Logic**:
1. Applies search query highlighting
2. Processes filter options (All/Permit/Deny)
3. Handles sort options (Default/User/Resource)
4. Maintains original order when needed

**Visual Features**:
- Search term highlighting
- Color-coded background based on decision
- Consistent styling across results

---

### `save_permissions_to_file(app, request_file)`
**Purpose**:  
Exports currently displayed results to a text file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| request_file | str     | Source request file for naming  |

**Export Process**:
1. Collects currently displayed results
2. Strips HTML formatting
3. Provides file save dialog
4. Handles write operations with error checking
5. Provides user feedback on success/failure

---

### `compute_abac_stats(app)`
**Purpose**:  
Calculates comprehensive statistics about the ABAC policy evaluation.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Return Value**:
Dictionary containing:
```python
{
    "Users": int,
    "Resources": int,
    "Rules": int,
    "Permits": int,
    "Denies": int
}
```

**Statistical Analysis**:
- Counts based on actual processed requests
- Provides accurate Permit/Deny ratios
- Supports policy analysis and optimization

---

### `update_sorted_permissions(app, results)`
**Purpose**:  
Advanced sorting and display of permission results.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| results   | list      | Results to process and display  |

**Features**:
- Two-column balanced layout
- Dynamic sorting based on user selection
- Search term highlighting preservation
- Responsive widget management
