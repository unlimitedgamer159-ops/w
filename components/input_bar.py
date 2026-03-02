from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QWidget


class InputBar(QWidget):
    submit = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Ask Stremini...")
        send = QPushButton("Send")
        send.clicked.connect(self._submit)
        layout.addWidget(self.editor, 1)
        layout.addWidget(send)

    def _submit(self) -> None:
        value = self.editor.toPlainText().strip()
        if value:
            self.submit.emit(value)
            self.editor.clear()
