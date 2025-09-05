"""Configuration utilities for environment variables."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
