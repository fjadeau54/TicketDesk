from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QColor
from typing import List
from ..db.models import Ticket
from ..utils.i18n import tr

class TicketTableModel(QAbstractTableModel):

    def __init__(self, tickets: List[Ticket] | None = None):
        super().__init__()
        self._tickets: List[Ticket] = tickets or []
        self._theme_colors: dict[str, str] = {}
        self._headers = [
            "ID",
            tr("ticket.table.title"),
            tr("ticket.table.urgency"),
            tr("ticket.table.deadline"),
            tr("ticket.table.theme"),
            tr("ticket.table.archived"),
        ]

    def set_tickets(self, tickets: List[Ticket]):
        self.beginResetModel()
        self._tickets = tickets
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._tickets)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        ticket = self._tickets[index.row()]
        col = index.column()

        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 0:
                return ticket.id
            elif col == 1:
                return ticket.title
            elif col == 2:
                return ticket.urgency
            elif col == 3:
                return ticket.deadline
            elif col == 4:
                return ticket.theme
            elif col == 5:
                return tr("yes") if ticket.archived else tr("no")
        elif role == Qt.ForegroundRole and ticket.archived:
            return QColor("red")
        elif col == 4 and role == Qt.BackgroundRole:
            color = self._theme_colors.get(ticket.theme)
            if color:
                qc = QColor(color)
                if qc.isValid():
                    return qc
        elif col == 4 and role == Qt.DecorationRole:
            color = self._theme_colors.get(ticket.theme)
            if color:
                qc = QColor(color)
                if qc.isValid():
                    from PySide6.QtGui import QPixmap
                    pix = QPixmap(12, 12)
                    pix.fill(qc)
                    return pix
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1

    def get_ticket_at(self, row: int) -> Ticket:
        return self._tickets[row]

    def set_theme_colors(self, mapping: dict[str, str]):
        self._theme_colors = mapping or {}
        if self.rowCount() > 0:
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole])

    def refresh_headers(self):
        self._headers = [
            "ID",
            tr("ticket.table.title"),
            tr("ticket.table.urgency"),
            tr("ticket.table.deadline"),
            tr("ticket.table.theme"),
            tr("ticket.table.archived"),
        ]
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(self._headers) - 1)
        if self.rowCount() > 0:
            top_left = self.index(0, 5)
            bottom_right = self.index(self.rowCount() - 1, 5)
            self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
