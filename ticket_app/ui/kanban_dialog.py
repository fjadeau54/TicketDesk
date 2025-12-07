from __future__ import annotations

from typing import List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QListWidget, QListWidgetItem, QWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ..services.ticket_service import ticket_service
from ..db.models import Ticket
from ..utils.i18n import tr


class KanbanList(QListWidget):
    """List widget that accepts drops to change ticket attribute."""

    def __init__(self, label: str, key: str, value: str):
        super().__init__()
        self.column_label = label
        self.key = key          # "theme" or "urgency"
        self.value = value
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSpacing(6)
        self.setMinimumWidth(180)
        self.setUniformItemSizes(True)

    def dropEvent(self, event):
        # Let the default behavior move the item visually
        super().dropEvent(event)
        if hasattr(self, "parent_dialog"):
            self.parent_dialog.handle_drop(self)


class KanbanDialog(QDialog):
    """Kanban view to drag tickets across columns grouped by theme or urgency."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("kanban.title"))
        self.tickets: List[Ticket] = []
        self.column_widgets: List[KanbanList] = []
        self._init_ui()
        self._load_tickets()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel(tr("kanban.group_by")))
        self.group_by_combo = QComboBox()
        self.group_by_combo.addItem(tr("kanban.group.theme"), "theme")
        self.group_by_combo.addItem(tr("kanban.group.urgency"), "urgency")
        self.group_by_combo.currentIndexChanged.connect(self._refresh_columns)
        top.addWidget(self.group_by_combo)
        top.addStretch()
        layout.addLayout(top)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.columns_layout = QHBoxLayout(container)
        self.columns_layout.setContentsMargins(0, 0, 0, 0)
        self.columns_layout.setSpacing(12)
        self.scroll.setWidget(container)
        layout.addWidget(self.scroll)

    def _load_tickets(self):
        self.tickets = [
            t for t in ticket_service.get_all_tickets(include_archived=False)
        ]
        self._refresh_columns()

    def _group_keys(self):
        mode = self.group_by_combo.currentData()
        if mode == "urgency":
            return ["Basse", "Normale", "Haute", "Critique"]
        # themes
        themes = sorted({t.theme or "" for t in self.tickets})
        return themes or [""]

    def _refresh_columns(self):
        # Clear old columns
        while self.columns_layout.count():
            item = self.columns_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.column_widgets.clear()

        mode = self.group_by_combo.currentData()
        for key in self._group_keys():
            display = key if key else tr("kanban.no_tickets")
            list_widget = KanbanList(label=display, key=mode, value=key)
            list_widget.parent_dialog = self
            self.column_widgets.append(list_widget)

            # Column container with title
            column_container = QVBoxLayout()
            header = QLabel(display)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("font-weight: bold;")
            column_container.addWidget(header)
            column_container.addWidget(list_widget)
            wrapper = QWidget()
            wrapper.setLayout(column_container)
            self.columns_layout.addWidget(wrapper)

        self._populate_tickets()

    def _populate_tickets(self):
        # Clear lists
        for col in self.column_widgets:
            col.clear()
        mode = self.group_by_combo.currentData()
        for t in self.tickets:
            target_value = getattr(t, mode) or ""
            # match by value
            target_col = None
            for col in self.column_widgets:
                if col.value == target_value or (not target_value and col.value == tr("kanban.no_tickets")):
                    target_col = col
                    break
            if not target_col and self.column_widgets:
                target_col = self.column_widgets[-1]
            item = QListWidgetItem(f"#{t.id} {t.title}")
            item.setData(Qt.UserRole, t.id)
            target_col.addItem(item)
        # empty columns placeholder
        placeholder = tr("kanban.column.empty")
        for col in self.column_widgets:
            if col.count() == 0:
                item = QListWidgetItem(placeholder)
                item.setFlags(Qt.NoItemFlags)
                item.setForeground(QColor("#888"))
                col.addItem(item)

    def handle_drop(self, column: KanbanList):
        """After a drop, update ticket attribute to match target column."""
        mode = column.key  # "theme" or "urgency"
        new_value = column.value
        # For each real item in this column, update the ticket
        for i in range(column.count()):
            item = column.item(i)
            ticket_id = item.data(Qt.UserRole)
            if ticket_id is None:
                continue
            t = next((x for x in self.tickets if x.id == ticket_id), None)
            if not t:
                continue
            setattr(t, mode, new_value)
            ticket_service.update_ticket(t)
        # Refresh to maintain placeholders
        self._load_tickets()
