from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from ..utils.i18n import tr

from ..services.note_service import note_service


class NotesPanel(QWidget):
    """Simple note-taking area persisted in the database."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_note()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        save_btn = QPushButton(tr("notes.save"))
        save_btn.clicked.connect(self._save_note)
        layout.addWidget(self.text_edit)
        layout.addWidget(save_btn)
        self._save_btn = save_btn

    def _load_note(self):
        self.text_edit.setPlainText(note_service.get_current_content())

    def _save_note(self):
        note_service.save_content(self.text_edit.toPlainText())

    def retranslate(self):
        self._save_btn.setText(tr("notes.save"))
