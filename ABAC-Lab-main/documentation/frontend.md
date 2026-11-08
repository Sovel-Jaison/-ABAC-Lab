# Code Structure for Frontend

This document provides an overview of the structure and functionality of the `gui.py` file, which serves as the main entry point for the ABAC Lab application. The file is built using PyQt5 and organizes the graphical user interface (GUI) into multiple pages, each dedicated to a specific feature of the tool.

---

## Table of Contents
1. [Overview](#1-overview)
2. [Key Components](#2-key-components)
   - [Imports](#21-imports)
   - [DragDropUpload Class](#22-dragdropupload-class)
   - [MyApp Class](#23-myapp-class)
3. [Application Pages](#3-application-pages)
4. [Toolbar](#4-toolbar)
5. [Styling](#5-styling)
6. [Utility Functions](#6-utility-functions)
7. [Backend Integration](#7-backend-integration)
8. [Adding New Features](#8-adding-new-features)

---

## **1. Overview**
The `gui.py` file is the frontend of the ABAC Lab application. It connects the GUI components to the backend logic. The application is structured into 6 main pages:

1. Policy Manager  
2. Analysis  
3. Data Conversion  
4. Log Generator  
5. Demos  
6. Help & Support

---

## **2. Key Components**

### **2.1 Imports**  
<details>
<summary>Click to expand PyQt5 import details</summary>

#### **Standard Library Imports**
- `sys`, `os`, `webbrowser`

#### **PyQt5 Imports**
- From `QtWidgets`: `QMainWindow`, `QPushButton`, `QVBoxLayout`, etc.
- From `QtGui`: `QIcon`, `QPixmap`, `QFontMetrics`, etc.
- From `QtCore`: `Qt`, `QUrl`, `QSize`, etc.

</details>

#### **Backend Imports**
Key backend modules include:
- `core.myabac`: parsing `.abac` files
- `features.log_generation`, `features.analysis`, `features.conversion`, etc.

---

### **2.2 DragDropUpload Class**
Custom widget for drag-and-drop or dialog-based upload of `.abac` files.  
Handles events like `dragEnterEvent`, `dropEvent`, and `mousePressEvent`.

---

### **2.3 MyApp Class**
Main window (`QMainWindow`) for the application using `QStackedWidget` to manage multiple pages.  
Tracks state for uploaded files and parsed policy data.

---

## **3. Application Pages**

Each page serves a distinct function in the application:

### **Page 1: Policy Manager**
- **Purpose**: Upload and manage `.abac` policy files.
- **Key Widgets**: `DragDropUpload`, `QListWidget`, `QPushButton`
- **Layout**: Vertical layout with a header, upload area, file list, and clear button.

### **Page 2: Analysis**
- **Purpose**: Perform access checks, show graphs/stats, and analyze rules.
- **Key Widgets**: `QPushButton`, `QScrollArea`
- **Layout**: Horizontal layout for analysis tools, results shown below.

### **Page 3: Data Conversion**
- **Purpose**: Convert policies to CSV or export them as dictionaries.
- **Key Widgets**: `QComboBox`, `QPushButton`
- **Layout**: Grid layout for file selection and actions.

### **Page 4: Log Generator**
- **Purpose**: Generate synthetic access logs.
- **Key Widgets**: `QLineEdit`, `QPushButton`
- **Layout**: Grid layout for input and submit controls.

### **Page 5: Demos**
- **Purpose**: Provide tutorial/demo access.
- **Key Widgets**: `QLabel`, `QPushButton`
- **Layout**: Vertical card-style layout.

### **Page 6: Help & Support**
- **Purpose**: FAQs, bug reports, and contact info.
- **Key Widgets**: `QScrollArea`, `QPushButton`
- **Layout**: Vertical layout for text and links.

---

## **4. Toolbar**

- **Purpose**: Navigation between pages
- **Components**:
  - `QToolBar`: vertical bar for buttons
  - `QAction`: icons linked to pages
- **Methods**:
  - `add_toolbar_actions`, `reset_toolbar_icons`, `switch_page`
- **Icons**: Default and active versions stored in `self.default_icons` and `self.active_icons`.

---

## **5. Styling**

- **Purpose**: Maintain consistent UI design
- **Implementation**: 
  - `apply_stylesheet` method applies the theme
- **Key Styles**:
  - Toolbar: Dark blue background, white text
  - Buttons: Rounded with hover effects
  - Scroll Areas: White background, black text

---

## **6. Utility Functions**

### `resource_path`
- **Purpose**: Resolves resource file paths, especially for PyInstaller builds.
- **Usage**: Ensures icons/images load correctly across platforms.

---

## **7. Backend Integration**

Frontend connects to core logic via:
- **File Parsing**: `parse_abac_file`
- **Log Generation**: `generate_logs`
- **Conversion**: `convert_uploaded_file`, `export_as_python_dict`
- **Analysis**: `show_permissions`, `show_bar_graph`, `show_heatmap`, `show_rulevu`, etc.
- **Precomputations**: `precompute_all_stats`, `precompute_bar_graphs`, `precompute_permstats`

---

## **8. Adding New Features**

This section provides a step-by-step guide to adding a new feature to the ABAC Lab application, including backend logic, page/widget creation, and toolbar integration with custom icons.

---

### **Step 1: Add Backend Logic**
- Create a Python function or module under the appropriate `features/` subdirectory.
- Implement the core functionality. For example:
  - For analysis features: add it to `features.analysis`
  - For conversions: use `features.conversion`

---

### **Step 2: Create a Page or Widget**

#### If the feature is a new page:
1. Create a new `QWidget` in the `MyApp` class.
2. Initialize it in the `initUI` method (e.g., `self.init_new_feature_page()`).
3. Add it to the stacked layout:
   ```python
   self.stacked_widget.addWidget(new_feature_widget)

---
### **Step 3: Add a Toolbar Icon**

#### To add a new toolbar icon for the feature:
1. Place the icon in the `res` folder:
- Save your `.png` file in the `res` folder. For example, name it `new_feature.png` for the default icon and `new_feature_active.png` for the active icon.
2. Update the `default_icons` and `active_icons` Dictionaries:
- Add entries for the new feature in the `add_toolbar_actions` method of the `MyApp` class:
```python
self.default_icons["new_feature"] = QIcon(resource_path("res/new_feature.png"))
self.active_icons["new_feature"] = QIcon(resource_path("res/new_feature_active.png"))
```
3. Create a New `QAction` for the Toolbar:
- Add a new action for the feaature in the `toolbar_actions` dictionary:
```python
   self.toolbar_actions["new_feature"] = QAction(self.default_icons["new_feature"], "New Feature", self)
```
4. Connect the Action to the Feature:
- Link the action to a method that switches to the new page or triggers the feature:
```python
  self.toolbar_actions["new_feature"].triggered.connect(lambda: self.show_new_feature_page())
```
5. Add the Action to the Toolbar:
- Add the action to the toolbar in the `add_toolbar_actions` method:
```python
  self.toolbar.addAction(self.toolbar_actions["new_feature"])
```
---
### **Step 4: Implement the Page-Switching Method**
- Create a method in the `MyApp` class to switch to the new page:
```python
  def show_new_feature_page(self):
    self.switch_page(page_index, "new_feature")
```
Replace `page_index` with the index of the new page in the `QStackedWidget`.

---
### **Step 5: Test the Feature**
- Run the application and verify that the new toolbar icon appears and functions correctly.
- Ensure the icon changes to the active version when the page is selected.
---
**Example**

If you want to add a "Settings" page with a toolbar icon:
1. Save `settings.png` and `settings_active.png`
2. Update the `default_icons` and `active_icons` dictionaries:

```python
self.default_icons["settings"] = QIcon(resource_path("res/settings.png"))
self.active_icons["settings"] = QIcon(resource_path("res/seetings_active.png"))
```
3. Add a new `QAction`:
```python
self.toolbar_actions["settings"] = QAction(self.default_icons["settings"], "Settings", self)
```
4. Connect the action to a method:
```python
self.toolbar_actions["settings"].triggered.connect(lambda: self.show_settings_page())
```
5. Add the action to the toolbar:
```python
self.toolbar.addAction(self.toolbar_actions["settings"])
```
6. Create the `show_settings_page` method:
```python
def show_settings_page(self):
  self.switch_page(6, "settings") # Assuming the page index is 6
```