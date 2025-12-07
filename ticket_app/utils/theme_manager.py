from __future__ import annotations

from PySide6.QtWidgets import QApplication


def _light_qss(table_bg: str, kanban_column: str) -> str:
    return f"""
    QWidget {{
        background: #f7f7f7;
        color: #222;
        font-size: 13px;
    }}
    QTableView {{
        background: {table_bg};
        alternate-background-color: #f2f2f2;
        gridline-color: #ccc;
    }}
    QHeaderView::section {{
        background: #e8e8e8;
        padding: 4px;
        border: 1px solid #d0d0d0;
    }}
    QListWidget::item:selected, QTableView::item:selected {{
        background: #cde5ff;
        color: #000;
    }}
    QWidget#KanbanColumn {{
        background: {kanban_column};
        border: 1px solid #d9d9d9;
        border-radius: 6px;
        padding: 6px;
    }}
    """


def _dark_qss(table_bg: str, kanban_column: str) -> str:
    return f"""
    QWidget {{
        background: #1f1f24;
        color: #f1f1f1;
        font-size: 13px;
    }}
    QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
        background: #2a2a30;
        border: 1px solid #3c3c45;
        color: #f1f1f1;
    }}
    QTableView {{
        background: {table_bg};
        alternate-background-color: #2b2b33;
        gridline-color: #3a3a44;
    }}
    QHeaderView::section {{
        background: #2b2b33;
        padding: 4px;
        border: 1px solid #3a3a44;
    }}
    QListWidget::item:selected, QTableView::item:selected {{
        background: #365172;
        color: #fff;
    }}
    QPushButton {{
        background: #2f2f36;
        border: 1px solid #41414d;
        padding: 6px 10px;
    }}
    QPushButton:hover {{
        background: #3b3b45;
    }}
    QWidget#KanbanColumn {{
        background: {kanban_column};
        border: 1px solid #3a3a44;
        border-radius: 6px;
        padding: 6px;
    }}
    """


def apply_theme(app: QApplication, settings: dict):
    appearance = settings.get("appearance", {})
    mode = appearance.get("mode", "light")
    table_bg = "#ffffff" if mode == "light" else "#2a2a30"
    default_kanban = "#f6f6f6" if mode == "light" else "#2a2a30"
    kanban_col = appearance.get("kanban_column", default_kanban) or default_kanban
    qss = _light_qss(table_bg, kanban_col) if mode == "light" else _dark_qss(table_bg, kanban_col)
    app.setStyleSheet(qss)


def get_appearance_settings(settings: dict) -> dict:
    return settings.get("appearance", {})
