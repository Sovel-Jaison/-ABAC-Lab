# Code Structure of `abac_stats.py`

## **Overview**

This module provides functionality to compute, display, and save statistics for ABAC policies. The statistics include counts of users, resources, attributes, rules, and permissions granted by the policy.

## Key Features
- Precomputes and caches statistics for all loaded ABAC policies
- Displays statistics in a clean grid layout
- Supports multiple policy files with dropdown selection
- Allows saving statistics to text files
- Efficient permission counting that avoids duplicates

## Imports
#### **Standard Library Import**
- `os`: Provides functions for file path manipulation and basename extraction

#### **PyQt5 Imports**
Used for GUI components and file operations.
- **`QtWidgets`**: 
    - `QLabel`: For displaying text labels
    - `QSizePolicy`: For widget sizing behavior
    - `QHBoxLayout`, `QGridLayout`: For horizontal and grid-based layouts
    - `QComboBox`: Dropdown menu for policy selection
    - `QMessageBox`: For displaying warnings and information dialogs
    - `QPushButton`: Interactive button widget
    - `QFileDialog`: For file save operations
    - `QWidget`: Base container widget

- **`QtCore`**:
    - `Qt`: Contains alignment flags and other core enums

## Functions

### `precompute_all_stats(app)`
**Purpose**:  
Precomputes and caches statistics for all loaded ABAC policies.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**Behavior**:
1. Initializes `app.abac_stats` dictionary
2. Iterates through all loaded ABAC files
3. Calls `get_abac_stats()` for each file
4. Stores results in cache

**Example Usage**:
```python
precompute_all_stats(app)  # Typically called after loading files
```
---

### `show_stats(app)`
**Purpose**:  
Main interface function that sets up and displays the statistics view.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |

**UI Components**:
1. **Dropdown Menu**: For selecting between multiple policies
2. **Stats Grid**: Cleanly formatted statistics display
3. **Top Bar Layout**: Contains the policy selection controls

**Behavior**:
1. Clears previous statistics display
2. Shows warning if no files are loaded
3. Sets up policy selection dropdown
4. Displays stats for current/default policy

---

### `get_abac_stats(app, abac_path)`
**Purpose**:  
Computes detailed statistics for a single ABAC policy.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| abac_path | str       | Path to the ABAC policy file     |

**Return Value**:
Returns a dictionary with the following statistics:
```python
{
    "Total Users": int,
    "Total Resources": int,
    "Total User Attributes": int,
    "Total Resource Attributes": int,
    "Total Rules": int,
    "Total Permissions Granted": int
}
```

**Key Features**:
- Counts unique permissions using set operations
- Efficiently gathers all user and resource attributes
- Handles large policy files effectively

**Example Output**:
```python
{
    "Total Users": 42,
    "Total Resources": 15,
    "Total User Attributes": 5,
    "Total Resource Attributes": 3,
    "Total Rules": 8,
    "Total Permissions Granted": 127
}
```

---

### `display_stats(app, abac_path)`
**Purpose**:  
Displays precomputed statistics for a specific policy in a grid layout.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| abac_path | str       | Path to the ABAC policy file     |

**UI Features**:
1. **Grid Layout**:
   - Left column: Statistic names
   - Right column: Values
   - Consistent spacing and alignment
2. **Clean Styling**:
   - Uniform font sizes
   - No borders for minimal appearance
3. **Responsive Design**:
   - Maintains layout at different window sizes

**Behavior**:
1. Updates current ABAC path reference
2. Clears previous stats display
3. Creates new grid layout with current stats
4. Adds to main container

---

### `save_abac_stats(app, abac_path)`
**Purpose**:  
Saves the statistics to a text file with policy filename included.

**Parameters**:
| Parameter | Type      | Description                      |
|-----------|-----------|----------------------------------|
| app       | QMainWindow | Main application instance       |
| abac_path | str       | Path to the ABAC policy file     |

**File Format**:
```
ABAC File: policy1.abac

Total Users: 42
Total Resources: 15
Total User Attributes: 5
Total Resource Attributes: 3
Total Rules: 8
Total Permissions Granted: 127
```

**User Interaction**:
1. Opens file save dialog
2. Validates path selection
3. Handles write operations
4. Provides success/error feedback

**Error Handling**:
- Catches and displays file operation errors
- Validates preconditions (file loaded)
