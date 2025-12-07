from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox,
    QLineEdit, QComboBox, QListWidgetItem, QFrame, QListWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette

from ..services.postit_service import postit_service
from .postit_edit_dialog import PostItEditDialog


class PostItCard(QFrame):
    """Small colored card showing a post-it with its tags."""

    def __init__(self, postit, parent=None):
        super().__init__(parent)
        self.setObjectName("PostItCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setAutoFillBackground(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.content_lbl = QLabel(postit.content)
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setAlignment(Qt.AlignTop)
        self.tags_lbl = QLabel(self._format_tags(postit.tags))
        self.tags_lbl.setStyleSheet("color: #444; font-size: 11px;")
        layout.addWidget(self.content_lbl)
        layout.addWidget(self.tags_lbl)
        layout.addStretch()
        self.apply_color(postit.color)

    @staticmethod
    def _format_tags(tags: str) -> str:
        parts = [t.strip().lstrip("#") for t in tags.split(",") if t.strip()]
        return " ".join(f"#{t}" for t in parts)

    def apply_color(self, color_value: str):
        palette = self.palette()
        base_color = QColor(color_value)
        if not base_color.isValid():
            base_color = QColor("#F7E264")
        palette.setColor(QPalette.Window, base_color.lighter(105))
        self.setPalette(palette)


class PostItListWidget(QListWidget):
    """List widget supporting drag and drop, emitting when order changes."""
    orderChanged = Signal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.orderChanged.emit()


class PostItBoard(QWidget):
    """Enhanced Post-it wall with tags, filters, and drag-and-drop ordering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_postits()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addWidget(QLabel("Post-it (mur filtrable)"))
        header.addStretch()
        layout.addLayout(header)

        filter_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filtrer par texte ou #tag")
        self.search_edit.textChanged.connect(self._refresh_wall)
        self.color_filter = QComboBox()
        self.color_filter.addItem("Toutes les couleurs", None)
        self.color_filter.currentIndexChanged.connect(self._refresh_wall)
        filter_row.addWidget(self.search_edit)
        filter_row.addWidget(self.color_filter)
        layout.addLayout(filter_row)

        self.list_widget = PostItListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setWrapping(True)
        self.list_widget.setMovement(QListWidget.Snap)
        self.list_widget.setSpacing(12)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("Nouveau")
        self.btn_edit = QPushButton("Modifier")
        self.btn_delete = QPushButton("Supprimer")
        refresh_btn = QPushButton("Rafraîchir")
        btn_row.addWidget(self.btn_new)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        refresh_btn.clicked.connect(self._load_postits)
        self.btn_new.clicked.connect(self._new_postit)
        self.btn_edit.clicked.connect(self._edit_postit)
        self.btn_delete.clicked.connect(self._delete_postit)
        self.list_widget.itemDoubleClicked.connect(lambda _: self._edit_postit())
        self.list_widget.orderChanged.connect(self._persist_order)

    def _load_postits(self):
        self._postits = postit_service.get_all_postits()
        self._refresh_color_filter()
        self._refresh_wall()

    def _refresh_color_filter(self):
        selected = self.color_filter.currentData()
        colors = []
        for p in self._postits:
            if p.color and p.color not in colors:
                colors.append(p.color)
        self.color_filter.blockSignals(True)
        self.color_filter.clear()
        self.color_filter.addItem("Toutes les couleurs", None)
        for c in colors:
            self.color_filter.addItem(c, c)
        # restore selection if possible
        if selected in colors:
            self.color_filter.setCurrentIndex(colors.index(selected) + 1)
        self.color_filter.blockSignals(False)

    def _refresh_wall(self):
        search = self.search_edit.text().lower().strip()
        color_filter = self.color_filter.currentData()
        self.list_widget.clear()
        filtered = []
        for p in self._postits:
            haystack = f"{p.content} {p.tags}".lower()
            if search and search not in haystack:
                continue
            if color_filter and p.color != color_filter:
                continue
            filtered.append(p)

        self._filtered_postits = filtered
        for p in filtered:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, p.id)
            card = PostItCard(p)
            item.setSizeHint(card.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)

    def _get_selected(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(getattr(self, "_filtered_postits", [])):
            return None
        return self._filtered_postits[row]

    def _new_postit(self):
        dlg = PostItEditDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            content = data["content"].strip()
            if not content:
                return
            postit_service.create_postit(
                content=content,
                tags=data["tags"].strip(),
                color=data["color"].strip() or "yellow"
            )
            self._load_postits()

    def _edit_postit(self):
        postit = self._get_selected()
        if not postit:
            QMessageBox.information(self, "Info", "Sélectionne un post-it.")
            return
        dlg = PostItEditDialog(self, content=postit.content, tags=postit.tags, color=postit.color)
        if dlg.exec():
            data = dlg.get_data()
            content = data["content"].strip()
            if not content:
                return
            postit.content = content
            postit.tags = data["tags"].strip()
            postit.color = data["color"].strip() or postit.color
            postit_service.update_postit(postit)
            self._load_postits()

    def _delete_postit(self):
        postit = self._get_selected()
        if not postit:
            QMessageBox.information(self, "Info", "Sélectionne un post-it.")
            return
        postit_service.delete_postit(postit.id)
        self._load_postits()

    def _persist_order(self):
        visible_ids = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            pid = item.data(Qt.UserRole)
            if pid is not None:
                visible_ids.append(pid)
        hidden_ids = [p.id for p in self._postits if p.id not in visible_ids]
        postit_service.reorder_postits(visible_ids + hidden_ids)
        self._load_postits()
