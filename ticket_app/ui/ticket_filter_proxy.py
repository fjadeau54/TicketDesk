from datetime import date, timedelta, datetime
from PySide6.QtCore import QSortFilterProxyModel


class TicketFilterProxy(QSortFilterProxyModel):
    """Filters tickets by search, urgency, deadline and theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""
        self.urgency = None
        self.deadline_filter = "all"
        self.theme = None

    def set_filters(self, search_text: str = "", urgency=None,
                    deadline_filter: str = "all", theme=None):
        self.search_text = search_text.lower().strip()
        self.urgency = urgency
        self.deadline_filter = deadline_filter
        self.theme = theme
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        if not model:
            return True
        ticket = model.get_ticket_at(source_row)

        # search
        if self.search_text:
            haystack = " ".join([
                str(ticket.title or ""),
                str(ticket.theme or ""),
                str(ticket.description or "")
            ]).lower()
            if self.search_text not in haystack:
                return False

        # urgency
        if self.urgency:
            if (ticket.urgency or "").lower() != str(self.urgency).lower():
                return False

        # theme
        if self.theme:
            if (ticket.theme or "") != self.theme:
                return False

        # deadline filters
        if self.deadline_filter != "all":
            if not ticket.deadline:
                return False
            try:
                d = datetime.strptime(ticket.deadline, "%Y-%m-%d").date()
            except Exception:
                return False
            today = date.today()
            if self.deadline_filter == "today":
                if d != today:
                    return False
            elif self.deadline_filter == "week":
                start = today - timedelta(days=today.weekday())
                end = start + timedelta(days=6)
                if not (start <= d <= end):
                    return False
            elif self.deadline_filter == "overdue":
                if d >= today:
                    return False

        return True
