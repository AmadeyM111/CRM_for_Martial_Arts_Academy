from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QMenuBar, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BJJ Academy CRM System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize UI
        self.init_ui()
        self.init_menu()
        self.init_status_bar()
        
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs (will be implemented in separate modules)
        self.add_tabs()
        
    def add_tabs(self):
        """Add main tabs to the interface"""
        # Students tab
        from app.views.students_tab import StudentsTab
        students_tab = StudentsTab()
        self.tab_widget.addTab(students_tab, "Ученики")
        
        # Trainings tab
        from app.views.trainings_tab import TrainingsTab
        trainings_tab = TrainingsTab()
        self.tab_widget.addTab(trainings_tab, "Тренировки")
        
        # Payments tab
        from app.views.payments_tab import PaymentsTab
        payments_tab = PaymentsTab()
        self.tab_widget.addTab(payments_tab, "Платежи")
        
        # Reports tab
        from app.views.reports_tab import ReportsTab
        reports_tab = ReportsTab()
        self.tab_widget.addTab(reports_tab, "Отчеты")
        
        # Settings tab
        from app.views.settings_tab import SettingsTab
        settings_tab = SettingsTab()
        self.tab_widget.addTab(settings_tab, "Настройки")
        
    def init_menu(self):
        """Initialize menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('Файл')
        
        # Backup action
        backup_action = QAction('Создать резервную копию', self)
        backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Помощь')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def init_status_bar(self):
        """Initialize status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
    def create_backup(self):
        """Create database backup"""
        # TODO: Implement backup functionality
        QMessageBox.information(self, "Резервное копирование", 
                              "Функция резервного копирования будет реализована")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "О программе", 
                         "BJJ Academy CRM System v1.0.0\n"
                         "Система управления клиентами для академии бразильского джиу-джитсу")
