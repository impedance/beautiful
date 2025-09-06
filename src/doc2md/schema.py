"""JSON schemas for LLM-generated manifests.

`CHAPTER_MANIFEST_SCHEMA` defines the structure for metadata produced by the
LLM for each chapter. The schema is used in ``llm_client.format_chapter`` and
unit tests to validate that responses include all required fields before the
Markdown files are written.
"""

from __future__ import annotations

from typing import Any, Dict


CHAPTER_MANIFEST_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["chapter_number", "title", "filename", "slug"],
    "properties": {
        # Basic required fields
        "chapter_number": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "filename": {"type": "string", "minLength": 1},
        "slug": {"type": "string", "minLength": 1},
        # Navigation fields (optional)
        "readPrev": {
            "type": ["object", "null"],
            "properties": {
                "to": {"type": "string", "minLength": 1},
                "label": {"type": "string", "minLength": 1},
            },
            "required": ["to", "label"],
            "additionalProperties": False,
        },
        "readNext": {
            "type": ["object", "null"],
            "properties": {
                "to": {"type": "string", "minLength": 1},
                "label": {"type": "string", "minLength": 1},
            },
            "required": ["to", "label"],
            "additionalProperties": False,
        },
        # Alternative simple navigation (backward compatibility)
        "nextRead": {
            "type": ["object", "null"],
            "properties": {
                "to": {"type": "string", "minLength": 1},
                "label": {"type": "string", "minLength": 1},
            },
            "required": ["to", "label"],
            "additionalProperties": False,
        },
        # Optional metadata fields
        "description": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string", "minLength": 1}},
    },
    "additionalProperties": False,
}

__all__ = ["CHAPTER_MANIFEST_SCHEMA"]
