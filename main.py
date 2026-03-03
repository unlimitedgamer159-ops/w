import json
import os
import sys

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QScrollArea, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

from agents.architect_agent import ArchitectParser
from agents.code_agent import CodeParser
from agents.data_agent import DataParser
from agents.finance_agent import FinanceParser
from agents.growth_agent import GrowthParser
from agents.personal_os import PersonalOSParser
from agents.research_agent import ResearchParser
from agents.strategy_legal import StrategyLegalParser
from components.input_bar import InputBar
from components.report_card import ReportCard
from components.sidebar import Sidebar
from components.topbar import TopBar
from config import AGENT_ENDPOINTS, APP_HEIGHT, APP_NAME, APP_WIDTH

PARSERS = {
    "research": ResearchParser(),
    "architect": ArchitectParser(),
    "data": DataParser(),
    "growth": GrowthParser(),
    "code": CodeParser(),
    "strategy": StrategyLegalParser(),
    "legal": StrategyLegalParser(),
    "finance": FinanceParser(),
    "personal_os": PersonalOSParser(),
}


def resource_path(*parts: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, *parts)


class Worker(QThread):
    completed = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, agent: str, mode: str, prompt: str):
        super().__init__()
        self.agent = agent
        self.mode = mode
        self.prompt = prompt

    def run(self) -> None:
        try:
            endpoint = AGENT_ENDPOINTS[self.agent]
            payload = {"mode": self.mode, "prompt": self.prompt}
            response = requests.post(endpoint, json=payload, timeout=120)
            response.raise_for_status()
            text = response.text
            try:
                text = response.json().get("response", response.text)
            except json.JSONDecodeError:
                pass
            self.completed.emit(text)
        except Exception as exc:
            self.failed.emit(str(exc))


class StreminiWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.agent = "research"
        self.mode = "Deep Dive"
        self.worker = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)

        self.sidebar = Sidebar()
        self.sidebar.agent_changed.connect(self._set_agent)
        self.sidebar.mode_changed.connect(self._set_mode)
        layout.addWidget(self.sidebar, 1)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.topbar = TopBar()
        self.topbar.on_clear(self._clear_output)
        right_layout.addWidget(self.topbar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_host = QWidget()
        self.chat_host.setObjectName("ChatArea")
        self.chat_layout = QVBoxLayout(self.chat_host)
        self.chat_layout.addStretch()
        self.scroll.setWidget(self.chat_host)
        right_layout.addWidget(self.scroll, 1)

        self.input = InputBar()
        self.input.submit.connect(self._submit)
        right_layout.addWidget(self.input)

        layout.addWidget(right, 3)

    def _set_agent(self, agent: str) -> None:
        self.agent = agent

    def _set_mode(self, mode: str) -> None:
        self.mode = mode

    def _submit(self, prompt: str) -> None:
        self.topbar.set_running(True)
        self.worker = Worker(self.agent, self.mode, prompt)
        self.worker.completed.connect(self._render_response)
        self.worker.failed.connect(self._render_error)
        self.worker.finished.connect(lambda: self.topbar.set_running(False))
        self.worker.start()

    def _clear_output(self) -> None:
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_response(self, content: str) -> None:
        parser = PARSERS[self.agent]
        blocks = parser.parse(content)
        for block in blocks:
            if block.kind == "mermaid":
                view = QWebEngineView()
                view.setHtml(
                    """
                    <html><head><script src='https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'></script></head>
                    <body><div class='mermaid'>"""
                    + block.body.replace("```mermaid", "").replace("```", "")
                    + """</div><script>mermaid.initialize({startOnLoad:true});</script></body></html>
                    """
                )
                view.setMinimumHeight(260)
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, view)
            else:
                card = ReportCard(block.title, block.body, block.severity)
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, card)

    def _render_error(self, message: str) -> None:
        card = ReportCard("Request failed", message, "high")
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, card)


def load_fonts() -> None:
    for filename in ("DMSans-Regular.ttf", "Lora-Regular.ttf"):
        path = resource_path("assets", "fonts", filename)
        if os.path.exists(path):
            QFontDatabase.addApplicationFont(path)


def main() -> int:
    app = QApplication(sys.argv)
    with open(resource_path("styles.qss"), "r", encoding="utf-8") as fh:
        app.setStyleSheet(fh.read())
    load_fonts()
    window = StreminiWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
