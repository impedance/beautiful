"""Client for interacting with the OpenRouter LLM API."""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Protocol, Tuple

import httpx
from jsonschema import validate

from .config import (
    API_KEY,
    API_URL,
    DEFAULT_MODEL,
    HTTP_REFERER,
    APP_TITLE,
)
from .schema import CHAPTER_MANIFEST_SCHEMA


class PromptBuilderProtocol(Protocol):
    """Interface for prompt builders."""

    def build_for_chapter(
        self, chapter_html: str
    ) -> List[Dict[str, str]]: ...  # pragma: no cover - interface


class OpenRouterClient:
    """HTTP client wrapper with basic retry and response parsing."""

    def __init__(
        self,
        prompt_builder: PromptBuilderProtocol,
        api_key: str | None = None,
        *,
        model: str | None = None,
        api_url: str | None = None,
        max_retries: int = 5,
        client: httpx.Client | None = None,
    ) -> None:
        self.prompt_builder = prompt_builder
        self.api_key = api_key or API_KEY
        self.model = model or DEFAULT_MODEL
        self.api_url = api_url or API_URL
        self.max_retries = max_retries
        self._client = client or httpx.Client()
        self.http_referer = HTTP_REFERER
        self.app_title = APP_TITLE
        if not self.api_key:
            raise RuntimeError("OpenRouter API key is missing. Set OPENROUTER_API_KEY.")

    def format_chapter(self, chapter_html: str) -> Tuple[Dict[str, Any], str]:
        """Format a chapter of HTML via the OpenRouter API."""
        messages = self.prompt_builder.build_for_chapter(chapter_html)

        payload = {"model": self.model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        if self.app_title:
            headers["X-Title"] = self.app_title

        delay = 1
        for attempt in range(self.max_retries):
            response = self._client.post(self.api_url, json=payload, headers=headers)
            if response.status_code in {429} or 500 <= response.status_code < 600:
                if attempt == self.max_retries - 1:
                    response.raise_for_status()
                time.sleep(delay)
                delay *= 2
                continue
            response.raise_for_status()
            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                content_type = response.headers.get("Content-Type", "")
                snippet = response.text[:200]
                raise ValueError(
                    "Unexpected response from OpenRouter:"
                    f" content-type={content_type!r}, body={snippet!r}"
                ) from exc
            content = data["choices"][0]["message"]["content"]
            json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
            md_match = re.search(r"```markdown\n(.*?)\n```", content, re.DOTALL)
            if not json_match or not md_match:
                raise ValueError(
                    "LLM response does not contain valid JSON and Markdown blocks."
                )
            manifest = json.loads(json_match.group(1))
            validate(instance=manifest, schema=CHAPTER_MANIFEST_SCHEMA)
            markdown = md_match.group(1)
            return manifest, markdown

        raise RuntimeError("Failed to obtain response from OpenRouter after retries")
