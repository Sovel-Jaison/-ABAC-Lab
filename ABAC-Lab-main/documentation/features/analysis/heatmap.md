# Code Structure of `heatmap.py`

## **Overview**

This module provides functionality to generate and display heatmaps that visualize the coverage of ABAC policies. The heatmaps show the relationship between rules and attributes, highlighting which attributes are most frequently used in policy evaluations.

## Key Features
- Precomputes heatmap data for efficient visualization
- Displays interactive heatmaps with rule-attribute relationships
- Supports multiple policy files with a dropdown selector
- Responsive design that adapts to window resizing

## Imports
#### **Standard Library Import**
- `os`: Provides functions for interacting with the operating system, such as file path manipulation

#### **PyQt5 Imports**
Used for GUI components of the app.
- **`QtWidgets`**: Contains classes for creating / managing GUI elements.
    - `QWidget`: Base class for all UI objects, used as containers for other widgets
    - `QVBoxLayout`: Vertical box layout manager for widget arrangement
    - `QHBoxLayout`: Horizontal box layout manager for widget arrangement  
    - `QPushButton`: Interactive button widget (used for Back button)
    - `QMessageBox`: Pre-built dialog boxes for warnings/notifications
    - `QComboBox`: Dropdown selection widget for policy selection
    - `QLabel`: Text display widget for labels and information

- **`QtCore`**: 
    - `Qt`: Contains core Qt enums and flags (used for alignment properties)

#### **Matplotlib Imports**
Visualization framework for creating the heatmap.
- `FigureCanvasQTAgg` (as `FigureCanvas`): Embeds matplotlib figures in Qt applications
- `NavigationToolbar2QT` (as `NavigationToolbar`): Interactive toolbar for figure navigation (zoom/pan/save)
- `pyplot` (as `plt`): MATLAB-style plotting interface for figure creation

### **Seaborn Import**
- `sns`: High-level statistical visualization library that enhances matplotlib, used here for creating aesthetically pleasing heatmaps with built-in annotations.

### **Numpy Import**
- `np`: Fundamental package for numerical computing in Python, used for:
  - Creating and manipulating the heatmap data matrix
  - Efficient numerical operations on rule/attribute counts
  - Handling array-based data structures

## Functions

### `precompute_heatmaps(app)`
**Purpose**:  
Precomputes and caches heatmap data for all loaded ABAC policies to enable fast visualization switching.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | The main application instance containing ABAC data |

**Behavior**:
1. Iterates through all ABAC files in `app.abac_data`
2. Skips already cached files
3. Calls `generate_heatmap_data()` for each uncached file
4. Stores results in `app.heatmap_cache` dictionary

**Example Usage**:
```python
def on_files_loaded(app):
    precompute_heatmaps(app)  # Cache heatmaps when files are first loaded
```

---

### `generate_heatmap_data(app, file_path)`
**Purpose**:  
Generates the numerical data structure needed for heatmap visualization of a single ABAC policy.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Path to the ABAC policy file     |

**Return Value**:
Returns a dictionary with the following structure:
```python
{
    "data": np.ndarray,      # 2D matrix of attribute usage counts (rules x attributes)
    "rules": List[int],      # List of rule indices (0-based)
    "attributes": List[str], # Sorted attribute names (prefixed with 'user.' or 'res.')
    "file_name": str         # Base filename for display purposes
}
```

**Algorithm**:
1. Collects all actions from all rules
2. Initializes counting structure
3. Evaluates each rule against all user-resource-action combinations
4. Counts attribute usage when rules evaluate to True
5. Structures data into a matrix format

**Example Output**:
```python
{
    "data": array([[5, 2, 0], [3, 4, 1]]),
    "rules": [0, 1],
    "attributes": ['user.role', 'user.department', 'res.type'],
    "file_name": "policy1.abac"
}
```

---

### `show_heatmap(app)`
**Purpose**:  
Main interface function that sets up and displays the heatmap visualization widget.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**UI Components Created**:
1. **Container Widget**: White background panel holding all elements
2. **Top Control Bar**:
   - Back button (returns to main view)
   - Policy selection dropdown (when multiple files exist)
3. **Heatmap Display Area**: Canvas for matplotlib figure

**Behavior**:
1. Hides all other application widgets
2. Clears previous results
3. Sets up responsive layout
4. Initializes display with first policy's heatmap
5. Shows scrollable results area

**Event Handling**:
- Back button: Calls `app.show_page2()`
- Dropdown selection: Triggers `display_heatmap()` for selected file

---

### `display_heatmap(app, file_path)`
**Purpose**:  
Renders the actual heatmap visualization for a specific policy file.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| file_path | str       | Path to the ABAC policy file     |

**Visualization Features**:
1. **Heatmap Properties**:
   - Color gradient: Bluescale (darker = more usage)
   - Annotated cells: Shows exact count values
   - Grid lines: Black borders between cells

2. **Axis Labels**:
   - X-axis: Attributes (grouped by user/resource)
   - Y-axis: Rules (numbered sequentially)

3. **Interactive Elements**:
   - Zoom/Pan tools via navigation toolbar
   - Responsive to window resizing
   - Hover tooltips (via matplotlib)
