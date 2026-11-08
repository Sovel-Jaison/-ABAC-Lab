# **Code Structure of `bar_graph.py`**

## **Overview**

Provides functionality to generate and display bar graphs that visualize access patterns in ABAC policies. The bar graphs represent the top and least accessed resources based on policy evaluations, highlighting which resources have the most and least access across users and actions.

## **Key Features**

* Precomputes bar graph data for fast visualization switching
* Displays interactive bar graphs for the top 10 and least 10 accessed resources
* Supports multiple policy files with a dropdown selector for easy switching
* Responsive design with hover functionality to display exact values on bar graph

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
Visualization framework for creating the bar graphs.
- `FigureCanvasQTAgg` (as `FigureCanvas`): Embeds matplotlib figures in Qt applications
- `NavigationToolbar2QT` (as `NavigationToolbar`): Interactive toolbar for figure navigation (zoom/pan/save)
- `pyplot` (as `plt`): MATLAB-style plotting interface for figure creation

### **Seaborn Import**
- `sns`: High-level statistical visualization library that enhances matplotlib, used here for creating aesthetically pleasing bar graphs with color gradients.

## **Functions**

### `initialize_bar_graph_cache(app)`

**Purpose**:
Initializes the cache to store precomputed bar graph data for faster access.

**Parameters**:

| Parameter | Type        | Description                   |
| --------- | ----------- | ----------------------------- |
| app       | QMainWindow | The main application instance |

---

### `precompute_bar_graphs(app)`

**Purpose**:
Precomputes and caches bar graph data for all loaded ABAC policies.

**Parameters**:

| Parameter | Type        | Description                                        |
| --------- | ----------- | -------------------------------------------------- |
| app       | QMainWindow | The main application instance containing ABAC data |

**Behavior**:

1. Iterates through all ABAC files in `app.abac_data`
2. Skips already cached files
3. Calls `generate_bar_graph_data()` for each uncached file
4. Stores results in `app.bar_graph_cache` dictionary

**Example Usage**:

```python
def on_files_loaded(app):
    precompute_bar_graphs(app)  # Cache bar graphs when files are first loaded
```

---

### `generate_bar_graph_data(app, file_path)`

**Purpose**:
Generates the numerical data structure needed for bar graph visualization of a single ABAC policy.

**Parameters**:

| Parameter  | Type        | Description                  |
| ---------- | ----------- | ---------------------------- |
| app        | QMainWindow | Main application instance    |
| file\_path | str         | Path to the ABAC policy file |

**Return Value**:

```python
{
    "top_10": [(resource_name, access_count), ...],
    "least_10": [(resource_name, access_count), ...],
    "file_name": str  # Base filename for display purposes
}
```

**Algorithm**:

1. Collects all actions from all rules
2. Initializes counting structure
3. Evaluates each rule against all user-resource-action combinations
4. Counts access to resources when rules evaluate to True
5. Structures the data into a dictionary for top 10 and least 10 accessed resources

---

### `show_bar_graph(app)`

**Purpose**:
Main interface function that sets up and displays the bar graph visualization widget.

**Parameters**:

| Parameter | Type        | Description               |
| --------- | ----------- | ------------------------- |
| app       | QMainWindow | Main application instance |

**UI Components Created**:

1. **Container Widget**: White background panel holding all elements
2. **Top Control Bar**:

   * Back button (returns to main view)
   * Policy selection dropdown (when multiple files exist)
3. **Bar Graph Display Area**: Canvas for matplotlib figure

**Behavior**:

1. Hides all other application widgets
2. Clears previous results
3. Sets up responsive layout
4. Initializes display with first policy's bar graph
5. Shows scrollable results area

**Event Handling**:

* Back button: Calls `app.show_page2()`
* Dropdown selection: Triggers `display_bar_graph_from_cache()` for selected file

---

### `display_bar_graph_from_cache(app, file_path)`

**Purpose**:
Renders the actual bar graph visualization for a specific policy file.

**Parameters**:

| Parameter  | Type        | Description                  |
| ---------- | ----------- | ---------------------------- |
| app        | QMainWindow | Main application instance    |
| file\_path | str         | Path to the ABAC policy file |

**Visualization Features**:

1. **Bar Graph Properties**:

   * Top 10 resources with highest access
   * Least 10 resources with lowest access
   * Color gradient: Bluescale (darker = more usage)
   * Annotated bars: Shows exact count values

2. **Interactive Elements**:

   * Zoom/Pan tools via navigation toolbar
   * Responsive to window resizing
   * Hover tooltips (via matplotlib)

**Hover Functionality**:

* Displays exact access count values when hovering over bars