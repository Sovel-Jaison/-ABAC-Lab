import sys
import os  # Used to get file basenames
import webbrowser # Python’s standard library, it doesn't need to be added to requirements.txt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QAction, QMessageBox, QStackedWidget, QLabel, QToolBar,
    QSizePolicy, QScrollArea, QComboBox, QGridLayout, QListWidget, QListWidgetItem, QSpacerItem, QLineEdit, QToolButton, QSizePolicy, QFrame, QLayout, QProgressDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator, QFontMetrics, QDesktopServices
from PyQt5.QtCore import Qt, QSize, QUrl
# Import backend functions (ensure myabac.py is importable as a module)
from core.myabac import parse_abac_file
from features.log_generation.log_generation import generate_logs
from features.conversion.conv import SingleFileUpload, convert_uploaded_file
from features.conversion.serialization.serialization import export_as_python_dict
from features.analysis.permissions.access_perms import (
    show_permissions, on_file_dropdown_changed,
    update_displayed_results, save_permissions_to_file, compute_abac_stats,
    update_sorted_permissions
)
from features.analysis.bar_graph import show_bar_graph, initialize_bar_graph_cache, precompute_bar_graphs
from features.analysis.permissions.manual_perms import show_manual_check, save_manual_check_results, save_manual_check_page_results, set_manual_page, on_manual_page_input
from features.analysis.heatmap import show_heatmap, precompute_heatmaps
from features.analysis.abac_stats import show_stats, save_abac_stats, precompute_all_stats
from features.analysis.permissions.rule_perms import on_permstats_file_dropdown_changed, show_rulevu, show_permstats, initialize_permstats_cache, precompute_permstats

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller. """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class DragDropUpload(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setFixedSize(500, 200)
        self.setStyleSheet(
            """
            background-color: transparent;
            color: black;
            border: 5px dashed black;
            border-radius: 5px;
            padding: 20px;
            font-size: 16px;
            text-align: center;
            """)
        layout = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: black;")
        image_path = resource_path("res/upload_b.png")
        self.label.setText(
            f"""
            <div style="text-align: center;">
                <img src='{image_path}' width='50' height='50'><br>
                <span style="font-size: 24px;">Upload File</span><br>
                <span style="font-size: 16px;">Click to browse or drag & drop files here</span>
            </div>
            """)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.endswith('.abac'):
                    self.main_window.handle_file_upload(file_path)
                else:
                    QMessageBox.warning(self.main_window, "Invalid File", "Please upload a .abac file.")


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            options = QFileDialog.Options()
            file_names, _ = QFileDialog.getOpenFileNames(
                self,
                "Select ABAC Policy Files",
                "",
                "Policy Files (*.abac);;All Files (*)",
                options=options,
            )
            if file_names:
                for file_name in file_names:
                    if file_name.endswith('.abac'):
                        self.main_window.handle_file_upload(file_name)
                    else:
                        QMessageBox.warning(self.main_window, "Invalid File", "Please upload a .abac file.")


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.abac_data = {}
        self.uploaded_files = []
        self.permissions_results = {}
        self.heatmap_cache = {}
        self.current_abac_path = None
        self.current_manual_abac = None   # <-- Initialize here
        initialize_bar_graph_cache(self)
        initialize_permstats_cache(self)  # Initialize cache
        self.initUI()

    def open_bug_form(self):
        """Opens the Google Form for bug reporting."""
        webbrowser.open("https://forms.gle/34brscir1o13jyJk9")  # Your Google Form link

    def create_faq(self, question_text, answer_text):
        faq_widget = QWidget()
        faq_layout = QVBoxLayout(faq_widget)
        faq_layout.setSpacing(5)
        faq_layout.setContentsMargins(0, 0, 0, 0)

        question_button = QToolButton()
        question_button.setText(f"❓ {question_text}")
        question_button.setCheckable(True)
        question_button.setChecked(False)
        question_button.setStyleSheet("""
            QToolButton {
                font-size: 20px;
                text-align: left;
                padding: 8px;
                border: none;
                color: #003366;
                font-weight: bold;
            }
            QToolButton::checked {
                color: #000000;
            }
        """)
        question_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        question_button.setArrowType(Qt.DownArrow)
        question_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Answer box
        answer_frame = QFrame()
        answer_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #003366;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        answer_frame.setVisible(False)
        answer_frame.setMaximumWidth(800)
        answer_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        answer_label = QLabel(answer_text)
        answer_label.setWordWrap(True)
        answer_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        answer_label.setStyleSheet("""
            font-size: 18px;
            color: black;
            background: transparent;
            border: none;
        """)
        answer_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        answer_label.setMinimumWidth(760)
        answer_label.setMaximumWidth(760)
        font_metrics = QFontMetrics(answer_label.font())
        text_rect = font_metrics.boundingRect(
            0, 0, answer_label.width() - 20, 1000, 
            Qt.TextWordWrap, answer_text
        )
        answer_label.setMinimumHeight(text_rect.height() + 20)

        answer_layout = QVBoxLayout()
        answer_layout.setContentsMargins(0, 0, 0, 0)
        answer_layout.addWidget(answer_label)
        answer_layout.setSizeConstraint(QLayout.SetFixedSize)
        answer_frame.setLayout(answer_layout)

        # Toggle logic
        def toggle_answer():
            is_expanded = question_button.isChecked()
            question_button.setArrowType(Qt.UpArrow if is_expanded else Qt.DownArrow)
            answer_frame.setVisible(is_expanded)
            QApplication.processEvents() 
            
        question_button.clicked.connect(toggle_answer)

        faq_layout.addWidget(question_button)
        faq_layout.addWidget(answer_frame)

        return faq_widget

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setOrientation(Qt.Vertical)
        self.add_toolbar_actions()
        self.stacked_widget = QStackedWidget()
        # Create pages
        self.page1 = QWidget()  # Policy Page
        self.page2 = QWidget()  # Analysis Page
        self.page3 = QWidget()  # Conversion Page
        self.page4 = QWidget()  # Log Page
        self.page5 = QWidget()  # Demos
        self.page6 = QWidget()  # Help & Support

        # ------------------------
        # Set up page 1 (Policy Page)
        page1_layout = QVBoxLayout()
        page1_label = QLabel("Policy Manager")
        page1_label.setAlignment(Qt.AlignCenter)
        page1_label.setStyleSheet("font-size: 30px; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
        page1_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        page1_label.setContentsMargins(20, 20, 20, 20)
        page1_layout.addWidget(page1_label)
        page1_layout.addStretch()

        # Drag and Drop Upload Button
        button_layout = QVBoxLayout()
        button_layout.addStretch()

        self.page1_sub_label = QLabel("Please start by uploading a .abac file")
        self.page1_sub_label.setAlignment(Qt.AlignCenter)
        self.page1_sub_label.setStyleSheet("font-size: 18px; color: black;")
        self.page1_sub_label.setMaximumWidth(400)
        button_layout.addWidget(self.page1_sub_label, alignment=Qt.AlignCenter)

        self.upload_btn = DragDropUpload(self.page1, main_window=self)
        self.upload_btn.setFixedSize(500, 200)
        button_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        button_layout.addStretch()
        page1_layout.addLayout(button_layout)
        page1_layout.addStretch()

        # Label for "Uploaded Files"
        self.uploaded_file_label = QLabel("Uploaded Files:", self.page1)
        self.uploaded_file_label.setAlignment(Qt.AlignCenter)
        self.uploaded_file_label.setStyleSheet("font-size: 20px; color: black;")
        page1_layout.addWidget(self.uploaded_file_label)

        # Layout for individual file buttons
        self.file_list_widget = QListWidget(self.page1)
        self.file_list_widget.setStyleSheet("QListWidget { background-color: white; }")
        page1_layout.addWidget(self.file_list_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.clear_files_button = QPushButton("Clear Files", self.page1)
        self.clear_files_button.setFixedSize(150, 40)
        self.clear_files_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)

        self.clear_files_button.clicked.connect(self.clear_uploaded_files)
        self.clear_files_button.hide()
        buttons_layout.addWidget(self.clear_files_button)
        buttons_layout.addStretch()
        page1_layout.addLayout(buttons_layout)
        self.page1.setLayout(page1_layout)

        # ------------------------
        # Set up page 2 (Analysis)
        self.page2_layout = QVBoxLayout()
        self.page2_label = QLabel("Analysis Page")
        self.page2_label.setAlignment(Qt.AlignCenter)
        self.page2_label.setStyleSheet("font-size: 30px; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
        self.page2_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.page2_label.setContentsMargins(20, 20, 20, 20)
        self.page2_layout.addWidget(self.page2_label, alignment=Qt.AlignTop)

        # Create main horizontal layout
        column_widget = QWidget()
        column_layout = QHBoxLayout()

        # Permissions Column
        self.perm_widget = QWidget()
        perm_layout = QVBoxLayout(self.perm_widget)
        self.perm_widget.setFixedSize(240, 400)
        self.perm_widget.setStyleSheet("border-radius: 5px; padding: 0px; border: 2px solid #003366;")
        perm_layout.setContentsMargins(10, 10, 10, 10)
        self.permissions_lbl = QLabel("Access evaluation helps identify which subjects have access to which resources. "
        "This information helps identify any unauthorized access and ensure the integrity of the policies."
        "Users can see who has access to which resources and make necessary adjustments to their policies.")
        self.permissions_lbl.setWordWrap(True)
        self.permissions_lbl.setFixedWidth(220)
        self.permissions_lbl.setStyleSheet("font-size: 14px; color: black; border: none;")
        perm_layout.addWidget(self.permissions_lbl, alignment=Qt.AlignTop)

        self.perm_btn = QPushButton("Access Evaluation", self.page2)
        self.perm_btn.setFixedSize(200, 40)
        self.perm_btn.setStyleSheet("border: none;")
        perm_layout.addWidget(self.perm_btn, alignment=Qt.AlignHCenter | Qt.AlignTop)
        column_layout.addWidget(self.perm_widget)

        # Bar Graph Column
        self.bar_graph_widget = QWidget()
        bar_graph_layout = QVBoxLayout(self.bar_graph_widget)
        self.bar_graph_widget.setFixedSize(240, 400)
        self.bar_graph_widget.setStyleSheet("border-radius: 5px; padding: 0px; border: 2px solid #003366;")
        bar_graph_layout.setContentsMargins(10, 10, 10, 10)
        self.bar_grph_lbl = QLabel("The bar graph helps identify which top 10 resources are accessed the most and least. "
        "This information helps for understanding how permissions are distributed across subjects and resources.")
        self.bar_grph_lbl.setWordWrap(True)
        self.bar_grph_lbl.setFixedWidth(220)        
        self.bar_grph_lbl.setStyleSheet("font-size: 14px; color: black; border: none;")
        bar_graph_layout.addWidget(self.bar_grph_lbl, alignment=Qt.AlignTop)

        self.bar_graph_btn = QPushButton("Resource Access", self.page2)
        self.bar_graph_btn.setFixedSize(200, 40)
        self.bar_graph_btn.setStyleSheet("border: none;")
        bar_graph_layout.addWidget(self.bar_graph_btn, alignment=Qt.AlignHCenter | Qt.AlignTop)
        column_layout.addWidget(self.bar_graph_widget)

        #Stats Container (Middle Column)
        self.stats_widget = QWidget()
        self.stats_widget.setFixedSize(400, 400)
        self.stats_widget.setStyleSheet("border-radius: 5px; padding: 0px; border: 2px solid #003366;")

        # Layout for stats_widget
        stats_widget_layout = QVBoxLayout()
        stats_widget_layout.setContentsMargins(10, 10, 10, 10)
        self.stats_widget.setLayout(stats_widget_layout)
        
        # Make a child widget
        self.stats_container = QWidget()
        self.stats_container_layout = QVBoxLayout()
        self.stats_container.setFixedWidth(400)  # Set a fixed width for the container
        self.stats_container.setStyleSheet("border: none;")
        self.stats_container.setLayout(self.stats_container_layout)

        stats_widget_layout.addWidget(self.stats_container)
        # Add a Save button below the stats container
        self.save_stats_btn = QPushButton("Save Stats")
        self.save_stats_btn.setFixedSize(200, 40)
        self.save_stats_btn.setStyleSheet("border: none;")
        self.save_stats_btn.clicked.connect(lambda: save_abac_stats(self, self.current_abac_path))  # Connect to save function
        stats_widget_layout.addWidget(self.save_stats_btn, alignment=Qt.AlignCenter)
        column_layout.addWidget(self.stats_widget)

        # Rule Analysis Column
        self.rule_widget = QWidget()
        rule_layout = QVBoxLayout(self.rule_widget)
        self.rule_widget.setFixedSize(240, 400)
        self.rule_widget.setStyleSheet("border-radius: 5px; padding: 0px; border: 2px solid #003366;")
        rule_layout.setContentsMargins(10, 10, 10, 10)
        self.rule_perm_lbl = QLabel(
            "The rule analysis helps identify how many permissions are granted by each rule."
            "It provides insights into potential unauthorized access and ensures policy integrity."
            "These tools are essential for maintaining access control policies for your given .abac file.")
        self.rule_perm_lbl.setWordWrap(True)
        self.rule_perm_lbl.setFixedWidth(220)
        self.rule_perm_lbl.setStyleSheet("font-size: 14px; color: black; border: none;")
        rule_layout.addWidget(self.rule_perm_lbl, alignment=Qt.AlignTop)

        self.rule_perm_btn = QPushButton("Rule Analysis", self.page2)
        self.rule_perm_btn.setFixedSize(200, 40)
        self.rule_perm_btn.setStyleSheet("border: none;")
        rule_layout.addWidget(self.rule_perm_btn, alignment=Qt.AlignHCenter | Qt.AlignTop)
        column_layout.addWidget(self.rule_widget)

        # Heat Map Column
        self.heat_map_widget = QWidget()
        heat_map_layout = QVBoxLayout(self.heat_map_widget)
        self.heat_map_widget.setFixedSize(240, 400)
        self.heat_map_widget.setStyleSheet("border-radius: 5px; padding: 0px; border: 2px solid #003366;")
        heat_map_layout.setContentsMargins(10, 10, 10, 10)
        self.heat_map_lbl = QLabel("The heatmap displays the frequency of attribute usage across various rules. "
        "This information helps for identifying patterns and trends in policies, which helps for potential gaps or redundancies in the policy.")
        self.heat_map_lbl.setWordWrap(True)
        self.heat_map_lbl.setFixedWidth(220)
        self.heat_map_lbl.setStyleSheet("font-size: 14px; color: black; border: none;")
        heat_map_layout.addWidget(self.heat_map_lbl, alignment=Qt.AlignTop)

        self.heatmap_btn_page2 = QPushButton("Attribute Usage", self.page2)
        self.heatmap_btn_page2.setFixedSize(200, 40)
        self.heatmap_btn_page2.setStyleSheet("border: none;")
        heat_map_layout.addWidget(self.heatmap_btn_page2, alignment=Qt.AlignHCenter | Qt.AlignTop)
        column_layout.addWidget(self.heat_map_widget)

        # Add the columns layout to the main layout
        self.page2_layout.addLayout(column_layout)

        # Container for results area
        self.results_area_container = QWidget()
        self.results_area_layout = QVBoxLayout(self.results_area_container)

        # Scroll area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)
        self.results_area_layout.addWidget(self.scroll_area)
        self.scroll_area.hide()

        self.page2_layout.addWidget(column_widget, alignment=Qt.AlignCenter)
        self.page2_layout.addWidget(self.results_area_container)

        self.page2.setLayout(self.page2_layout)

        # Connect button signals 
        """Fix buttons"""
        self.perm_btn.clicked.connect(self.show_permissions_choice)
        self.bar_graph_btn.clicked.connect(self.show_bar_graph)
        self.heatmap_btn_page2.clicked.connect(self.show_heatmap)
        self.rule_perm_btn.clicked.connect(self.show_rule_choices)

        # Set the layout for page 2
        self.page2.setLayout(self.page2_layout)

        # ------------------------
        # Set up page 3 (Convert CSV to ABAC)
        self.page3_layout = QVBoxLayout()
        self.page3_label = QLabel("Data Conversion")
        self.page3_label.setAlignment(Qt.AlignCenter)
        self.page3_label.setStyleSheet("font-size: 30px; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
        self.page3_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.page3_label.setContentsMargins(20, 20, 20, 20)
        self.page3_layout.addWidget(self.page3_label) 

        self.page3_grid_layout = QGridLayout()
        self.page3_grid_layout.setRowStretch(0, 1)

        # Add label for the dropdown menu
        self.page3_file_label = QLabel("Select an uploaded abac file to convert to CSV or export as Python dictionary:")
        self.page3_file_label.setAlignment(Qt.AlignCenter)
        self.page3_file_label.setStyleSheet("font-size: 18px; color: black")
        self.page3_grid_layout.addWidget(self.page3_file_label, 1, 0, alignment=Qt.AlignCenter)

        # Create a vertical layout for the dropdown menu and the button
        self.dropdown_button_layout = QVBoxLayout()
        
        # Add dropdown menu (QComboBox)
        self.page3_current_uploaded_files = QComboBox()
        self.page3_current_uploaded_files.adjustSize()
        self.page3_current_uploaded_files.setFixedSize(200, 40)
        self.page3_current_uploaded_files.setStyleSheet("font-size: 16px; color: black; border: 2px solid black;")
        self.dropdown_button_layout.addWidget(self.page3_current_uploaded_files, alignment=Qt.AlignCenter)

        self.dropdown_button_layout.addSpacerItem(QSpacerItem(20, 40))
        
        # Create horizontal layout for two buttons
        self.conversion_button_hlayout = QHBoxLayout()
        
        # Add "Convert to CSV" button
        self.conv_uploaded_abac_btn = QPushButton("Convert to CSV", self.page3)
        self.conv_uploaded_abac_btn.setFixedSize(200, 50)
        self.conv_uploaded_abac_btn.setStyleSheet("font-size: 18px; color: white;")
        self.conv_uploaded_abac_btn.clicked.connect(lambda: convert_uploaded_file(self))
        self.conversion_button_hlayout.addWidget(self.conv_uploaded_abac_btn, alignment=Qt.AlignCenter)

        # Add "Export as Python Dictionary" button
        self.export_dict_btn = QPushButton("Export Policy Data", self.page3)
        self.export_dict_btn.setFixedSize(200, 50)
        self.export_dict_btn.setStyleSheet("font-size: 18px; color: white;")
        self.export_dict_btn.clicked.connect(lambda: export_as_python_dict(self))
        self.conversion_button_hlayout.addWidget(self.export_dict_btn, alignment=Qt.AlignCenter)

        # Add the horizontal layout to the vertical layout
        self.dropdown_button_layout.addLayout(self.conversion_button_hlayout)
        
        # Add the vertical layout to the grid layout
        self.page3_grid_layout.addLayout(self.dropdown_button_layout, 2, 0, alignment=Qt.AlignCenter)

        # Add a spacer item to create space between the dropdown menu and the button
        self.page3_grid_layout.setRowStretch(3, 1)

        self.page3_convert_label = QLabel("Or upload a new abac policy file to convert to CSV:")
        self.page3_convert_label.setAlignment(Qt.AlignCenter)
        self.page3_convert_label.setStyleSheet("font-size: 18px; color: black;")
        self.page3_grid_layout.addWidget(self.page3_convert_label, 4, 0, alignment=Qt.AlignCenter)

        # Add the lowest button
        self.upload_abac_btn = SingleFileUpload(self.page3, main_window=self)
        self.page3_grid_layout.addWidget(self.upload_abac_btn, 5, 0, alignment=Qt.AlignCenter)
        self.page3_grid_layout.setRowStretch(6, 1)

        self.page3_layout.addLayout(self.page3_grid_layout)
        self.page3.setLayout(self.page3_layout)

        # ------------------------
        # Set up page 4 (Logs)
        self.page4_layout = QVBoxLayout()
        self.page4_label = QLabel("Log Generator")
        self.page4_label.setAlignment(Qt.AlignCenter)
        self.page4_label.setStyleSheet("font-size: 30px; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
        self.page4_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.page4_label.setContentsMargins(20, 20, 20, 20)
        self.page4_layout.addWidget(self.page4_label) 
        
        self.page4_grid_layout = QGridLayout()
        
        self.page4_grid_layout.setRowStretch(0, 1)
        self.page4_grid_layout.setRowStretch(1, 1)
        self.page4_grid_layout.setRowStretch(2, 1)
        
        # Add description labelfor generator page
        self.page4_generator_description = QLabel(
            "The log generator allows users to create a specified number of log entries for testing and analysis. "
            "Users can define the number of entries and optionally set the percentage of 'allow' decisions. "
            "This feature helps simulate real-world access control scenarios to evaluate policy effectiveness and identify potential issues.")
        
        self.page4_generator_description.setStyleSheet("font-size: 18px; color: black; border: none;")
        self.page4_generator_description.setWordWrap(True)
        self.page4_generator_description.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.page4_generator_description.setFixedSize(800, 100)
        
        self.page4_grid_layout.addWidget(self.page4_generator_description, 1, 0, alignment=Qt.AlignCenter | Qt.AlignTop)
        
        self.page4_grid_layout.setRowStretch(2, 0)

        # Add label for number of log entry
        self.page4_generator_label = QLabel("Enter the desired amount of logs to be generated:")
        self.page4_generator_label.setAlignment(Qt.AlignCenter)
        self.page4_generator_label.setStyleSheet("font-size: 18px; color: black; background-color: white;")
        self.page4_grid_layout.addWidget(self.page4_generator_label, 3, 0, alignment=Qt.AlignCenter)
        
        self.page4_current_uploaded_files = QComboBox()
        self.page4_current_uploaded_files.adjustSize()
        self.page4_current_uploaded_files.setStyleSheet("font-size: 14px; color: black; border: 2px solid black; background-color: white;")
        self.page4_current_uploaded_files.setFixedSize(200, 40)
        self.page4_grid_layout.addWidget(self.page4_current_uploaded_files, 4, 0, alignment=Qt.AlignCenter)
        
        self.page4_inputs_vlayout = QVBoxLayout()

        # Number of entries
        self.page4_integer_label = QLabel("Number of entries (Required):")
        self.page4_integer_label.setStyleSheet("font-size: 15px; color: black;")
        self.page4_inputs_vlayout.addWidget(self.page4_integer_label, alignment=Qt.AlignCenter)
        self.page4_integer_text_edit = QLineEdit(self)
        self.page4_integer_text_edit.setFixedSize(200, 20)
        self.page4_integer_text_edit.setValidator(QIntValidator())
        self.page4_integer_text_edit.setPlaceholderText("e.g. 1000")
        self.page4_integer_text_edit.setToolTip("Enter the number of total entries. This field is required.")
        self.page4_integer_text_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }                                       
        """)
        self.page4_inputs_vlayout.addWidget(self.page4_integer_text_edit, alignment=Qt.AlignCenter)

        spacer = QWidget()
        spacer.setFixedHeight(10)
        self.page4_inputs_vlayout.addWidget(spacer)
        
        # Percentage of permits
        self.page4_percentage_label = QLabel("Percentage of permits (Optional):")
        self.page4_percentage_label.setStyleSheet("font-size: 15px; color: black;")
        self.page4_inputs_vlayout.addWidget(self.page4_percentage_label, alignment=Qt.AlignCenter)
        self.page4_percentage_text_edit = QLineEdit(self)
        self.page4_percentage_text_edit.setFixedSize(200, 20)
        self.page4_percentage_text_edit.setValidator(QIntValidator())
        self.page4_percentage_text_edit.setPlaceholderText("e.g. 70")
        self.page4_percentage_text_edit.setToolTip("Enter the percentage of permits. This field is optional.")
        self.page4_percentage_text_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }                                       
        """)
        self.page4_inputs_vlayout.addWidget(self.page4_percentage_text_edit, alignment=Qt.AlignCenter)

        # Percentage of over permits
        self.page4_over_percentage_label = QLabel("Percentage of over permits (Optional):")
        self.page4_over_percentage_label.setStyleSheet("font-size: 15px; color: black;")
        self.page4_inputs_vlayout.addWidget(self.page4_over_percentage_label, alignment=Qt.AlignCenter)
        self.page4_over_percentage_text_edit = QLineEdit(self)
        self.page4_over_percentage_text_edit.setFixedSize(200, 20)
        self.page4_over_percentage_text_edit.setValidator(QIntValidator())
        self.page4_over_percentage_text_edit.setPlaceholderText("e.g. 5")
        self.page4_over_percentage_text_edit.setToolTip("Enter the percentage of over permits. This field is optional.")
        self.page4_over_percentage_text_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }  
        """)
        self.page4_inputs_vlayout.addWidget(self.page4_over_percentage_text_edit, alignment=Qt.AlignCenter)

        # Percentage of under permits
        self.page4_under_percentage_label = QLabel("Percentage of under permits (Optional):")
        self.page4_under_percentage_label.setStyleSheet("font-size: 15px; color: black;")
        self.page4_inputs_vlayout.addWidget(self.page4_under_percentage_label, alignment=Qt.AlignCenter)
        self.page4_under_percentage_text_edit = QLineEdit(self)
        self.page4_under_percentage_text_edit.setFixedSize(200, 20)
        self.page4_under_percentage_text_edit.setValidator(QIntValidator())
        self.page4_under_percentage_text_edit.setPlaceholderText("e.g. 5")
        self.page4_under_percentage_text_edit.setToolTip("Enter the percentage of under permits. This field is optional.")
        self.page4_under_percentage_text_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid black; 
            }
            QLineEdit::placeholder {
                color: gray;            
            }  
        """)
        self.page4_inputs_vlayout.addWidget(self.page4_under_percentage_text_edit, alignment=Qt.AlignCenter)

        # Widget to hold the vertical layout
        page4_inputs_widget = QWidget()
        page4_inputs_widget.setLayout(self.page4_inputs_vlayout)
        self.page4_grid_layout.addWidget(page4_inputs_widget, 5, 0, alignment=Qt.AlignCenter)
        # --- End: Stack text edits vertically with labels ---

        # Add button to submit numbers
        self.page4_submit_btn = QPushButton("Submit", self)
        self.page4_submit_btn.clicked.connect(lambda: generate_logs(self))
        self.page4_grid_layout.addWidget(self.page4_submit_btn, 6, 0, alignment=Qt.AlignCenter)
        self.page4_grid_layout.setRowStretch(7, 1)
        self.page4_layout.addLayout(self.page4_grid_layout)
        self.page4_layout.addStretch()
        self.page4.setLayout(self.page4_layout)

        # ------------------------
        # Set up page 5 (Demos)

        self.page5_layout = QVBoxLayout()
        self.page5_label = QLabel("Demos")
        self.page5_label.setAlignment(Qt.AlignCenter)
        self.page5_label.setStyleSheet("font-size: 30px; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
        self.page5_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.page5_label.setContentsMargins(20, 20, 20, 20)
        self.page5_layout.addWidget(self.page5_label, alignment=Qt.AlignTop)
        self.page5_layout.addStretch(1)

        # Title
        demo_title = QLabel("Interactive Demo")
        demo_title.setAlignment(Qt.AlignCenter)
        demo_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #003366; padding-bottom: 10px; border: none;")

        # Description
        demo_desc = QLabel("Watch this video to learn how to use ABAC Lab’s features, including policy uploading, analysis, and log generation.")
        demo_desc.setWordWrap(True)
        demo_desc.setAlignment(Qt.AlignCenter)
        demo_desc.setStyleSheet("font-size: 18px; color: black; padding: 10px;")

        # Thumbnail image
        demo_image = QLabel()
        demo_image.setPixmap(QPixmap(resource_path("res/demo_thumbnail.png")).scaled(600, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        demo_image.setAlignment(Qt.AlignCenter)
        demo_image.setStyleSheet("border: none;")

        # Demo button
        btn = QPushButton("▶ Watch Demo Video")
        btn.setFixedSize(260, 50)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #005F9E;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://youtu.be/KtmSem5jK-A")))

        # Wrap content in a styled card
        card = QWidget()
        card.setFixedWidth(700)
        card.setStyleSheet("""
            background-color: white;
            border: 3px solid #003366;
            border-radius: 15px;
            padding: 30px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)
        card_layout.addWidget(demo_title)
        card_layout.addWidget(demo_desc)
        card_layout.addWidget(demo_image)
        card_layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.page5_layout.addWidget(card, alignment=Qt.AlignCenter)

        self.page5_layout.addStretch(2)

        self.page5.setLayout(self.page5_layout)

        # ------------------------
        # Set up page 6 (Help & Support)
        self.page6_layout = QVBoxLayout()
        self.page6.setLayout(self.page6_layout)

        # Header label
        self.page6_label = QLabel("Help & Support")
        self.page6_label.setAlignment(Qt.AlignCenter)
        self.page6_label.setStyleSheet("font-size: 30px; color: white; background-color: #003366; padding: 5px; border-radius: 5px;")
        self.page6_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.page6_label.setContentsMargins(20, 20, 20, 20)
        self.page6_layout.addWidget(self.page6_label, alignment=Qt.AlignTop)

        # FAQ title
        faq_title = QLabel("FAQ")
        faq_title.setAlignment(Qt.AlignLeft)
        faq_title.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #003366;
            margin-top: 20px;
        """)
        self.page6_layout.addWidget(faq_title)

        # Scrollable FAQ
        faq_scroll = QScrollArea()
        faq_scroll.setWidgetResizable(True)
        faq_widget = QWidget()
        faq_widget.setStyleSheet("background-color: white;")
        faq_layout = QVBoxLayout(faq_widget)
        faq_layout.setSpacing(10)

        # Add FAQ items
        faq_items = [
            self.create_faq(
                "What if I don't have a policy, but I want to find out how the application works?",
                "In this application, we provide demo datasets so you can explore and experience how the application works even if you don't have a policy file."
            ),
            self.create_faq(
                "Can I export the results of my analysis?",
                "On the Analysis page, each feature includes options to export results. This includes Access Evaluation, Resource Access, Rule Analysis, Attribute Usage, and Stats. Some sections use a 'Save' button, while visualizations like bar graphs and heatmaps have a print icon in the toolbar. When you export your results, the file will also include the name of the ABAC policy used during the analysis."
            ),
            self.create_faq(
                "How do I validate that the policy I'm analyzing is functioning correctly?",
                "Use the Access Evaluation and Rule Analysis tools to simulate access requests. These features help you verify whether the intended access decisions match your policy design."
            ),
            self.create_faq(
                "What are the limitations of this tool?",
                "This tool is focused on policy modeling, evaluation, and visualization. It is not a runtime access decision engine or a replacement for real-time enforcement systems. It also assumes that data inputs are well-formed and validated."
            ),
            self.create_faq(
                "How can I understand what each policy rule is doing?",
                "Rule Analysis breaks down how many permissions each rule grants and which ones. You can also import a custom rule file to evaluate it against the attribute data and see how it performs. This helps you fine-tune and audit your rule set."
            )
        ]
        for faq in faq_items:
            faq_layout.addWidget(faq)

        faq_scroll.setWidget(faq_widget)
        self.page6_layout.addWidget(faq_scroll)

        # Bottom Row with Bug Report, Publication Link, and Version Info
        bottom_row = QHBoxLayout()

        # Left: Bug and Contact Info
        bug_contact_layout = QVBoxLayout()
        bug_contact_layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        report_bug_btn = QPushButton("Report a Bug")
        report_bug_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                padding: 16px;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)

        report_bug_btn.setFixedSize(240, 60)
        report_bug_btn.clicked.connect(self.open_bug_form)

        contact_label = QLabel("Need more help? Contact us at:")
        contact_label.setStyleSheet("font-size: 20px; color: black;")

        email_layout = QHBoxLayout()
        contact_icon = QLabel()
        contact_icon.setPixmap(QPixmap(resource_path("res/email_icon.png")).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        contact_icon.setFixedSize(24, 24)

        contact_email = QLabel('<a href="mailto:abaclab.research@gmail.com">abaclab.research@gmail.com</a>')
        contact_email.setOpenExternalLinks(True)
        contact_email.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #003366;
            text-decoration: none;
        """)

        email_layout.addWidget(contact_icon)
        email_layout.addSpacing(10)
        email_layout.addWidget(contact_email)

        bug_contact_layout.addWidget(report_bug_btn)
        bug_contact_layout.addSpacing(10)
        bug_contact_layout.addWidget(contact_label)
        bug_contact_layout.addLayout(email_layout)

        # Center: Publication Link
        publication_layout = QVBoxLayout()
        publication_layout.setAlignment(Qt.AlignCenter | Qt.AlignBottom)

        publication_label = QLabel('<a href="https://arxiv.org/abs/2505.08209">Access the ABAC Lab Research Publication</a>')
        publication_label.setOpenExternalLinks(True)
        publication_label.setStyleSheet("""
            font-size: 18px;
            color: #003366;
            font-weight: bold;
        """)
        publication_label.setAlignment(Qt.AlignCenter)
        publication_layout.addWidget(publication_label)

        # Right: Version Box
        version_layout = QVBoxLayout()
        version_layout.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        version_box = QWidget()
        version_box_layout = QHBoxLayout(version_box)
        version_box_layout.setContentsMargins(10, 10, 10, 10)
        version_box.setStyleSheet("""
            background-color: #003366;
            border-radius: 5px;
            padding: 7px;
        """)
        version_icon = QLabel()
        version_icon.setPixmap(QPixmap(resource_path("res/abac_w.png")).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        version_label = QLabel("ABAC Lab v1.0")
        version_label.setStyleSheet("font-size: 19px; font-weight: bold; color: white; margin-left: 12px;")

        version_box_layout.addWidget(version_icon)
        version_box_layout.addWidget(version_label)
        version_box_layout.setAlignment(Qt.AlignVCenter)

        credits_label = QLabel('Credit: Icons by <a href="https://icons8.com/icons">Icons8</a> • <a href="https://brew.sh">Homebrew</a>')
        credits_label.setOpenExternalLinks(True)
        credits_label.setStyleSheet("""
            font-size: 12px;
            color: black;
            margin-top: 6px;
        """)
        credits_label.setAlignment(Qt.AlignRight)

        version_layout.addWidget(version_box)
        version_layout.addWidget(credits_label)

        # Add all layouts to the bottom row
        bottom_row.addLayout(bug_contact_layout)
        bottom_row.addStretch(1)
        bottom_row.addLayout(publication_layout)
        bottom_row.addStretch(1)
        bottom_row.addLayout(version_layout)
        self.page6_layout.addLayout(bottom_row)


        # ------------------------
        self.stacked_widget.addWidget(self.page1)  # Policy
        self.stacked_widget.addWidget(self.page2)  # Analysis
        self.stacked_widget.addWidget(self.page3)  # Convert
        self.stacked_widget.addWidget(self.page4)  # Log Generator
        self.stacked_widget.addWidget(self.page5)  # Demos
        self.stacked_widget.addWidget(self.page6)  # Help & Support
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        self.apply_stylesheet()
        self.setWindowTitle("ABAC Lab")
        self.setGeometry(300, 300, 1000, 800)
        self.showMaximized()
        self.show()

        self.switch_page(0, "policy")

    def get_file_names(self, file_paths):
        file_names = [os.path.basename(file_path) for file_path in file_paths]
        return file_names

    def clear_uploaded_files(self):
        self.abac_data = {}
        self.uploaded_files = []
        self.current_abac_path = None
        self.uploaded_file_label.setText("")
        self.clear_files_button.hide()
        # Clear individual file buttons
        self.file_list_widget.clear()

    def upload_file(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Select ABAC Policy Files",
            "",
            "All Files (*);;Policy Files (*.txt *.pol *.abac)",
            options=options,
        )
        if file_names:
            for file_name in file_names:
                try:
                    self.handle_file_upload(file_name)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse ABAC file:\n{str(e)}")

    def handle_file_upload(self, file_path):
        try:
            # Create a single progress dialog for this file's processing
            progress = QProgressDialog(f"Processing {os.path.basename(file_path)}...", None, 0, 100, self)
            progress.setWindowTitle("Loading File")
            progress.setWindowModality(Qt.WindowModal)
            progress.setCancelButton(None)  # Remove cancel button (optional)
            progress.show()
            QApplication.processEvents()

            # Step 1: Parse ABAC file (20%)
            progress.setValue(20)
            new_user_mgr, new_res_mgr, new_rule_mgr = parse_abac_file(file_path)
            
            # Store parsed data
            self.abac_data[file_path] = (new_user_mgr, new_res_mgr, new_rule_mgr)
            if file_path not in self.uploaded_files:
                self.uploaded_files.append(file_path)
                self.add_file_to_list(file_path)

            # Step 2: Precompute stats (40%)
            progress.setValue(40)
            precompute_all_stats(self)
            
            # Step 3: Precompute bar graphs (60%)
            progress.setValue(60)
            precompute_bar_graphs(self)
            
            # Step 4: Precompute heatmaps (80%)
            progress.setValue(80)
            precompute_heatmaps(self)
            
            # Step 5: Precompute permission stats (100%)
            progress.setValue(100)
            precompute_permstats(self)

            self.clear_files_button.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse ABAC file:\n{str(e)}")
        finally:
            progress.close()  # Ensure dialog closes even on error

    def add_file_to_list(self, file_path):
        file_name = os.path.basename(file_path)
        item = QListWidgetItem()
        remove_button = QPushButton()
        remove_button.setFixedSize(40, 40)
        remove_button.setIcon(QIcon("res/trash.png"))
        remove_button.setIconSize(QSize(24, 24))
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)

        remove_button.clicked.connect(lambda: self.remove_file(file_path, item))

        # Create custom widget with horizontal layout
        widget = QWidget()
        layout = QHBoxLayout(widget)

        file_label = QLabel(file_name)
        file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        file_label.setAlignment(Qt.AlignCenter)
        file_label.setStyleSheet("font-size: 16px; color: black;")

        layout.addWidget(file_label)
        layout.addWidget(remove_button)

        widget.setLayout(layout)
        # Reserves enough space for the widget
        item.setSizeHint(widget.sizeHint())
        self.file_list_widget.addItem(item)
        self.file_list_widget.setItemWidget(item, widget)

    def remove_file(self, file_path, item):
        if file_path in self.uploaded_files:
            self.uploaded_files.remove(file_path)
            del self.abac_data[file_path]
            # Remove precomputed stats
            if hasattr(self, 'abac_stats') and file_path in self.abac_stats:
                del self.abac_stats[file_path]
            # Remove cached bar graph data
            if hasattr(self, 'bar_graph_cache') and file_path in self.bar_graph_cache:
                del self.bar_graph_cache[file_path]
            if hasattr(self, 'heatmap_cache') and file_path in self.heatmap_cache:
                del self.heatmap_cache[file_path]
            if hasattr(self, 'permstats_cache') and file_path in self.permstats_cache:
                del self.permstats_cache[file_path]
            # Remove widget from the layout
            row = self.file_list_widget.row(item)
            self.file_list_widget.takeItem(row)
            if self.current_abac_path == file_path:
                if self.uploaded_files:
                    self.current_abac_path = self.uploaded_files[0]  # Default to the first file
                else:
                    self.current_abac_path = None  # No files left
            if not self.uploaded_files:
                self.clear_files_button.hide()
            

    def add_toolbar_actions(self):
        # Prevent layout shifting upwards when switching between pages
        self.toolbar.setFixedWidth(300)

        title_layout = QHBoxLayout()
        abac_label = QLabel("ABAC Lab")
        abac_label.setAlignment(Qt.AlignCenter)
        abac_label.setStyleSheet("font-size: 32px; color: white;")
        title_layout.addWidget(abac_label)
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(resource_path("res/abac_w.png")).scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(icon_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        self.toolbar.addWidget(title_widget)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        

        self.default_icons = {
            "policy": QIcon(resource_path("res/policy.png")),
            "analysis": QIcon(resource_path("res/analysis.png")),
            "convert": QIcon(resource_path("res/convert.png")),
            "log": QIcon(resource_path("res/log.png")),
            "demo": QIcon(resource_path("res/demo.png")),
            "help": QIcon(resource_path("res/help.png")),
        }

        self.toolbar_actions = {
            "policy": QAction(self.default_icons["policy"], "Policy Manager", self),
            "analysis": QAction(self.default_icons["analysis"], "Analysis", self),
            "convert": QAction(self.default_icons["convert"], "Data Conversion", self),
            "log": QAction(self.default_icons["log"], "Log Generator", self),
            "demo": QAction(self.default_icons["demo"], "Demos", self),
            "help": QAction(self.default_icons["help"], "Help && Support", self),
        }

        self.active_icons = {
            "policy": QIcon(resource_path("res/policy_active.png")),
            "analysis": QIcon(resource_path("res/analysis_active.png")),
            "convert": QIcon(resource_path("res/convert_active.png")),
            "log": QIcon(resource_path("res/log_active.png")),
            "demo": QIcon(resource_path("res/demo_active.png")),
            "help": QIcon(resource_path("res/help_active.png")),
        }

        # Connect top section buttons to switch_page function
        self.toolbar_actions["policy"].triggered.connect(lambda: self.show_page1())
        self.toolbar_actions["analysis"].triggered.connect(lambda: self.show_page2())
        self.toolbar_actions["convert"].triggered.connect(lambda: self.show_page3())
        self.toolbar_actions["log"].triggered.connect(lambda: self.show_page4())
        self.toolbar_actions["demo"].triggered.connect(lambda: self.show_page5())

        # Add top section actions
        for key in ["policy", "analysis", "convert", "log", "demo"]:
            self.toolbar.addAction(self.toolbar_actions[key])

        # Add spacer to push the last two to the bottom
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        # Add bottom section actions (Settings & Help)
        self.toolbar_actions["help"].triggered.connect(lambda: self.show_page6())

        for key in ["help"]:
            self.toolbar.addAction(self.toolbar_actions[key])
        
    def show_permissions(self):
        show_permissions(self)

    def on_file_dropdown_changed(self, selected_file_name):
        on_file_dropdown_changed(self, selected_file_name)

    def update_displayed_results(self, results):
        update_displayed_results(self, results)

    def save_permissions_to_file(self, request_file):
        save_permissions_to_file(self, request_file)

    def compute_abac_stats(self):
        return compute_abac_stats(self)
    
    def save_abac_stats(self, abac_path):
        save_abac_stats(self, abac_path)

    def update_sorted_permissions(self, results):
        update_sorted_permissions(self, results)

    def show_permissions_choice(self):
        self.stats_widget.hide()
        self.perm_widget.hide()
        self.bar_graph_widget.hide()
        self.heat_map_widget.hide()
        self.rule_widget.hide()
        self.rule_perm_lbl.hide()
        self.rule_perm_btn.hide()
        self.heat_map_lbl.hide()
        self.heatmap_btn_page2.hide()
        self.perm_btn.hide()
        self.permissions_lbl.hide()
        self.bar_graph_btn.hide()
        self.bar_grph_lbl.hide()
        self.stats_container.hide()
        self.clear_results_container()
        self.results_area_container.show()
        self.page2_label.hide()

        container = QWidget()
        container.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()

        prompt_label = QLabel("Choose a method for processing permissions:")
        prompt_label.setStyleSheet("color: red; font-weight: bold; font-size: 26px;")
        layout.addWidget(prompt_label, alignment=Qt.AlignCenter)

        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        file_widget.setStyleSheet("""
            QWidget{
            border-radius: 10px; 
            padding: 0px; 
            border: 2px solid #003366;
        }
        """)
        file_widget.setFixedSize(400, 300)
        file_label = QLabel("This feature evaluates access requests from an input file based on the predefined policies.")
        file_label.setStyleSheet("font-size: 24px; color: black; border: none;")
        file_label.setWordWrap(True)
        file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        file_layout.addWidget(file_label, alignment=Qt.AlignCenter)

        process_btn = QPushButton("File Check")
        process_btn.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            color: white;
            background-color: #005F9E;
            border: none;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #003366;
        }
    """)

        process_btn.setFixedSize(200, 40)
        # This calls your existing permissions processing (the current show_permissions function)
        process_btn.clicked.connect(self.show_permissions)
        file_layout.addWidget(process_btn, alignment=Qt.AlignCenter | Qt.AlignBottom)

        manual_widget = QWidget()
        manual_layout = QVBoxLayout(manual_widget)
        manual_widget.setStyleSheet("""
            QWidget{
            border-radius: 10px; 
            padding: 0px; 
            border: 2px solid #003366;
        }
        """)
        manual_widget.setFixedSize(400, 300)
        manual_label = QLabel("This feature allows users to manually check access requests based on the predefined policies. "
        "Users can input subjects, resources, and actions, and the system will determine whether access is granted according to the policy rules.")
        manual_label.setStyleSheet("font-size: 22px; color: black; border: none;")
        manual_label.setWordWrap(True)
        manual_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        manual_layout.addWidget(manual_label, alignment=Qt.AlignCenter)
        
        manual_btn = QPushButton("Manual Check")
        manual_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: white;
                background-color: #005F9E;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)

        manual_btn.setFixedSize(200, 40)
        manual_btn.clicked.connect(self.show_manual_check)
        manual_layout.addWidget(manual_btn, alignment=Qt.AlignCenter | Qt.AlignBottom)

        grid_permissions_layout = QHBoxLayout()
        grid_permissions_layout.addWidget(file_widget, alignment=Qt.AlignRight)
        grid_permissions_layout.addWidget(manual_widget, alignment=Qt.AlignLeft)

        layout.addLayout(grid_permissions_layout)

        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: white;
                background-color: #005F9E;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)

        back_btn.setFixedSize(150, 40)
        back_btn.clicked.connect(self.show_page2)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        container.setLayout(layout)

        self.results_layout.addWidget(container)
        self.scroll_area.show()

    def show_manual_check(self):
        show_manual_check(self)

    def save_manual_check_results(self):
        save_manual_check_results(self)

    def save_manual_check_page_results(self):
        save_manual_check_page_results(self)

    def set_manual_page(self, page):
        set_manual_page(self, page)

    def show_bar_graph(self):
        show_bar_graph(self)

    def show_heatmap(self):
        show_heatmap(self)

    def go_back(self, container):
        """Clear the results layout and returns to Page 2."""    
        self.scroll_area.hide()
        self.results_layout.removeWidget(container)
        container.setParent(None)
        container.deleteLater()

        self.show_page2()
        self.switch_page(1, "analysis")
        QApplication.processEvents()

    def clear_results_container(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


    def show_permstats(self):
        show_permstats(self)

    def on_permstats_file_dropdown_changed(self, selected_file_name):
        on_permstats_file_dropdown_changed(self, selected_file_name)

    def show_rulevu(self):
        show_rulevu(self)

    def on_manual_page_input(self):
        on_manual_page_input(self)

    def show_rule_choices(self):
        self.stats_widget.hide()
        self.perm_widget.hide()
        self.bar_graph_widget.hide()
        self.heat_map_widget.hide()
        self.rule_widget.hide()
        self.rule_perm_lbl.hide()
        self.rule_perm_btn.hide()
        self.heat_map_lbl.hide()
        self.heatmap_btn_page2.hide()
        self.perm_btn.hide()
        self.permissions_lbl.hide()
        self.bar_graph_btn.hide()
        self.bar_grph_lbl.hide()
        self.clear_results_container()
        self.results_area_container.show()
        self.stats_container.hide()
        self.page2_label.hide()

        container = QWidget()
        container.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()
        
        prompt_label = QLabel("Choose a method for processing rules:")
        prompt_label.setStyleSheet("color: red; font-weight: bold; font-size: 26px;")
        layout.addWidget(prompt_label, alignment=Qt.AlignCenter)

        rule_permissions_widget = QWidget()
        rule_permissions_layout = QVBoxLayout(rule_permissions_widget)
        rule_permissions_widget.setStyleSheet("""
            QWidget {
                border: 2px solid #003366;
                border-radius: 10px;
                padding: 10px;    
            }
        """)
        rule_permissions_widget.setFixedSize(400, 300)
        rule_permissions_label = QLabel("This feature shows how many permissions are granted by each rule in the input policies and lists all the permissions covered by that rule.")
        rule_permissions_label.setStyleSheet("font-size: 24px; color: black; border: none;")
        rule_permissions_label.setWordWrap(True)
        rule_permissions_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        rule_permissions_layout.addWidget(rule_permissions_label, alignment=Qt.AlignCenter)

        stats_btn = QPushButton("Rule Permissions")
        stats_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: white;
                background-color: #005F9E;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)

        stats_btn.setFixedSize(200, 40)
        stats_btn.clicked.connect(self.show_permstats)  # Calls show_permstats
        rule_permissions_layout.addWidget(stats_btn, alignment=Qt.AlignCenter | Qt.AlignBottom)

        rule_view_widget = QWidget()
        rule_view_layout = QVBoxLayout(rule_view_widget)
        rule_view_widget.setStyleSheet("""
            QWidget {
                border: 2px solid #003366;
                border-radius: 10px;
                padding: 10px;    
            }
        """)
        rule_view_widget.setFixedSize(400, 300)
        rule_view_label = QLabel("This feature takes a set of rules from an input file and computes the total number of permissions granted based on the attribute data in the input policy. "
        "It also lists all permissions covered by each rule.")
        rule_view_label.setStyleSheet("font-size: 24px; color: black; border: none;")
        rule_view_label.setWordWrap(True)
        rule_view_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        rule_view_layout.addWidget(rule_view_label, alignment=Qt.AlignCenter)

        rule_view_btn = QPushButton("File Check")
        rule_view_btn.setFixedSize(200, 40)
        rule_view_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: white;
                background-color: #005F9E;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)

        rule_view_btn.clicked.connect(self.show_rulevu)
        rule_view_layout.addWidget(rule_view_btn, alignment=Qt.AlignCenter | Qt.AlignBottom)
    
        grid_rule_layout = QHBoxLayout()
        grid_rule_layout.addWidget(rule_permissions_widget, alignment=Qt.AlignRight)
        grid_rule_layout.addWidget(rule_view_widget, alignment=Qt.AlignLeft)
        
        layout.addLayout(grid_rule_layout)

        back_btn = QPushButton("Back")
        back_btn.setFixedSize(150, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                color: white;
                background-color: #005F9E;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
        """)

        back_btn.clicked.connect(self.show_page2)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)
        
        container.setLayout(layout)
        self.results_layout.addWidget(container)
        self.scroll_area.show()

    def reset_toolbar_icons(self):
        for key, action in self.toolbar_actions.items():
            if key in self.default_icons:
                action.setIcon(self.default_icons[key])
        

    def switch_page(self, page_index, page_name):
        # Reset all toolbar icons to default before setting active one
        self.reset_toolbar_icons()

        # Set the selected button to its active icon
        if page_name in self.active_icons:
            self.toolbar_actions[page_name].setIcon(self.active_icons[page_name])

        # Change the current page
        self.stacked_widget.setCurrentIndex(page_index)

        self.toolbar.update()

    def show_page1(self):
        self.switch_page(0, "policy")

    def show_page2(self):
        self.switch_page(1, "analysis")
        self.results_area_container.hide()
        self.stats_widget.show()
        self.perm_widget.show()
        self.bar_graph_widget.show()
        self.heat_map_widget.show()
        self.rule_widget.show()
        self.rule_perm_lbl.show()
        self.rule_perm_btn.show()
        self.heat_map_lbl.show()
        self.heatmap_btn_page2.show()
        self.perm_btn.show()
        self.permissions_lbl.show()
        self.bar_graph_btn.show()
        self.bar_grph_lbl.show()
        self.stats_container.show()
        self.scroll_area.hide()
        self.page2_label.show()
        show_stats(self)

    def show_page3(self):
        self.page3_current_uploaded_files.clear()
        file_names = self.get_file_names(self.uploaded_files)
        self.page3_current_uploaded_files.addItems(file_names)
        self.switch_page(2, "convert")

    def show_page4(self):
        self.page4_current_uploaded_files.clear()
        file_names = self.get_file_names(self.uploaded_files)
        self.page4_current_uploaded_files.addItems(file_names)
        self.switch_page(3, "log")

    def show_page5(self):
        self.switch_page(4, "demo")

    def show_page6(self):
        self.switch_page(5, "help")

    def apply_stylesheet(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #005F9E;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                font-family: 'Arial';
            }
            QPushButton:hover {
                background-color: #003366;
            }
            QToolBar {
                background-color: #003366;
                border: none;
                padding: 5px; 
                border-radius: 10px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                color: white;
                font-size: 12px;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Arial';
            }
            QComboBox {
                background-color: #FFFFFF;
                color: black
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: black;
                selection-background-color: #ADD8E6;
                selection-color: black;
            }
            QToolBar QToolButton:hover {
                background-color: #005F9E; 
            }
            QListWidget {
            font-family: 'Arial';
            color: black;
            }
        """
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())