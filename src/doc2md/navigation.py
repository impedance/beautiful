"""Navigation utilities for generated Markdown files."""

from __future__ import annotations

import json
import os
from typing import List, Dict

import frontmatter


def inject_navigation_and_create_toc(output_dir: str) -> None:
    """Inject readPrev/readNext into Markdown files and create toc.json."""
    files = sorted(f for f in os.listdir(output_dir) if f.endswith(".md"))
    titles: Dict[str, str] = {}
    for name in files:
        path = os.path.join(output_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        titles[name] = post.get("title", "")

    toc: List[Dict[str, str]] = []
    for idx, name in enumerate(files):
        path = os.path.join(output_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        if idx > 0:
            prev = files[idx - 1]
            post["readPrev"] = {
                "to": f"/{os.path.splitext(prev)[0]}",
                "label": titles[prev],
            }
        if idx < len(files) - 1:
            nxt = files[idx + 1]
            post["readNext"] = {
                "to": f"/{os.path.splitext(nxt)[0]}",
                "label": titles[nxt],
            }
        with open(path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        toc.append({"title": titles[name], "to": f"/{os.path.splitext(name)[0]}"})

    with open(os.path.join(output_dir, "toc.json"), "w", encoding="utf-8") as f:
        json.dump(toc, f, ensure_ascii=False, indent=2)


__all__ = ["inject_navigation_and_create_toc"]
