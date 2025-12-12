from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QColorDialog, QLineEdit, QSpinBox, QFormLayout, QMessageBox, QCheckBox, QGroupBox, QComboBox
)
import shutil
from pathlib import Path

from ..services.theme_service import theme_service
from ..utils.settings_store import load_settings, save_settings
from ..utils.i18n import tr, available_languages
from ..config import DB_PATH, DATA_DIR, LOG_DIR
from ..db.database import init_db
from ..utils.settings_store import SETTINGS_PATH
from ..utils.theme_manager import get_appearance_settings


class ThemeEditDialog(QDialog):
    """Dialog to add/edit a theme."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.setWindowTitle(tr("theme.dialog.title"))
        self.theme = theme
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit(theme.name if theme else "")
        self.color_label = QLabel(theme.color if theme else "#cccccc")
        btn_color = QPushButton(tr("theme.pick_color"))
        btn_color.clicked.connect(self._choose_color)
        color_row = QHBoxLayout()
        color_row.addWidget(self.color_label)
        color_row.addWidget(btn_color)

        self.spin_x = QSpinBox(); self.spin_x.setRange(-10000, 10000)
        self.spin_y = QSpinBox(); self.spin_y.setRange(-10000, 10000)
        self.spin_w = QSpinBox(); self.spin_w.setRange(0, 5000)
        self.spin_h = QSpinBox(); self.spin_h.setRange(0, 5000)
        if theme:
            self.spin_x.setValue(theme.x)
            self.spin_y.setValue(theme.y)
            self.spin_w.setValue(theme.width)
            self.spin_h.setValue(theme.height)

        form.addRow(tr("theme.name"), self.name_edit)
        form.addRow(tr("theme.color"), color_row)
        form.addRow(tr("theme.posx"), self.spin_x)
        form.addRow(tr("theme.posy"), self.spin_y)
        form.addRow(tr("theme.width"), self.spin_w)
        form.addRow(tr("theme.height"), self.spin_h)
        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = QPushButton(tr("dlg.ok")); cancel = QPushButton(tr("dlg.cancel"))
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addWidget(cancel)
        layout.addLayout(btns)

    def _choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_label.setText(color.name())

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "color": self.color_label.text(),
            "x": self.spin_x.value(),
            "y": self.spin_y.value(),
            "width": self.spin_w.value(),
            "height": self.spin_h.value(),
        }


class SettingsDialog(QDialog):
    """Settings dialog for themes and alerts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings.title"))
        self.settings = load_settings()
        self._initial_language = self.settings.get("language", "fr")
        self.language_changed = False
        self.data_reset = False
        self._init_ui()
        self._load_alerts()
        self._load_themes()
        self._load_shortcuts()
        self._load_appearance()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Alerts
        alerts_group = QGroupBox(tr("settings.alerts"))
        alerts_layout = QVBoxLayout(alerts_group)
        self.chk_before = QCheckBox(tr("settings.alerts.before"))
        self.chk_dayof = QCheckBox(tr("settings.alerts.dayof"))
        self.chk_overdue = QCheckBox(tr("settings.alerts.overdue"))
        alerts_layout.addWidget(self.chk_before)
        alerts_layout.addWidget(self.chk_dayof)
        alerts_layout.addWidget(self.chk_overdue)
        layout.addWidget(alerts_group)

        # Themes
        theme_group = QGroupBox(tr("settings.themes"))
        theme_layout = QVBoxLayout(theme_group)
        self.theme_list = QListWidget()
        self.theme_list.itemDoubleClicked.connect(self._edit_theme)
        theme_layout.addWidget(self.theme_list)
        btn_row = QHBoxLayout()
        btn_new = QPushButton(tr("settings.new"))
        btn_edit = QPushButton(tr("settings.edit"))
        btn_delete = QPushButton(tr("settings.delete"))
        btn_new.clicked.connect(self._new_theme)
        btn_edit.clicked.connect(self._edit_theme)
        btn_delete.clicked.connect(self._delete_theme)
        btn_row.addWidget(btn_new)
        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_delete)
        theme_layout.addLayout(btn_row)
        layout.addWidget(theme_group)

        # Language
        lang_group = QGroupBox(tr("settings.language"))
        lang_layout = QVBoxLayout(lang_group)
        self.lang_combo = QComboBox()
        for code, label in available_languages().items():
            self.lang_combo.addItem(label, code)
        lang_layout.addWidget(self.lang_combo)
        layout.addWidget(lang_group)

        # Shortcuts
        shortcuts_group = QGroupBox(tr("shortcuts.title"))
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        shortcuts_layout.addWidget(QLabel(tr("shortcuts.info")))
        form = QFormLayout()
        self.shortcut_fields = {}
        self._shortcut_defs = [
            ("palette", tr("shortcuts.palette")),
            ("new", tr("shortcuts.new")),
            ("edit", tr("shortcuts.edit")),
            ("delete", tr("shortcuts.delete")),
            ("archive", tr("shortcuts.archive")),
            ("refresh", tr("shortcuts.refresh")),
            ("focus_search", tr("shortcuts.focus_search")),
            ("settings", tr("shortcuts.settings")),
        ]
        for key, label in self._shortcut_defs:
            edit = QLineEdit()
            self.shortcut_fields[key] = edit
            form.addRow(label, edit)
        shortcuts_layout.addLayout(form)
        layout.addWidget(shortcuts_group)

        # Appearance
        appearance_group = QGroupBox(tr("appearance.title"))
        appearance_layout = QVBoxLayout(appearance_group)
        app_form = QFormLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(tr("appearance.mode.light"), "light")
        self.mode_combo.addItem(tr("appearance.mode.dark"), "dark")
        self.kanban_bg_edit = QLineEdit()
        btn_kanban = QPushButton(tr("appearance.pick_color"))
        btn_kanban.clicked.connect(lambda: self._pick_color(self.kanban_bg_edit))
        row_kanban = QHBoxLayout()
        row_kanban.addWidget(self.kanban_bg_edit)
        row_kanban.addWidget(btn_kanban)
        app_form.addRow(tr("appearance.mode"), self.mode_combo)
        app_form.addRow(tr("appearance.kanban_column"), row_kanban)
        appearance_layout.addLayout(app_form)
        layout.addWidget(appearance_group)

        # Reset data
        reset_group = QGroupBox(tr("settings.reset.title"))
        reset_layout = QVBoxLayout(reset_group)
        self.reset_btn = QPushButton(tr("settings.reset.button"))
        self.reset_btn.clicked.connect(self._reset_data)
        reset_layout.addWidget(self.reset_btn)
        layout.addWidget(reset_group)

        # footer
        footer = QHBoxLayout()
        ok = QPushButton(tr("settings.close"))
        ok.clicked.connect(self.accept)
        footer.addStretch()
        footer.addWidget(ok)
        layout.addLayout(footer)

    def _load_alerts(self):
        alerts = self.settings.get("alerts", {})
        self.chk_before.setChecked(alerts.get("one_day_before", True))
        self.chk_dayof.setChecked(alerts.get("day_of", True))
        self.chk_overdue.setChecked(alerts.get("overdue", True))
        current_lang = self.settings.get("language", "fr")
        idx = self.lang_combo.findData(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

    def _load_themes(self):
        self.theme_list.clear()
        self._themes = theme_service.get_all()
        for t in self._themes:
            self.theme_list.addItem(f"{t.name} ({t.color}) [{t.x},{t.y}] {t.width}x{t.height}")

    def _load_shortcuts(self):
        shortcuts = self.settings.get("shortcuts", {})
        for key, edit in self.shortcut_fields.items():
            edit.setText(shortcuts.get(key, ""))

    def _load_appearance(self):
        appearance = get_appearance_settings(self.settings)
        mode = appearance.get("mode", "light")
        idx = self.mode_combo.findData(mode)
        if idx >= 0:
            self.mode_combo.setCurrentIndex(idx)
        self.kanban_bg_edit.setText(appearance.get("kanban_column", ""))

    def _pick_color(self, target_edit: QLineEdit):
        color = QColorDialog.getColor()
        if color.isValid():
            target_edit.setText(color.name())

    def _selected_theme(self):
        row = self.theme_list.currentRow()
        if row < 0 or row >= len(self._themes):
            return None
        return self._themes[row]

    def _new_theme(self):
        dlg = ThemeEditDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            if not data["name"]:
                QMessageBox.warning(self, tr("settings.title"), tr("validation.name_required"))
                return
            theme_service.create(**data)
            self._load_themes()

    def _edit_theme(self):
        theme = self._selected_theme()
        if not theme:
            return
        old_name = theme.name
        dlg = ThemeEditDialog(self, theme=theme)
        if dlg.exec():
            data = dlg.get_data()
            if not data["name"]:
                QMessageBox.warning(self, tr("settings.title"), tr("validation.name_required"))
                return
            theme.name = data["name"]
            theme.color = data["color"]
            theme.x = data["x"]; theme.y = data["y"]
            theme.width = data["width"]; theme.height = data["height"]
            theme_service.update(theme, old_name=old_name)
            self._load_themes()

    def _delete_theme(self):
        theme = self._selected_theme()
        if not theme:
            return
        theme_service.delete(theme.id)
        self._load_themes()

    def accept(self):
        self.settings["alerts"] = {
            "one_day_before": self.chk_before.isChecked(),
            "day_of": self.chk_dayof.isChecked(),
            "overdue": self.chk_overdue.isChecked(),
        }
        new_lang = self.lang_combo.currentData()
        self.settings["language"] = new_lang
        self.language_changed = new_lang != self._initial_language
        self.settings["shortcuts"] = {
            key: edit.text().strip()
            for key, edit in self.shortcut_fields.items()
            if edit.text().strip()
        }
        self.settings["appearance"] = {
            "mode": self.mode_combo.currentData(),
            "kanban_column": self.kanban_bg_edit.text().strip() or "#f6f6f6",
        }
        save_settings(self.settings)
        super().accept()

    def _reset_data(self):
        reply = QMessageBox.question(
            self,
            tr("settings.reset.title"),
            tr("settings.reset.confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            # Remove DB and settings
            if DB_PATH.exists():
                DB_PATH.unlink()
            if SETTINGS_PATH.exists():
                SETTINGS_PATH.unlink()
            # Clear data and logs dirs
            if DATA_DIR.exists():
                shutil.rmtree(DATA_DIR)
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if LOG_DIR.exists():
                shutil.rmtree(LOG_DIR)
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            init_db()
            QMessageBox.information(self, tr("settings.reset.title"), tr("settings.reset.success"))
            self.data_reset = True
        except Exception as e:
            QMessageBox.critical(self, tr("settings.reset.title"), tr("settings.reset.error", err=e))
