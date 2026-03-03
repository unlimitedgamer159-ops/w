from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from config import AGENT_MODES


class Sidebar(QFrame):
    agent_changed = pyqtSignal(str)
    mode_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Sidebar")
        self._active_agent = "research"

        layout = QVBoxLayout(self)
        logo = QLabel("Stremini")
        logo.setStyleSheet("font-size: 26px; font-family: 'Lora'; font-weight: 700;")
        layout.addWidget(logo)

        self.agent_container = QWidget()
        self.agent_grid = QGridLayout(self.agent_container)
        layout.addWidget(self.agent_container)

        self.mode_container = QWidget()
        self.mode_grid = QGridLayout(self.mode_container)
        layout.addWidget(self.mode_container)
        layout.addStretch()

        self._render_agents()
        self._render_modes(self._active_agent)

    def _render_agents(self) -> None:
        agents = list(AGENT_MODES.keys())
        for idx, agent in enumerate(agents):
            button = QPushButton(agent.replace("_", " ").title())
            button.clicked.connect(lambda _=False, a=agent: self.select_agent(a))
            self.agent_grid.addWidget(button, idx // 2, idx % 2)

    def _render_modes(self, agent: str) -> None:
        while self.mode_grid.count():
            item = self.mode_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, mode in enumerate(AGENT_MODES[agent]):
            button = QPushButton(mode)
            button.clicked.connect(lambda _=False, m=mode: self.mode_changed.emit(m))
            self.mode_grid.addWidget(button, idx // 2, idx % 2)

    def select_agent(self, agent: str) -> None:
        self._active_agent = agent
        self._render_modes(agent)
        self.agent_changed.emit(agent)
        self.mode_changed.emit(AGENT_MODES[agent][0])
