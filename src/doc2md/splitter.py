"""HTML splitting utilities."""

from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup


def split_html_by_h1(html_content: str) -> List[str]:
    """Split HTML content into fragments by <h1> headings."""
    soup = BeautifulSoup(html_content, "lxml")
    chapters: List[str] = []
    for h1 in soup.find_all("h1"):
        parts = [str(h1)]
        for sibling in h1.next_siblings:
            if getattr(sibling, "name", None) == "h1":
                break
            parts.append(str(sibling))
        chapters.append("".join(parts))
    return chapters
