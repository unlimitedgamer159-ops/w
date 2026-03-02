from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from config import SEVERITY_COLORS


class ReportCard(QFrame):
    def __init__(self, title: str, body: str, severity: str | None = None) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background: #ffffff; border: 1px solid #e4e0d8; border-radius: 12px;")
        layout = QVBoxLayout(self)
        heading = QLabel(title)
        heading.setStyleSheet("font-weight: 700;")
        text = QLabel(body)
        text.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(text)

        if severity:
            color = SEVERITY_COLORS.get(severity.lower(), "#6b7280")
            self.setStyleSheet(
                f"background: #ffffff; border: 1px solid {color}; border-left: 6px solid {color}; border-radius: 12px;"
            )
