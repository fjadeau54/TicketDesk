from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QComboBox
)

DEFAULT_COLORS = [
    ("Jaune", "#F7E264"),
    ("Vert", "#C2E08A"),
    ("Bleu", "#9CD5FF"),
    ("Rose", "#F6B3D2"),
    ("Orange", "#FFCC99"),
    ("Violet", "#CBB2FF"),
    ("Gris", "#E0E0E0"),
]

class PostItEditDialog(QDialog):

    def __init__(self, parent=None, content: str = "", tags: str = "", color: str = "#F7E264"):
        super().__init__(parent)
        self.setWindowTitle("Post-it")

        layout = QVBoxLayout(self)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(content)
        layout.addWidget(self.text_edit)

        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags"))
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("#bug, #ui, #todo")
        self.tags_edit.setText(tags)
        tags_layout.addWidget(self.tags_edit)
        layout.addLayout(tags_layout)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Couleur"))
        self.color_combo = QComboBox()
        for label, val in DEFAULT_COLORS:
            self.color_combo.addItem(label, val)
        self.color_combo.setEditable(True)
        self.color_combo.setCurrentText(color)
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Annuler")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_content(self) -> str:
        return self.text_edit.toPlainText()

    def get_tags(self) -> str:
        return self.tags_edit.text()

    def get_color(self) -> str:
        return self.color_combo.currentText()

    def get_data(self) -> dict:
        return {
            "content": self.get_content(),
            "tags": self.get_tags(),
            "color": self.get_color()
        }
