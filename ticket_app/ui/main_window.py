from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar,
    QTableView, QSplitter, QTabWidget, QMessageBox, QCheckBox,
    QLineEdit, QComboBox, QHBoxLayout, QLabel, QFileDialog
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from ..services.ticket_service import ticket_service
from ..services.theme_service import theme_service
from .ticket_table_model import TicketTableModel
from .ticket_form_dialog import TicketFormDialog
from .notes_panel import NotesPanel
from .postit_board import PostItBoard
from .ticket_detail_panel import TicketDetailPanel
from .ticket_filter_proxy import TicketFilterProxy
from .settings_dialog import SettingsDialog
from ..config import DB_PATH

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ticket Manager")
        self._alerts_shown = False

        self._init_ui()
        self._load_tickets()

    def _init_ui(self):
        toolbar = QToolBar("Actions")
        self.addToolBar(toolbar)

        act_new = QAction("Nouveau ticket", self)
        act_edit = QAction("Modifier", self)
        act_delete = QAction("Supprimer", self)
        act_refresh = QAction("Rafraîchir", self)
        self.act_archive = QAction("Archiver", self)
        act_settings = QAction("Paramètres", self)
        act_db = QAction("BDD", self)

        toolbar.addAction(act_new)
        toolbar.addAction(act_edit)
        toolbar.addAction(act_delete)
        toolbar.addAction(self.act_archive)
        toolbar.addSeparator()
        toolbar.addAction(act_refresh)
        toolbar.addAction(act_settings)
        toolbar.addAction(act_db)

        self.show_archived = QCheckBox("Afficher archivés")
        self.show_archived.stateChanged.connect(self._load_tickets)
        toolbar.addWidget(self.show_archived)

        act_new.triggered.connect(self._new_ticket)
        act_edit.triggered.connect(self._edit_ticket)
        act_delete.triggered.connect(self._delete_ticket)
        act_refresh.triggered.connect(self._load_tickets)
        self.act_archive.triggered.connect(self._toggle_archive)
        act_settings.triggered.connect(self._open_settings)
        act_db.triggered.connect(self._open_db_menu)

        central = QWidget()
        main_layout = QVBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)

        # Tableau des tickets
        self.table_view = QTableView()
        self.model = TicketTableModel([])
        self.proxy = TicketFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.table_view.setModel(self.proxy)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.selectionModel().selectionChanged.connect(
            self._update_archive_action_label
        )
        splitter.addWidget(self.table_view)

        # Onglets : Notes / Post-it
        right_tabs = QTabWidget()
        self.notes_panel = NotesPanel()
        self.postit_board = PostItBoard()
        right_tabs.addTab(self.notes_panel, "Bloc-notes")
        right_tabs.addTab(self.postit_board, "Post-it")
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
        self.search_edit.setPlaceholderText("Rechercher (titre, thème, description)")
        self.search_edit.textChanged.connect(self._apply_filters)
        self.cmb_urgency = QComboBox()
        self.cmb_urgency.addItems(["Tous", "Basse", "Normale", "Haute", "Critique"])
        self.cmb_urgency.currentTextChanged.connect(self._apply_filters)
        self.cmb_deadline = QComboBox()
        self.cmb_deadline.addItems(["Tous", "Aujourd'hui", "Cette semaine", "En retard"])
        self.cmb_deadline.currentTextChanged.connect(self._apply_filters)
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItem("Tous")
        self.cmb_theme.currentTextChanged.connect(self._apply_filters)

        filter_bar.addWidget(QLabel("Recherche"))
        filter_bar.addWidget(self.search_edit)
        filter_bar.addWidget(QLabel("Urgence"))
        filter_bar.addWidget(self.cmb_urgency)
        filter_bar.addWidget(QLabel("Échéance"))
        filter_bar.addWidget(self.cmb_deadline)
        filter_bar.addWidget(QLabel("Thème"))
        filter_bar.addWidget(self.cmb_theme)
        main_layout.insertLayout(0, filter_bar)
        self.setCentralWidget(central)

    def _load_tickets(self):
        tickets = ticket_service.get_all_tickets(
            include_archived=self.show_archived.isChecked()
        )
        self.model.set_tickets(tickets)
        self.model.set_theme_colors(theme_service.get_theme_colors())
        self._refresh_theme_filter(tickets)
        self._update_archive_action_label()
        self.detail_panel.set_ticket(self._get_selected_ticket())
        self._show_deadline_alerts()

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
            QMessageBox.information(self, "Info", "Sélectionne un ticket.")
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
            QMessageBox.information(self, "Info", "Sélectionne un ticket.")
            return
        if ticket.archived:
            ticket_service.unarchive_ticket(ticket.id)
        else:
            ticket_service.archive_ticket(ticket.id)
        self._load_tickets()

    def _delete_ticket(self):
        ticket = self._get_selected_ticket()
        if not ticket:
            QMessageBox.information(self, "Info", "Sélectionne un ticket.")
            return
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Supprimer le ticket #{ticket.id} ?",
        )
        if reply == QMessageBox.Yes:
            ticket_service.delete_ticket(ticket.id)
            self._load_tickets()

    def _update_archive_action_label(self, *args):
        ticket = self._get_selected_ticket()
        if ticket and ticket.archived:
            self.act_archive.setText("Restaurer")
        else:
            self.act_archive.setText("Archiver")
        self.detail_panel.set_ticket(ticket)

    def _select_first_row(self):
        if self.proxy.rowCount() > 0:
            index = self.proxy.index(0, 0)
            self.table_view.selectRow(index.row())
        else:
            self.detail_panel.set_ticket(None)

    def _apply_filters(self):
        self.proxy.set_filters(
            search_text=self.search_edit.text(),
            urgency=self.cmb_urgency.currentText(),
            deadline_filter=self.cmb_deadline.currentText(),
            theme=self.cmb_theme.currentText(),
        )
        self._select_first_row()

    def _refresh_theme_filter(self, tickets):
        themes = sorted({t.theme for t in tickets if t.theme})
        current = self.cmb_theme.currentText()
        self.cmb_theme.blockSignals(True)
        self.cmb_theme.clear()
        self.cmb_theme.addItem("Tous")
        for th in themes:
            self.cmb_theme.addItem(th)
        if current in ["Tous"] + themes:
            self.cmb_theme.setCurrentText(current)
        self.cmb_theme.blockSignals(False)

    def _open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            theme_service.refresh_cache()
            self._load_tickets()

    def _open_db_menu(self):
        menu = QTabWidget()  # placeholder to silence lints (unused), not shown
        action = QMessageBox.question(
            self,
            "Base de données",
            "Voulez-vous exporter la base ?\n\nCliquez Non pour importer.",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        if action == QMessageBox.Cancel:
            return
        if action == QMessageBox.Yes:
            self._export_db()
        else:
            self._import_db()

    def _export_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la base",
            "ticket_app.db",
            "Base SQLite (*.db);;Tous les fichiers (*)"
        )
        if not path:
            return
        try:
            import shutil
            shutil.copyfile(DB_PATH, path)
            QMessageBox.information(self, "Export", f"Base exportée vers :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export", f"Échec de l'export : {e}")

    def _import_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer une base",
            "",
            "Base SQLite (*.db);;Tous les fichiers (*)"
        )
        if not path:
            return
        try:
            import shutil
            shutil.copyfile(path, DB_PATH)
            QMessageBox.information(self, "Import", "Base importée.\nRedémarre l'application pour prendre en compte.")
        except Exception as e:
            QMessageBox.critical(self, "Import", f"Échec de l'import : {e}")

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
            msgs.append(f"1 jour avant : {len(before)} ticket(s)")
        if dayof:
            msgs.append(f"Aujourd'hui : {len(dayof)} ticket(s)")
        if overdue:
            msgs.append(f"En retard : {len(overdue)} ticket(s)")
        if msgs:
            QMessageBox.warning(self, "Alertes échéances", "\n".join(msgs))
            self._alerts_shown = True
