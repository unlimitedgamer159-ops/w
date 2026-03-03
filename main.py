import json
import os
import sys

import requests
from functools import partial

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
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
from config import AGENT_ENDPOINTS, AGENT_MODES, APP_HEIGHT, APP_NAME, APP_WIDTH

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


class AgentCard(QFrame):
    def __init__(self, chip: str, title: str, description: str, agent: str):
        super().__init__()
        self.agent = agent
        self.setObjectName("AgentCard")

        layout = QVBoxLayout(self)
        chip_label = QLabel(chip)
        chip_label.setObjectName("CardChip")
        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        description_label = QLabel(description)
        description_label.setObjectName("CardDescription")
        description_label.setWordWrap(True)
        cta_label = QLabel("Open agent →")
        cta_label.setObjectName("CardCTA")

        layout.addWidget(chip_label, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(cta_label)


class HomePage(QWidget):
    agent_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("HomePage")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 28, 24, 24)
        root.setSpacing(16)

        hero = QWidget()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setSpacing(8)
        hero_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Choose the right specialist for every workflow.")
        title.setObjectName("HeroTitle")
        subtitle = QLabel(
            "Stremini Workspace brings your AI specialists into one polished command center. "
            "Open any agent below to run deep research, execute coding tasks, drive financial analysis, "
            "design AI systems, and unlock startup growth workflows."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("HeroSubtitle")
        hero_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        hero_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        cards = [
            ("Research", "Research & Math Agent", "Generate structured research papers, solve advanced math problems, and organize technical analysis with clear outputs.", "research"),
            ("ARIA", "ARIA Personal OS", "Your strategic second brain for planning, habits, reflection, and long-term personal operating system decisions.", "personal_os"),
            ("Finance", "Finance Agent", "Build financial models, evaluate business metrics, and receive concise analysis tailored for business and investment decisions.", "finance"),
            ("Startup & Legal", "Startup & Legal Compliance Agent", "Navigate startup setup, policy readiness, compliance checkpoints, and legal process guidance in one workspace.", "strategy"),
            ("Engineering", "Code Agent", "Design architecture, generate production-grade code, and iterate quickly on implementation with focused engineering support.", "code"),
            ("Growth / Strategy", "Growth & Marketing Intelligence Agent", "Build GTM strategy with competitor research, ICP modeling, SEO planning, funnel diagnostics, and structured outputs like SWOT, TAM/SAM/SOM, and KPI summaries.", "growth"),
            ("Advanced AI", "AI Systems Architect Agent", "Design production AI systems with RAG architecture, vector database selection, model tradeoff analysis, orchestration design, and scaling-aware cloud planning.", "architect"),
            ("Analytics / Ops", "Data & Decision Intelligence Agent", "Interpret CSV and JSON business data with retention, conversion, and anomaly analysis, then produce clear insights, risk flags, hypotheses, and experiment priorities.", "data"),
        ]

        for idx, (chip, card_title, description, agent) in enumerate(cards):
            card = AgentCard(chip, card_title, description, agent)
            card.mousePressEvent = partial(self._open_agent, agent)
            grid.addWidget(card, idx // 4, idx % 4)

        root.addWidget(hero)
        root.addWidget(grid_host)

    def _open_agent(self, agent: str, _event) -> None:
        self.agent_selected.emit(agent)


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
        self.mode = AGENT_MODES[self.agent][0]
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
        self.topbar.on_home(self._go_home)
        right_layout.addWidget(self.topbar)

        self.pages = QStackedWidget()

        self.home_page = HomePage()
        self.home_page.agent_selected.connect(self._launch_agent)
        self.pages.addWidget(self.home_page)

        chat_page = QWidget()
        chat_layout_root = QVBoxLayout(chat_page)
        chat_layout_root.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_host = QWidget()
        self.chat_host.setObjectName("ChatArea")
        self.chat_layout = QVBoxLayout(self.chat_host)
        self.chat_layout.addStretch()
        self.scroll.setWidget(self.chat_host)
        chat_layout_root.addWidget(self.scroll, 1)

        self.input = InputBar()
        self.input.submit.connect(self._submit)
        chat_layout_root.addWidget(self.input)

        self.pages.addWidget(chat_page)

        right_layout.addWidget(self.pages, 1)

        layout.addWidget(right, 3)

    def _set_agent(self, agent: str) -> None:
        self.agent = agent
        self.mode = AGENT_MODES[agent][0]

    def _set_mode(self, mode: str) -> None:
        self.mode = mode

    def _launch_agent(self, agent: str) -> None:
        self.sidebar.select_agent(agent)
        self.pages.setCurrentIndex(1)

    def _go_home(self) -> None:
        self.pages.setCurrentIndex(0)

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
