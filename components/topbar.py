from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class TopBar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.status = QLabel("Ready")
        home = QPushButton("Home")
        clear = QPushButton("Clear")
        home.clicked.connect(self._home_requested)
        clear.clicked.connect(self._clear_requested)
        layout.addWidget(self.status)
        layout.addStretch()
        layout.addWidget(home)
        layout.addWidget(clear)
        self._clear_callbacks = []
        self._home_callbacks = []

    def on_clear(self, callback) -> None:
        self._clear_callbacks.append(callback)

    def on_home(self, callback) -> None:
        self._home_callbacks.append(callback)

    def _clear_requested(self) -> None:
        for callback in self._clear_callbacks:
            callback()

    def _home_requested(self) -> None:
        for callback in self._home_callbacks:
            callback()

    def set_running(self, running: bool) -> None:
        self.status.setText("Running" if running else "Ready")
