"""Utilities for building prompts for the LLM."""

from __future__ import annotations

from pathlib import Path
import random
from typing import Dict, List


class PromptBuilder:
    """Builds system and user prompts for chapter conversion."""

    def __init__(
        self, rules_path: str | Path, samples_dir: str | Path, num_examples: int = 2
    ) -> None:
        self.rules = Path(rules_path).read_text(encoding="utf-8")
        self.examples = self._load_examples(samples_dir, num_examples)

    def _load_examples(self, samples_dir: str | Path, num_examples: int) -> str:
        sample_paths = sorted(Path(samples_dir).rglob("*.md"))
        if not sample_paths:
            return ""
        k = min(num_examples, len(sample_paths))
        chosen = random.sample(sample_paths, k=k)
        contents: List[str] = []
        for path in chosen:
            contents.append(path.read_text(encoding="utf-8").strip())
        return "\n\n".join(contents)

    def build_for_chapter(self, chapter_html: str) -> List[Dict[str, str]]:
        system_prompt = (
            "You are an expert DOCX to Markdown converter. Follow all rules precisely.\n"
            f"FORMATTING RULES:\n{self.rules}\n"
            f"EXAMPLES:\n{self.examples}"
        )
        user_prompt = (
            "Convert this chapter HTML to Markdown. Return EXACTLY two blocks: a JSON manifest, then the Markdown content.\n"
            f"CHAPTER HTML:\n```html\n{chapter_html}\n```"
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
