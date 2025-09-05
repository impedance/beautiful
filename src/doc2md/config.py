"""Configuration utilities for environment variables."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
_base_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
API_URL = f"{_base_url}/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER", "")
APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "")

__all__ = [
    "API_KEY",
    "API_URL",
    "DEFAULT_MODEL",
    "HTTP_REFERER",
    "APP_TITLE",
]
