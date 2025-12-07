from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from ..utils.i18n import tr


class CommandPalette(QDialog):
    """Simple command palette (Ctrl+K) with filterable actions."""

    def __init__(self, actions: list[tuple[str, str]], parent=None):
        """
        actions: list of tuples (action_id, label)
        """
        super().__init__(parent)
        self.setWindowTitle(tr("palette.title"))
        self.actions = actions
        self.filtered = actions
        self._init_ui()
        self._refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("palette.search"))
        self.search_edit.textChanged.connect(self._filter)
        self.search_edit.returnPressed.connect(self._accept_current)
        layout.addWidget(self.search_edit)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(lambda _: self.accept())
        layout.addWidget(self.list_widget)

    def _filter(self):
        text = self.search_edit.text().lower()
        if not text:
            self.filtered = self.actions
        else:
            self.filtered = [
                (aid, label) for aid, label in self.actions
                if text in label.lower()
            ]
        self._refresh()

    def _refresh(self):
        self.list_widget.clear()
        for aid, label in self.filtered:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, aid)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _accept_current(self):
        if self.list_widget.currentRow() >= 0:
            self.accept()

    def get_selected_action(self) -> str | None:
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.filtered):
            return None
        return self.filtered[row][0]
