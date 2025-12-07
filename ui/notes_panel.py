from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QLabel
from ..services.note_service import note_service

class NotesPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Bloc-notes"))

        self.text_edit = QPlainTextEdit()
        layout.addWidget(self.text_edit)

        self.save_btn = QPushButton("Sauvegarder")
        layout.addWidget(self.save_btn)

        self.save_btn.clicked.connect(self._save)

        # charger contenu
        self.text_edit.setPlainText(note_service.get_current_content())

    def _save(self):
        content = self.text_edit.toPlainText()
        note_service.save_content(content)
