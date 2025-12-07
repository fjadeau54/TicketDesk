from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QDialogButtonBox, QDateEdit
)
from PySide6.QtCore import QDate
from ..services.theme_service import theme_service
from ..utils.i18n import tr

class TicketFormDialog(QDialog):
    """Dialog to create or edit a ticket."""

    URGENCIES = [
        ("Basse", "urgency.low"),
        ("Normale", "urgency.normal"),
        ("Haute", "urgency.high"),
        ("Critique", "urgency.critical"),
    ]

    def __init__(self, parent=None, ticket=None):
        super().__init__(parent)
        self.setWindowTitle(tr("ticket.form.title"))
        self._ticket = ticket
        self._build_form()
        if ticket:
            self._populate(ticket)

    def _build_form(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.theme_combo = QComboBox()
        self.theme_combo.setEditable(True)
        self._load_themes()
        self.urgency_combo = QComboBox()
        for value, key in self.URGENCIES:
            self.urgency_combo.addItem(tr(key), value)
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.deadline_edit.setDate(QDate.currentDate())
        self.description_edit = QTextEdit()

        form.addRow(tr("ticket.form.field.title"), self.title_edit)
        form.addRow(tr("ticket.form.field.theme"), self.theme_combo)
        form.addRow(tr("ticket.form.field.urgency"), self.urgency_combo)
        form.addRow(tr("ticket.form.field.deadline"), self.deadline_edit)
        form.addRow(tr("ticket.form.field.description"), self.description_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self, ticket):
        self.title_edit.setText(ticket.title)
        if ticket.theme:
            self.theme_combo.setCurrentText(ticket.theme)
        if ticket.urgency:
            idx = self.urgency_combo.findData(ticket.urgency)
            if idx >= 0:
                self.urgency_combo.setCurrentIndex(idx)
        if ticket.deadline:
            try:
                parts = [int(p) for p in ticket.deadline.split("-")]
                self.deadline_edit.setDate(QDate(parts[0], parts[1], parts[2]))
            except Exception:
                pass
        self.description_edit.setPlainText(ticket.description)

    def get_ticket_data(self) -> dict:
        theme_text = self.theme_combo.currentText().strip()
        if theme_text and theme_text not in [self.theme_combo.itemText(i) for i in range(self.theme_combo.count())]:
            # create new theme with default color if not existing
            theme_service.create(theme_text, color="#cccccc")
            self._load_themes(select=theme_text)
        return {
            "title": self.title_edit.text().strip(),
            "theme": theme_text,
            "urgency": self.urgency_combo.currentData(),
            "deadline": self.deadline_edit.date().toString("yyyy-MM-dd"),
            "description": self.description_edit.toPlainText().strip(),
        }

    def _load_themes(self, select: str | None = None):
        themes = sorted([t.name for t in theme_service.get_all()])
        self.theme_combo.clear()
        self.theme_combo.addItems(themes)
        if select:
            self.theme_combo.setCurrentText(select)
