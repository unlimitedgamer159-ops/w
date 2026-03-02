from dataclasses import dataclass


@dataclass
class ParsedBlock:
    kind: str
    title: str
    body: str
    severity: str | None = None


class BaseAgentParser:
    def parse(self, content: str) -> list[ParsedBlock]:
        blocks: list[ParsedBlock] = []
        current_title = "Response"
        current_lines: list[str] = []
        for line in content.splitlines():
            if line.startswith("##"):
                if current_lines:
                    blocks.append(ParsedBlock("section", current_title, "\n".join(current_lines).strip()))
                current_title = line.lstrip("# ").strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            blocks.append(ParsedBlock("section", current_title, "\n".join(current_lines).strip()))
        return blocks
