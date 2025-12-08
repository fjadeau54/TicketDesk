from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar,
    QTableView, QSplitter, QTabWidget, QMessageBox, QCheckBox,
    QLineEdit, QComboBox, QHBoxLayout, QLabel, QFileDialog, QAbstractItemView, QApplication, QMenu
)
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QTimer

from ..services.ticket_service import ticket_service
from ..services.theme_service import theme_service
from .ticket_table_model import TicketTableModel
from .ticket_form_dialog import TicketFormDialog
from .notes_panel import NotesPanel
from .postit_board import PostItBoard
from .ticket_detail_panel import TicketDetailPanel
from .ticket_filter_proxy import TicketFilterProxy
from .settings_dialog import SettingsDialog
from .command_palette import CommandPalette
from .kanban_dialog import KanbanDialog
from ..config import DB_PATH
from ..utils.i18n import tr
from ..utils import i18n
from ..utils.theme_manager import apply_theme

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app.title"))
        self._alerts_shown = False

        self._init_ui()
        self._load_tickets()
        self._init_shortcuts()
        self._init_auto_refresh()

    def _init_ui(self):
        toolbar = QToolBar("Actions")
        self.addToolBar(toolbar)

        act_new = QAction(tr("menu.new_ticket"), self)
        act_edit = QAction(tr("menu.edit"), self)
        act_delete = QAction(tr("menu.delete"), self)
        act_refresh = QAction(tr("menu.refresh"), self)
        self.act_archive = QAction(tr("menu.archive"), self)
        act_settings = QAction(tr("menu.settings"), self)
        act_db = QAction(tr("menu.db"), self)
        act_kanban = QAction(tr("kanban.title"), self)
        self.act_kanban = act_kanban
        self.actions_map = {
            "new": act_new,
            "edit": act_edit,
            "delete": act_delete,
            "refresh": act_refresh,
            "archive": self.act_archive,
            "settings": act_settings,
            "db": act_db,
            "kanban": act_kanban,
        }

        toolbar.addAction(act_new)
        toolbar.addAction(act_edit)
        toolbar.addAction(act_delete)
        toolbar.addAction(self.act_archive)
        toolbar.addSeparator()
        toolbar.addAction(act_refresh)
        toolbar.addAction(act_settings)
        toolbar.addAction(act_db)
        toolbar.addAction(act_kanban)

        self.show_archived = QCheckBox(tr("menu.show_archived"))
        self.show_archived.stateChanged.connect(self._load_tickets)
        toolbar.addWidget(self.show_archived)

        act_new.triggered.connect(self._new_ticket)
        act_edit.triggered.connect(self._edit_ticket)
        act_delete.triggered.connect(self._delete_ticket)
        act_refresh.triggered.connect(self._load_tickets)
        self.act_archive.triggered.connect(self._toggle_archive)
        act_settings.triggered.connect(self._open_settings)
        act_db.triggered.connect(self._open_db_menu)
        act_kanban.triggered.connect(self._open_kanban)

        central = QWidget()
        main_layout = QVBoxLayout(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tableau des tickets
        self.table_view = QTableView()
        self.model = TicketTableModel([])
        self.proxy = TicketFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.table_view.setModel(self.proxy)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.selectionModel().selectionChanged.connect(
            self._update_archive_action_label
        )
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_table_context_menu)
        splitter.addWidget(self.table_view)

        # Onglets : Notes / Post-it
        right_tabs = QTabWidget()
        self.tabs = right_tabs
        self.notes_panel = NotesPanel()
        self.postit_board = PostItBoard()
        right_tabs.addTab(self.notes_panel, tr("notes.title"))
        right_tabs.addTab(self.postit_board, tr("postit.title"))
        # panneau détails + onglets
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        self.detail_panel = TicketDetailPanel(on_toggle_resolved=self._toggle_archive)
        right_layout.addWidget(self.detail_panel)
        right_layout.addWidget(right_tabs)
        splitter.addWidget(right_container)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # Barre de recherche + filtres rapides
        filter_bar = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("filter.search"))
        self.search_edit.textChanged.connect(self._apply_filters)
        self.cmb_urgency = QComboBox()
        self._populate_urgency_combo()
        self.cmb_urgency.currentTextChanged.connect(self._apply_filters)
        self.cmb_deadline = QComboBox()
        self._populate_deadline_combo()
        self.cmb_deadline.currentTextChanged.connect(self._apply_filters)
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItem(tr("filter.all"))
        self.cmb_theme.currentTextChanged.connect(self._apply_filters)

        self.lbl_search = QLabel(tr("filter.search"))
        self.lbl_urgency = QLabel(tr("filter.urgency"))
        self.lbl_deadline = QLabel(tr("filter.deadline"))
        self.lbl_theme = QLabel(tr("filter.theme"))

        filter_bar.addWidget(self.lbl_search)
        filter_bar.addWidget(self.search_edit)
        filter_bar.addWidget(self.lbl_urgency)
        filter_bar.addWidget(self.cmb_urgency)
        filter_bar.addWidget(self.lbl_deadline)
        filter_bar.addWidget(self.cmb_deadline)
        filter_bar.addWidget(self.lbl_theme)
        filter_bar.addWidget(self.cmb_theme)
        main_layout.insertLayout(0, filter_bar)
        self.setCentralWidget(central)

    def _init_shortcuts(self):
        from ..utils.settings_store import load_settings
        settings = load_settings()
        self._shortcuts_map = {}
        for sc in getattr(self, "_shortcuts_objs", []):
            sc.deleteLater()
        self._shortcuts_objs = []
        shortcuts_cfg = settings.get("shortcuts", {})

        def bind(seq, handler):
            if not seq:
                return
            qs = QShortcut(QKeySequence(seq), self)
            qs.activated.connect(handler)
            self._shortcuts_objs.append(qs)

        bind(shortcuts_cfg.get("palette", "Ctrl+K"), self._open_command_palette)
        bind(shortcuts_cfg.get("new"), self._new_ticket)
        bind(shortcuts_cfg.get("edit"), self._edit_ticket)
        bind(shortcuts_cfg.get("delete"), self._delete_ticket)
        bind(shortcuts_cfg.get("archive"), self._toggle_archive)
        bind(shortcuts_cfg.get("refresh"), self._load_tickets)
        bind(shortcuts_cfg.get("focus_search"), lambda: (self.search_edit.setFocus(), self.search_edit.selectAll()))
        bind(shortcuts_cfg.get("settings"), self._open_settings)
        bind(shortcuts_cfg.get("kanban"), self._open_kanban)

    def _populate_urgency_combo(self):
        current = self.cmb_urgency.currentData()
        self.cmb_urgency.blockSignals(True)
        self.cmb_urgency.clear()
        self.cmb_urgency.addItem(tr("filter.all"), None)
        self.cmb_urgency.addItem(tr("urgency.low"), "Basse")
        self.cmb_urgency.addItem(tr("urgency.normal"), "Normale")
        self.cmb_urgency.addItem(tr("urgency.high"), "Haute")
        self.cmb_urgency.addItem(tr("urgency.critical"), "Critique")
        if current is not None:
            idx = self.cmb_urgency.findData(current)
            if idx >= 0:
                self.cmb_urgency.setCurrentIndex(idx)
        self.cmb_urgency.blockSignals(False)

    def _populate_deadline_combo(self):
        current = self.cmb_deadline.currentData()
        self.cmb_deadline.blockSignals(True)
        self.cmb_deadline.clear()
        self.cmb_deadline.addItem(tr("filter.all"), "all")
        self.cmb_deadline.addItem(tr("filter.deadline.today"), "today")
        self.cmb_deadline.addItem(tr("filter.deadline.week"), "week")
        self.cmb_deadline.addItem(tr("filter.deadline.overdue"), "overdue")
        if current:
            idx = self.cmb_deadline.findData(current)
            if idx >= 0:
                self.cmb_deadline.setCurrentIndex(idx)
        self.cmb_deadline.blockSignals(False)

    def _load_tickets(self):
        current = self._get_selected_ticket()
        current_id = current.id if current else None
        tickets = ticket_service.get_all_tickets(
            include_archived=self.show_archived.isChecked()
        )
        self.model.set_tickets(tickets)
        self.model.set_theme_colors(theme_service.get_theme_colors())
        self._refresh_theme_filter(tickets)
        self._restore_selection(current_id)
        self._update_archive_action_label()
        self.detail_panel.set_ticket(self._get_selected_ticket())
        self._show_deadline_alerts()
        if hasattr(self.postit_board, "_refresh_wall"):
            self.postit_board._refresh_wall()

    def _get_selected_ticket(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            return None
        proxy_index = indexes[0]
        source_index = self.proxy.mapToSource(proxy_index)
        return self.model.get_ticket_at(source_index.row())

    def _new_ticket(self):
        dlg = TicketFormDialog(self)
        if dlg.exec():
            data = dlg.get_ticket_data()
            ticket_service.create_ticket(**data)
            self._load_tickets()
            self._select_first_row()

    def _edit_ticket(self):
        ticket = self._get_selected_ticket()
        if not ticket:
            QMessageBox.information(self, "Info", tr("dlg.info.select_ticket"))
            return
        dlg = TicketFormDialog(self, ticket=ticket)
        if dlg.exec():
            data = dlg.get_ticket_data()
            ticket.title = data["title"]
            ticket.urgency = data["urgency"]
            ticket.deadline = data["deadline"]
            ticket.theme = data["theme"]
            ticket.description = data["description"]
            ticket_service.update_ticket(ticket)
            self._load_tickets()

    def _toggle_archive(self):
        ticket = self._get_selected_ticket()
        if not ticket:
            QMessageBox.information(self, "Info", tr("dlg.select_ticket"))
            return
        if ticket.id is None:
            return
        if ticket.archived:
            if ticket.id is not None:
                ticket_service.unarchive_ticket(ticket.id)
        else:
            if ticket.id is not None:
                ticket_service.archive_ticket(ticket.id)
        self._load_tickets()

    def _delete_ticket(self):
        ticket = self._get_selected_ticket()
        if not ticket:
            QMessageBox.information(self, "Info", tr("dlg.info.select_ticket"))
            return
        if ticket.id is None:
            return
        reply = QMessageBox.question(
            self,
            tr("dlg.confirmation"),
            tr("dlg.confirm.delete_ticket", id=ticket.id),
        )
        if reply == QMessageBox.StandardButton.Yes:
            ticket_service.delete_ticket(ticket.id)
            self._load_tickets()

    def _update_archive_action_label(self, *args):
        ticket = self._get_selected_ticket()
        if ticket and ticket.archived:
            self.act_archive.setText(tr("menu.restore"))
        else:
            self.act_archive.setText(tr("menu.archive"))
        self.detail_panel.set_ticket(ticket)

    def _select_first_row(self):
        if self.proxy.rowCount() > 0:
            index = self.proxy.index(0, 0)
            self.table_view.selectRow(index.row())
        else:
            self.detail_panel.set_ticket(None)
        self._update_archive_action_label()

    def _restore_selection(self, ticket_id):
        if ticket_id is None:
            self._select_first_row()
            return
        # find in model
        for row in range(self.model.rowCount()):
            t = self.model.get_ticket_at(row)
            if t.id == ticket_id:
                proxy_index = self.proxy.mapFromSource(self.model.index(row, 0))
                if proxy_index.isValid():
                    self.table_view.selectRow(proxy_index.row())
                    self.detail_panel.set_ticket(t)
                    return
        self._select_first_row()

    def _apply_filters(self):
        theme_value = None
        if self.cmb_theme.currentIndex() > 0:
            theme_value = self.cmb_theme.currentText()
        self.proxy.set_filters(
            search_text=self.search_edit.text(),
            urgency=self.cmb_urgency.currentData(),
            deadline_filter=self.cmb_deadline.currentData(),
            theme=theme_value,
        )
        self._select_first_row()

    def _refresh_theme_filter(self, tickets):
        themes = sorted({t.theme for t in tickets if t.theme})
        current = self.cmb_theme.currentText()
        self.cmb_theme.blockSignals(True)
        self.cmb_theme.clear()
        self.cmb_theme.addItem(tr("filter.all"))
        for th in themes:
            self.cmb_theme.addItem(th)
        if current in [tr("filter.all")] + themes:
            self.cmb_theme.setCurrentText(current)
        self.cmb_theme.blockSignals(False)

    def _open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            theme_service.refresh_cache()
            self._load_tickets()
            if getattr(dlg, "language_changed", False):
                i18n.set_language(dlg.settings.get("language", "fr"))
                self._retranslate_ui()
            if getattr(dlg, "data_reset", False):
                self._load_tickets()
                if hasattr(self.notes_panel, "_load_note"):
                    self.notes_panel._load_note()
                if hasattr(self.postit_board, "_load_postits"):
                    self.postit_board._load_postits()
            apply_theme(QApplication.instance(), dlg.settings)

    def _open_command_palette(self):
        actions = [
            ("new", tr("palette.action.new")),
            ("edit", tr("palette.action.edit")),
            ("delete", tr("palette.action.delete")),
            ("archive", tr("palette.action.archive")),
            ("focus_search", tr("palette.action.focus_search")),
            ("refresh", tr("palette.action.refresh")),
            ("settings", tr("palette.action.open_settings")),
            ("kanban", tr("palette.action.kanban")),
        ]
        dlg = CommandPalette(actions, parent=self)
        if dlg.exec():
            action_id = dlg.get_selected_action()
            if not action_id:
                return
            if action_id == "new":
                self._new_ticket()
            elif action_id == "edit":
                self._edit_ticket()
            elif action_id == "delete":
                self._delete_ticket()
            elif action_id == "archive":
                self._toggle_archive()
            elif action_id == "focus_search":
                self.search_edit.setFocus()
                self.search_edit.selectAll()
            elif action_id == "refresh":
                self._load_tickets()
            elif action_id == "settings":
                self._open_settings()
            elif action_id == "kanban":
                self._open_kanban()

    def _open_db_menu(self):
        menu = QTabWidget()  # placeholder to silence lints (unused), not shown
        action = QMessageBox.question(
            self,
            tr("dlg.db.title"),
            tr("dlg.db.question"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Yes
        )
        if action == QMessageBox.StandardButton.Cancel:
            return
        if action == QMessageBox.StandardButton.Yes:
            self._export_db()
        else:
            self._import_db()

    def _show_table_context_menu(self, pos):
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return
        # Align selection with the row that was right-clicked
        self.table_view.selectRow(index.row())
        ticket = self._get_selected_ticket()
        menu = QMenu(self)
        # Reuse existing actions so shortcuts/tooltips stay consistent
        for action in (self.actions_map["edit"], self.actions_map["delete"], self.act_archive):
            action.setEnabled(ticket is not None)
            menu.addAction(action)
        menu.exec(self.table_view.viewport().mapToGlobal(pos))

    def _export_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("dlg.db.export.title"),
            "ticket_app.db",
            "Base SQLite (*.db);;Tous les fichiers (*)"
        )
        if not path:
            return
        try:
            import shutil
            shutil.copyfile(DB_PATH, path)
            QMessageBox.information(self, "Export", tr("dlg.db.export.success", path=path))
        except Exception as e:
            QMessageBox.critical(self, "Export", tr("dlg.db.export.error", err=e))

    def _import_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("dlg.db.import.title"),
            "",
            "Base SQLite (*.db);;Tous les fichiers (*)"
        )
        if not path:
            return
        try:
            import shutil
            shutil.copyfile(path, DB_PATH)
            QMessageBox.information(self, "Import", tr("dlg.db.import.success"))
        except Exception as e:
            QMessageBox.critical(self, "Import", tr("dlg.db.import.error", err=e))

    def _show_deadline_alerts(self):
        if self._alerts_shown:
            return
        from ..utils.settings_store import get_alert_settings
        settings = get_alert_settings()
        if not any(settings.values()):
            return
        tickets = ticket_service.get_all_tickets(include_archived=False)
        from datetime import datetime, date, timedelta
        today = date.today()
        overdue = []
        dayof = []
        before = []
        for t in tickets:
            if not t.deadline:
                continue
            try:
                d = datetime.strptime(t.deadline, "%Y-%m-%d").date()
            except Exception:
                continue
            if settings.get("overdue") and d < today:
                overdue.append(t)
            elif settings.get("day_of") and d == today:
                dayof.append(t)
            elif settings.get("one_day_before") and d == today + timedelta(days=1):
                before.append(t)
        msgs = []
        if before:
            msgs.append(tr("alerts.before", n=len(before)))
        if dayof:
            msgs.append(tr("alerts.dayof", n=len(dayof)))
        if overdue:
            msgs.append(tr("alerts.overdue", n=len(overdue)))
        if msgs:
            QMessageBox.warning(self, tr("alerts.title"), "\n".join(msgs))
            self._alerts_shown = True

    def _retranslate_ui(self):
        self.setWindowTitle(tr("app.title"))
        self.actions_map["new"].setText(tr("menu.new_ticket"))
        self.actions_map["edit"].setText(tr("menu.edit"))
        self.actions_map["delete"].setText(tr("menu.delete"))
        self.actions_map["refresh"].setText(tr("menu.refresh"))
        self.actions_map["archive"].setText(tr("menu.archive"))
        self.actions_map["settings"].setText(tr("menu.settings"))
        self.actions_map["db"].setText(tr("menu.db"))
        self.actions_map["kanban"].setText(tr("kanban.title"))
        self.show_archived.setText(tr("menu.show_archived"))

        self.tabs.setTabText(0, tr("notes.title"))
        self.tabs.setTabText(1, tr("postit.title"))

        self.search_edit.setPlaceholderText(tr("filter.search"))
        self.lbl_search.setText(tr("filter.search"))
        self.lbl_urgency.setText(tr("filter.urgency"))
        self.lbl_deadline.setText(tr("filter.deadline"))
        self.lbl_theme.setText(tr("filter.theme"))

        self._populate_urgency_combo()
        self._populate_deadline_combo()
        tickets = ticket_service.get_all_tickets(
            include_archived=self.show_archived.isChecked()
        )
        self.model.set_theme_colors(theme_service.get_theme_colors())
        self._refresh_theme_filter(tickets)
        self._apply_filters()
        self._update_archive_action_label()
        if hasattr(self.detail_panel, "retranslate"):
            self.detail_panel.retranslate()
        if hasattr(self.notes_panel, "retranslate"):
            self.notes_panel.retranslate()
        if hasattr(self.postit_board, "retranslate"):
            self.postit_board.retranslate()
        if hasattr(self.model, "refresh_headers"):
            self.model.refresh_headers()
        self._init_shortcuts()
        self._init_auto_refresh()

    def _open_kanban(self):
        dlg = KanbanDialog(self)
        dlg.exec()

    def _init_auto_refresh(self):
        if hasattr(self, "_refresh_timer") and self._refresh_timer:
            self._refresh_timer.stop()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(30000)  # 30s
        self._refresh_timer.timeout.connect(self._load_tickets)
        self._refresh_timer.start()
