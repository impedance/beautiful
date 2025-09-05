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


def test_schema_validation_with_navigation() -> None:
    """Test that navigation fields are properly validated."""
    manifest = {
        "chapter_number": 2,
        "title": "Architecture",
        "filename": "2.architecture.md", 
        "slug": "architecture",
        "readPrev": {
            "to": "/developer/administrator/common",
            "label": "Общие сведения"
        },
        "readNext": {
            "to": "/developer/administrator/technical-requirements",
            "label": "Технические требования"
        },
        "description": "Architecture overview",
        "keywords": ["architecture", "components"]
    }
    validate(manifest, CHAPTER_MANIFEST_SCHEMA)


def test_schema_validation_with_nextread() -> None:
    """Test backward compatibility with nextRead field."""
    manifest = {
        "chapter_number": 1,
        "title": "Getting Started",
        "filename": "1.start.md",
        "slug": "start", 
        "nextRead": {
            "to": "/developer/administrator/architecture",
            "label": "Архитектура"
        }
    }
    validate(manifest, CHAPTER_MANIFEST_SCHEMA)


def test_schema_validation_invalid_navigation() -> None:
    """Test that invalid navigation objects are rejected."""
    manifest = {
        "chapter_number": 1,
        "title": "Test",
        "filename": "test.md",
        "slug": "test",
        "readNext": {
            "to": "",  # Empty string should fail minLength validation
            "label": "Next"
        }
    }
    with pytest.raises(ValidationError):
        validate(manifest, CHAPTER_MANIFEST_SCHEMA)
