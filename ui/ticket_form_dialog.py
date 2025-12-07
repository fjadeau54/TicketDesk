from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPlainTextEdit, QPushButton
)
from ..db.models import Ticket

class TicketFormDialog(QDialog):

    def __init__(self, parent=None, ticket: Ticket | None = None):
        super().__init__(parent)
        self.setWindowTitle("Ticket" if ticket else "Nouveau ticket")
        self._ticket = ticket

        layout = QVBoxLayout(self)

        # Titre
        layout.addWidget(QLabel("Titre"))
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)

        # Urgence
        layout.addWidget(QLabel("Urgence"))
        self.urgency_combo = QComboBox()
        self.urgency_combo.addItems(["Basse", "Moyenne", "Haute"])
        layout.addWidget(self.urgency_combo)

        # Échéance
        layout.addWidget(QLabel("Date limite (AAAA-MM-JJ)"))
        self.deadline_edit = QLineEdit()
        layout.addWidget(self.deadline_edit)

        # Thème
        layout.addWidget(QLabel("Thème"))
        self.theme_edit = QLineEdit()
        layout.addWidget(self.theme_edit)

        # Description
        layout.addWidget(QLabel("Description"))
        self.desc_edit = QPlainTextEdit()
        layout.addWidget(self.desc_edit)

        # Boutons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Enregistrer")
        self.cancel_btn = QPushButton("Annuler")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        if ticket:
            self._load_ticket(ticket)

    def _load_ticket(self, t: Ticket):
        self.title_edit.setText(t.title)
        self.urgency_combo.setCurrentText(t.urgency or "")
        self.deadline_edit.setText(t.deadline or "")
        self.theme_edit.setText(t.theme or "")
        self.desc_edit.setPlainText(t.description or "")

    def get_ticket_data(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "urgency": self.urgency_combo.currentText(),
            "deadline": self.deadline_edit.text().strip() or None,
            "theme": self.theme_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip(),
        }
