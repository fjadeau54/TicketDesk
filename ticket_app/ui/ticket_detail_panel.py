from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout, QTextEdit
from ..utils.i18n import tr


class TicketDetailPanel(QWidget):
    """Side panel showing details of the selected ticket."""

    def __init__(self, parent=None, on_toggle_resolved=None):
        super().__init__(parent)
        self._ticket = None
        self._on_toggle_resolved = on_toggle_resolved
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(tr("detail.title")))

        form = QFormLayout()
        self.lbl_theme = QLabel("-")
        self.lbl_urgency = QLabel("-")
        self.lbl_deadline = QLabel("-")
        self.lbl_created = QLabel("-")

        self.txt_description = QTextEdit()
        self.txt_description.setReadOnly(True)
        self.txt_description.setFixedHeight(120)

        form.addRow(tr("detail.theme"), self.lbl_theme)
        form.addRow(tr("detail.urgency"), self.lbl_urgency)
        form.addRow(tr("detail.deadline"), self.lbl_deadline)
        form.addRow(tr("detail.created"), self.lbl_created)
        form.addRow(tr("detail.description"), self.txt_description)

        layout.addLayout(form)

        self.btn_toggle = QPushButton(tr("detail.resolve"))
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
            self.btn_toggle.setText(tr("detail.resolve"))
            return

        self.lbl_theme.setText(ticket.theme or "-")
        self.lbl_urgency.setText(ticket.urgency or "-")
        self.lbl_deadline.setText(ticket.deadline or "-")
        self.lbl_created.setText(ticket.created_at or "-")
        self.txt_description.setPlainText(ticket.description or "")
        self.btn_toggle.setEnabled(True)
        if ticket.archived:
            self.btn_toggle.setText(tr("detail.reopen"))
        else:
            self.btn_toggle.setText(tr("detail.resolve"))

    def _handle_toggle(self):
        if self._ticket and self._on_toggle_resolved:
            self._on_toggle_resolved()

    def retranslate(self):
        # Update static labels
        self.findChild(QLabel, "").setText(tr("detail.title")) if False else None
        # rebuild form labels
        form = self.btn_toggle.parent().layout().itemAt(1).layout()  # not reliable
        # safer: rebuild label texts directly
        # Labels already stored
        # Only button and heading need update
        self.layout().itemAt(0).widget().setText(tr("detail.title"))
        form_layout = self.layout().itemAt(1).layout()
        form_layout.labelForField(self.lbl_theme).setText(tr("detail.theme"))
        form_layout.labelForField(self.lbl_urgency).setText(tr("detail.urgency"))
        form_layout.labelForField(self.lbl_deadline).setText(tr("detail.deadline"))
        form_layout.labelForField(self.lbl_created).setText(tr("detail.created"))
        form_layout.labelForField(self.txt_description).setText(tr("detail.description"))
        if self._ticket and self._ticket.archived:
            self.btn_toggle.setText(tr("detail.reopen"))
        else:
            self.btn_toggle.setText(tr("detail.resolve"))
