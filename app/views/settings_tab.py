from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SettingsTab(QWidget):
    """Tab for settings"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Вкладка настроек - в разработке")
        layout.addWidget(label)
