"""Client for interacting with the OpenRouter LLM API."""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Protocol, Tuple

import httpx
from jsonschema import validate

from .config import (
    # OpenRouter config  
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_DEFAULT_MODEL,
    OPENROUTER_HTTP_REFERER,
    OPENROUTER_APP_TITLE,
    # Mistral config
    MISTRAL_API_KEY,
    MISTRAL_API_URL,
    MISTRAL_DEFAULT_MODEL,
    # Backward compatibility
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


class BaseLLMClient:
    """Base class for LLM clients."""

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
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.max_retries = max_retries
        self._client = client or httpx.Client(timeout=30.0)

    def format_chapter(self, chapter_html: str) -> Tuple[Dict[str, Any], str]:
        """Format a chapter of HTML via the LLM API."""
        messages = self.prompt_builder.build_for_chapter(chapter_html)
        payload = {"model": self.model, "messages": messages}
        headers = self._get_headers()

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
                    f"Unexpected response from {self.__class__.__name__}:"
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

        raise RuntimeError(f"Failed to obtain response from {self.__class__.__name__} after retries")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for the API request. Override in subclasses."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }


class OpenRouterClient(BaseLLMClient):
    """OpenRouter API client."""

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
        api_key = api_key or OPENROUTER_API_KEY
        model = model or OPENROUTER_DEFAULT_MODEL
        api_url = api_url or OPENROUTER_API_URL
        
        super().__init__(
            prompt_builder=prompt_builder,
            api_key=api_key,
            model=model,
            api_url=api_url,
            max_retries=max_retries,
            client=client,
        )
        
        self.http_referer = OPENROUTER_HTTP_REFERER
        self.app_title = OPENROUTER_APP_TITLE
        
        if not self.api_key:
            raise RuntimeError("OpenRouter API key is missing. Set OPENROUTER_API_KEY.")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API requests."""
        headers = super()._get_headers()
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        if self.app_title:
            headers["X-Title"] = self.app_title
        return headers


class MistralClient(BaseLLMClient):
    """Mistral AI API client."""

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
        api_key = api_key or MISTRAL_API_KEY
        model = model or MISTRAL_DEFAULT_MODEL
        api_url = api_url or MISTRAL_API_URL
        
        super().__init__(
            prompt_builder=prompt_builder,
            api_key=api_key,
            model=model,
            api_url=api_url,
            max_retries=max_retries,
            client=client,
        )
        
        if not self.api_key:
            raise RuntimeError("Mistral API key is missing. Set MISTRAL_API_KEY.")


class ClientFactory:
    """Factory for creating LLM clients based on provider."""

    @staticmethod
    def create_client(
        provider: str,
        prompt_builder: PromptBuilderProtocol,
        model: str | None = None,
        **kwargs
    ) -> BaseLLMClient:
        """Create a client for the specified provider."""
        if provider.lower() == "mistral":
            return MistralClient(prompt_builder, model=model, **kwargs)
        elif provider.lower() == "openrouter":
            return OpenRouterClient(prompt_builder, model=model, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: 'mistral', 'openrouter'")
