from agents.base_agent import BaseAgentParser, ParsedBlock


class DataParser(BaseAgentParser):
    def parse(self, content: str) -> list[ParsedBlock]:
        blocks = super().parse(content)
        for block in blocks:
            lowered = block.body.lower()
            if "high" in lowered:
                block.severity = "high"
            elif "medium" in lowered:
                block.severity = "medium"
            elif "low" in lowered:
                block.severity = "low"
        return blocks
