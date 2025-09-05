from __future__ import annotations

import pytest
from jsonschema import validate, ValidationError

from doc2md.schema import CHAPTER_MANIFEST_SCHEMA


def test_schema_structure() -> None:
    assert CHAPTER_MANIFEST_SCHEMA["type"] == "object"
    required = set(CHAPTER_MANIFEST_SCHEMA["required"])
    assert {"chapter_number", "title", "filename", "slug"}.issubset(required)


def test_schema_validation_success() -> None:
    manifest = {
        "chapter_number": 1,
        "title": "Intro",
        "filename": "1.intro.md",
        "slug": "intro",
    }
    validate(manifest, CHAPTER_MANIFEST_SCHEMA)


def test_schema_validation_failure() -> None:
    manifest = {
        "chapter_number": "one",
        "title": "Intro",
        "filename": "1.intro.md",
        "slug": "intro",
    }
    with pytest.raises(ValidationError):
        validate(manifest, CHAPTER_MANIFEST_SCHEMA)
