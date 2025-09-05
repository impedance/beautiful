"""JSON schemas for LLM-generated manifests."""

from __future__ import annotations

from typing import Any, Dict

CHAPTER_MANIFEST_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["chapter_number", "title", "filename", "slug"],
    "properties": {
        "chapter_number": {"type": "integer", "minimum": 1},
        "title": {"type": "string"},
        "filename": {"type": "string"},
        "slug": {"type": "string"},
    },
    "additionalProperties": False,
}

__all__ = ["CHAPTER_MANIFEST_SCHEMA"]
