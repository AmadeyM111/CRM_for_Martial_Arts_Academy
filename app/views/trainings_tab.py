from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class TrainingsTab(QWidget):
    """Tab for managing trainings"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Вкладка тренировок - в разработке")
        layout.addWidget(label)
