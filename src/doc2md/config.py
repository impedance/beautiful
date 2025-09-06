"""Configuration utilities for environment variables."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# Default provider
DEFAULT_PROVIDER = os.getenv("DOC2MD_PROVIDER", "openrouter")

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
_openrouter_base_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_URL = f"{_openrouter_base_url}/chat/completions"
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-coder-32b-instruct:free")
OPENROUTER_HTTP_REFERER = os.getenv("OPENROUTER_HTTP_REFERER", "")
OPENROUTER_APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "")

# Mistral configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
_mistral_base_url = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1")
MISTRAL_API_URL = f"{_mistral_base_url}/chat/completions"
MISTRAL_DEFAULT_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

# Backward compatibility
API_KEY = OPENROUTER_API_KEY
API_URL = OPENROUTER_API_URL
DEFAULT_MODEL = OPENROUTER_DEFAULT_MODEL
HTTP_REFERER = OPENROUTER_HTTP_REFERER
APP_TITLE = OPENROUTER_APP_TITLE

__all__ = [
    "DEFAULT_PROVIDER",
    "OPENROUTER_API_KEY",
    "OPENROUTER_API_URL", 
    "OPENROUTER_DEFAULT_MODEL",
    "OPENROUTER_HTTP_REFERER",
    "OPENROUTER_APP_TITLE",
    "MISTRAL_API_KEY",
    "MISTRAL_API_URL",
    "MISTRAL_DEFAULT_MODEL",
    # Backward compatibility
    "API_KEY",
    "API_URL", 
    "DEFAULT_MODEL",
    "HTTP_REFERER",
    "APP_TITLE",
]
