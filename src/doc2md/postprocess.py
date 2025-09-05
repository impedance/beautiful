"""Markdown post-processing utilities."""

from __future__ import annotations

import re


class PostProcessor:
    """Apply final formatting fixes to generated Markdown."""

    def __init__(
        self, markdown_content: str, chapter_number: int, doc_slug: str
    ) -> None:
        self.md = markdown_content
        self.chapter_num = chapter_number
        self.slug = doc_slug
        self.h2_counter = 0
        self.h3_counter = 0
        self.h4_counter = 0

    def _normalize_h2(self, match: re.Match[str]) -> str:
        self.h2_counter += 1
        self.h3_counter = 0
        self.h4_counter = 0
        return f"## {self.chapter_num}.{self.h2_counter} {match.group(1)}"

    def _normalize_h3(self, match: re.Match[str]) -> str:
        self.h3_counter += 1
        self.h4_counter = 0
        return f"### {self.chapter_num}.{self.h2_counter}.{self.h3_counter} {match.group(1)}"

    def _normalize_h4(self, match: re.Match[str]) -> str:
        self.h4_counter += 1
        return (
            f"#### {self.chapter_num}.{self.h2_counter}.{self.h3_counter}.{self.h4_counter} "
            f"{match.group(1)}"
        )

    def run(self) -> str:
        """Run the post-processing steps and return the final Markdown."""
        lines = []
        for line in self.md.splitlines():
            match = re.match(r"## (.+)", line)
            if match:
                line = self._normalize_h2(match)
            else:
                match = re.match(r"### (.+)", line)
                if match:
                    line = self._normalize_h3(match)
                else:
                    match = re.match(r"#### (.+)", line)
                    if match:
                        line = self._normalize_h4(match)
            lines.append(line)

        self.md = "\n".join(lines)
        self.md = re.sub(
            r"!\[(.*?)\]\((.*?)\)",
            rf"![\1](/images/developer/administrator/{self.slug}/\2)",
            self.md,
        )
        return self.md


__all__ = ["PostProcessor"]
