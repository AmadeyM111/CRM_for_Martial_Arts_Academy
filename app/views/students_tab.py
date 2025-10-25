from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
                             QLabel, QMessageBox, QDialog, QFormLayout, QDateEdit,
                             QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class StudentsTab(QWidget):
    """Tab for managing students"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_students()
        
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Search and filter section
        search_group = QGroupBox("Поиск и фильтры")
        search_layout = QHBoxLayout(search_group)
        
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_students)
        search_layout.addWidget(self.search_input)
        
        search_layout.addWidget(QLabel("Пояс:"))
        self.belt_filter = QComboBox()
        self.belt_filter.addItems(["Все", "White", "Blue", "Purple", "Brown", "Black"])
        self.belt_filter.currentTextChanged.connect(self.filter_students)
        search_layout.addWidget(self.belt_filter)
        
        search_layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все", "Активные", "Неактивные"])
        self.status_filter.currentTextChanged.connect(self.filter_students)
        search_layout.addWidget(self.status_filter)
        
        layout.addWidget(search_group)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels([
            "ID", "Имя", "Фамилия", "Телефон", "Telegram", "Пояс", "Дата регистрации"
        ])
        self.students_table.setAlternatingRowColors(True)
        self.students_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.students_table)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить ученика")
        self.add_button.clicked.connect(self.add_student)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_student)
        buttons_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_student)
        buttons_layout.addWidget(self.delete_button)
        
        self.view_details_button = QPushButton("Подробности")
        self.view_details_button.clicked.connect(self.view_student_details)
        buttons_layout.addWidget(self.view_details_button)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
    def load_students(self):
        """Load students from database"""
        # TODO: Implement database loading
        # For now, add sample data
        sample_students = [
            (1, "Student", "One", "+7-999-000-00-01", "@student1", "White", "2024-01-15"),
            (2, "Student", "Two", "+7-999-000-00-02", "@student2", "Blue", "2024-02-20"),
            (3, "Student", "Three", "+7-999-000-00-03", "@student3", "Purple", "2024-03-10"),
        ]
        
        self.students_table.setRowCount(len(sample_students))
        
        for row, student in enumerate(sample_students):
            for col, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.students_table.setItem(row, col, item)
                
        self.students_table.resizeColumnsToContents()
        
    def filter_students(self):
        """Filter students based on search criteria"""
        # TODO: Implement filtering logic
        pass
        
    def add_student(self):
        """Add new student"""
        dialog = StudentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # TODO: Save to database
            self.load_students()
            
    def edit_student(self):
        """Edit selected student"""
        current_row = self.students_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите ученика для редактирования")
            return
            
        # TODO: Load student data and open edit dialog
        QMessageBox.information(self, "Информация", "Функция редактирования будет реализована")
        
    def delete_student(self):
        """Delete selected student"""
        current_row = self.students_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите ученика для удаления")
            return
            
        reply = QMessageBox.question(self, "Подтверждение", 
                                    "Вы уверены, что хотите удалить этого ученика?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Delete from database
            self.load_students()
            
    def view_student_details(self):
        """View detailed information about selected student"""
        current_row = self.students_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите ученика для просмотра")
            return
            
        # TODO: Open detailed view dialog
        QMessageBox.information(self, "Информация", "Функция просмотра деталей будет реализована")


class StudentDialog(QDialog):
    """Dialog for adding/editing student"""
    
    def __init__(self, parent=None, student_data=None):
        super().__init__(parent)
        self.student_data = student_data
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Добавить ученика" if not self.student_data else "Редактировать ученика")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # Student information fields
        self.first_name_input = QLineEdit()
        layout.addRow("Имя:", self.first_name_input)
        
        self.last_name_input = QLineEdit()
        layout.addRow("Фамилия:", self.last_name_input)
        
        self.phone_input = QLineEdit()
        layout.addRow("Телефон:", self.phone_input)
        
        self.telegram_input = QLineEdit()
        layout.addRow("Telegram:", self.telegram_input)
        
        self.email_input = QLineEdit()
        layout.addRow("Email:", self.email_input)
        
        self.belt_combo = QComboBox()
        self.belt_combo.addItems(["White", "Blue", "Purple", "Brown", "Black"])
        layout.addRow("Текущий пояс:", self.belt_combo)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        layout.addRow("Заметки:", self.notes_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addRow(buttons_layout)
        
        # Load existing data if editing
        if self.student_data:
            self.load_student_data()
