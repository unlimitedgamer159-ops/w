"""Global configuration for Stremini Workspace."""

from dataclasses import dataclass

APP_NAME = "Stremini Workspace"
APP_WIDTH = 1440
APP_HEIGHT = 920

AGENT_ENDPOINTS = {
    "code": "https://code-agent.vishwajeetadkine705.workers.dev",
    "research": "https://agentic-research.vishwajeetadkine705.workers.dev",
    "data": "https://data-agent.vishwajeetadkine705.workers.dev",
    "growth": "https://growth-agent.vishwajeetadkine705.workers.dev",
    "strategy": "https://startup-strategy.vishwajeetadkine705.workers.dev",
    "legal": "https://legal-compliance.vishwajeetadkine705.workers.dev",
    "architect": "https://architect-agent.vishwajeetadkine705.workers.dev",
    "finance": "https://finance-agent.vishwajeetadkine705.workers.dev",
    "personal_os": "https://personal-os.vishwajeetadkine705.workers.dev",
}

AGENT_MODES = {
    "code": ["Debug", "Refactor", "Review", "Generate"],
    "research": ["Deep Dive", "PDF", "Benchmarks", "Math"],
    "data": ["Diagnose", "Cohort", "Conversion", "Health"],
    "growth": ["GTM", "Funnel", "Competitor", "Roadmap"],
    "strategy": ["Executive", "Market", "Risk", "Ops"],
    "legal": ["Compliance", "Contracts", "IP", "Policy"],
    "architect": ["Flows", "Components", "Infra", "Docs"],
    "finance": ["Forecast", "What-if", "Burn", "Fundraise"],
    "personal_os": ["Memory", "Tasks", "Focus", "Journal"],
}

SEVERITY_COLORS = {
    "high": "#ef4444",
    "medium": "#f59e0b",
    "low": "#eab308",
}


@dataclass(frozen=True)
class Theme:
    bg: str = "#f7f5f2"
    surface: str = "#fbfaf8"
    surface2: str = "#f2f0ec"
    border: str = "#e4e0d8"
    text: str = "#1f2937"
    amber: str = "#d97706"


THEME = Theme()
