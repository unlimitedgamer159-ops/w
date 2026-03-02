from agents.base_agent import BaseAgentParser, ParsedBlock


class ResearchParser(BaseAgentParser):
    def parse(self, content: str) -> list[ParsedBlock]:
        blocks = super().parse(content)
        parsed: list[ParsedBlock] = []
        for block in blocks:
            if "```mermaid" in block.body:
                parsed.append(ParsedBlock("mermaid", block.title, block.body))
            else:
                parsed.append(block)
        return parsed
