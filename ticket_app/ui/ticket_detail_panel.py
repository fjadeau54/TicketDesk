from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout, QTextEdit


class TicketDetailPanel(QWidget):
    """Side panel showing details of the selected ticket."""

    def __init__(self, parent=None, on_toggle_resolved=None):
        super().__init__(parent)
        self._ticket = None
        self._on_toggle_resolved = on_toggle_resolved
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Détails du ticket"))

        form = QFormLayout()
        self.lbl_theme = QLabel("-")
        self.lbl_urgency = QLabel("-")
        self.lbl_deadline = QLabel("-")
        self.lbl_created = QLabel("-")

        self.txt_description = QTextEdit()
        self.txt_description.setReadOnly(True)
        self.txt_description.setFixedHeight(120)

        form.addRow("Thème", self.lbl_theme)
        form.addRow("Urgence", self.lbl_urgency)
        form.addRow("Échéance", self.lbl_deadline)
        form.addRow("Créé le", self.lbl_created)
        form.addRow("Description", self.txt_description)

        layout.addLayout(form)

        self.btn_toggle = QPushButton("Marquer comme résolu")
        self.btn_toggle.clicked.connect(self._handle_toggle)
        layout.addWidget(self.btn_toggle)

        layout.addStretch()

    def set_ticket(self, ticket):
        self._ticket = ticket
        if not ticket:
            self.lbl_theme.setText("-")
            self.lbl_urgency.setText("-")
            self.lbl_deadline.setText("-")
            self.lbl_created.setText("-")
            self.txt_description.setPlainText("")
            self.btn_toggle.setEnabled(False)
            self.btn_toggle.setText("Marquer comme résolu")
            return

        self.lbl_theme.setText(ticket.theme or "-")
        self.lbl_urgency.setText(ticket.urgency or "-")
        self.lbl_deadline.setText(ticket.deadline or "-")
        self.lbl_created.setText(ticket.created_at or "-")
        self.txt_description.setPlainText(ticket.description or "")
        self.btn_toggle.setEnabled(True)
        if ticket.archived:
            self.btn_toggle.setText("Réouvrir")
        else:
            self.btn_toggle.setText("Marquer comme résolu")

    def _handle_toggle(self):
        if self._ticket and self._on_toggle_resolved:
            self._on_toggle_resolved()
