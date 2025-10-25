from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PaymentsTab(QWidget):
    """Tab for managing payments"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Вкладка платежей - в разработке")
        layout.addWidget(label)
