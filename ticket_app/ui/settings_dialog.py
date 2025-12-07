from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QColorDialog, QLineEdit, QSpinBox, QFormLayout, QMessageBox, QCheckBox, QGroupBox
)

from ..services.theme_service import theme_service
from ..utils.settings_store import load_settings, save_settings


class ThemeEditDialog(QDialog):
    """Dialog to add/edit a theme."""

    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.setWindowTitle("Thème")
        self.theme = theme
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit(theme.name if theme else "")
        self.color_label = QLabel(theme.color if theme else "#cccccc")
        btn_color = QPushButton("Choisir couleur")
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

        form.addRow("Nom", self.name_edit)
        form.addRow("Couleur", color_row)
        form.addRow("Pos X", self.spin_x)
        form.addRow("Pos Y", self.spin_y)
        form.addRow("Largeur", self.spin_w)
        form.addRow("Hauteur", self.spin_h)
        layout.addLayout(form)

        btns = QHBoxLayout()
        ok = QPushButton("OK"); cancel = QPushButton("Annuler")
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
        self.setWindowTitle("Paramètres")
        self.settings = load_settings()
        self._init_ui()
        self._load_alerts()
        self._load_themes()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Alerts
        alerts_group = QGroupBox("Alertes échéances")
        alerts_layout = QVBoxLayout(alerts_group)
        self.chk_before = QCheckBox("1 jour avant")
        self.chk_dayof = QCheckBox("Jour J")
        self.chk_overdue = QCheckBox("En retard")
        alerts_layout.addWidget(self.chk_before)
        alerts_layout.addWidget(self.chk_dayof)
        alerts_layout.addWidget(self.chk_overdue)
        layout.addWidget(alerts_group)

        # Themes
        theme_group = QGroupBox("Thèmes et couleurs")
        theme_layout = QVBoxLayout(theme_group)
        self.theme_list = QListWidget()
        self.theme_list.itemDoubleClicked.connect(self._edit_theme)
        theme_layout.addWidget(self.theme_list)
        btn_row = QHBoxLayout()
        btn_new = QPushButton("Nouveau")
        btn_edit = QPushButton("Modifier")
        btn_delete = QPushButton("Supprimer")
        btn_new.clicked.connect(self._new_theme)
        btn_edit.clicked.connect(self._edit_theme)
        btn_delete.clicked.connect(self._delete_theme)
        btn_row.addWidget(btn_new)
        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_delete)
        theme_layout.addLayout(btn_row)
        layout.addWidget(theme_group)

        # footer
        footer = QHBoxLayout()
        ok = QPushButton("Fermer")
        ok.clicked.connect(self.accept)
        footer.addStretch()
        footer.addWidget(ok)
        layout.addLayout(footer)

    def _load_alerts(self):
        alerts = self.settings.get("alerts", {})
        self.chk_before.setChecked(alerts.get("one_day_before", True))
        self.chk_dayof.setChecked(alerts.get("day_of", True))
        self.chk_overdue.setChecked(alerts.get("overdue", True))

    def _load_themes(self):
        self.theme_list.clear()
        self._themes = theme_service.get_all()
        for t in self._themes:
            self.theme_list.addItem(f"{t.name} ({t.color}) [{t.x},{t.y}] {t.width}x{t.height}")

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
                QMessageBox.warning(self, "Validation", "Nom requis.")
                return
            theme_service.create(**data)
            self._load_themes()

    def _edit_theme(self):
        theme = self._selected_theme()
        if not theme:
            return
        dlg = ThemeEditDialog(self, theme=theme)
        if dlg.exec():
            data = dlg.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Validation", "Nom requis.")
                return
            theme.name = data["name"]
            theme.color = data["color"]
            theme.x = data["x"]; theme.y = data["y"]
            theme.width = data["width"]; theme.height = data["height"]
            theme_service.update(theme)
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
        save_settings(self.settings)
        super().accept()
