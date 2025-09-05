"""Markdown validation utilities."""

from __future__ import annotations

import re
from typing import List


def validate_app_annotations(markdown: str) -> List[str]:
    """Check that all ::AppAnnotation blocks are properly closed."""
    warnings: List[str] = []
    starts = [m.start() for m in re.finditer(r"::AppAnnotation", markdown)]
    ends = [m.start() for m in re.finditer(r"^::\s*$", markdown, flags=re.MULTILINE)]
    if len(starts) != len(ends):
        warnings.append("Mismatched ::AppAnnotation blocks")
    elif starts and any(s > e for s, e in zip(starts, ends)):
        warnings.append("Incorrect ::AppAnnotation block ordering")
    return warnings


def validate_table_captions(markdown: str) -> List[str]:
    """Ensure table captions follow '> Таблица N – Description' format."""
    warnings: List[str] = []
    for line in markdown.splitlines():
        if line.startswith("> Таблица"):
            if not re.match(r"^> Таблица \d+ – .+", line):
                warnings.append(f"Invalid table caption: {line}")
    return warnings


def validate_component_list_punctuation(markdown: str) -> List[str]:
    """Ensure component lists use ';' and '.' punctuation."""
    warnings: List[str] = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("- "):
            start = i
            while i < len(lines) and lines[i].startswith("- "):
                i += 1
            group = lines[start:i]
            for j, item in enumerate(group):
                text = item.rstrip()
                if j < len(group) - 1:
                    if not text.endswith(";"):
                        warnings.append(f"List item should end with ';': {item}")
                else:
                    if not text.endswith("."):
                        warnings.append(f"Last list item should end with '.': {item}")
            continue
        i += 1
    return warnings


def run_all_validators(markdown: str) -> List[str]:
    """Run all validators and collect warnings."""
    warnings = []
    warnings.extend(validate_app_annotations(markdown))
    warnings.extend(validate_table_captions(markdown))
    warnings.extend(validate_component_list_punctuation(markdown))
    return warnings


__all__ = [
    "validate_app_annotations",
    "validate_table_captions",
    "validate_component_list_punctuation",
    "run_all_validators",
]
