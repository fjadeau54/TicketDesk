from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PostItBoard(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Tableau de post-it (à implémenter)"))
