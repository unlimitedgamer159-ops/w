import re

from agents.base_agent import BaseAgentParser, ParsedBlock


class ResearchParser(BaseAgentParser):
    DIAGRAM_RE = re.compile(
        r"<diagram\s+type=[\"']?(?P<dtype>\w+)[\"']?\s+title=[\"']?(?P<title>[^\"'>]*)[\"']?\s*>(?P<code>[\s\S]*?)</diagram>",
        re.IGNORECASE,
    )
    MERMAID_RE = re.compile(r"```mermaid\s*(?P<code>[\s\S]*?)```", re.IGNORECASE)

    def parse(self, content: str) -> list[ParsedBlock]:
        sections = super().parse(content)
        parsed: list[ParsedBlock] = []

        for section in sections:
            parsed.extend(self._parse_section(section.title, section.body))

        return parsed or [ParsedBlock("section", "Response", content)]

    def _parse_section(self, title: str, body: str) -> list[ParsedBlock]:
        blocks: list[ParsedBlock] = []
        cursor = 0

        for match in self._iter_diagrams(body):
            start, end = match.span()
            text_chunk = body[cursor:start].strip()
            if text_chunk:
                blocks.append(ParsedBlock("section", title, text_chunk))

            diagram_code = match.group("code").strip()
            diagram_title = (match.groupdict().get("title") or "Diagram").strip() or "Diagram"
            blocks.append(ParsedBlock("mermaid", diagram_title, diagram_code))
            cursor = end

        trailing = body[cursor:].strip()
        if trailing:
            blocks.append(ParsedBlock("section", title, trailing))

        return blocks

    def _iter_diagrams(self, body: str):
        matches = []
        matches.extend(self.DIAGRAM_RE.finditer(body))
        matches.extend(self.MERMAID_RE.finditer(body))
        return sorted(matches, key=lambda m: m.start())
