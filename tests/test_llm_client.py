from __future__ import annotations

import httpx

from doc2md.llm_client import OpenRouterClient, PromptBuilderProtocol


class DummyBuilder(PromptBuilderProtocol):
    def build_for_chapter(self, chapter_html: str):  # type: ignore[override]
        return [{"role": "user", "content": chapter_html}]


def _make_success_response():
    content = """```json
{
  "chapter_number": 1,
  "title": "One",
  "filename": "1.one.md",
  "slug": "one"
}
```
```markdown
# One
```"""
    return {"choices": [{"message": {"content": content}}]}


def test_format_chapter_parses_blocks() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=_make_success_response())
    )
    client = OpenRouterClient(
        DummyBuilder(), api_key="k", client=httpx.Client(transport=transport)
    )
    manifest, markdown = client.format_chapter("<h1>One</h1>")
    expected_manifest = {
        "chapter_number": 1,
        "title": "One",
        "filename": "1.one.md",
        "slug": "one",
    }
    assert manifest == expected_manifest
    assert markdown == "# One"


def test_format_chapter_retries_on_429(monkeypatch) -> None:
    responses = [
        httpx.Response(429, json={"error": "Too Many"}),
        httpx.Response(200, json=_make_success_response()),
    ]
    transport = httpx.MockTransport(lambda request: responses.pop(0))
    sleep_calls: list[int] = []
    monkeypatch.setattr("doc2md.llm_client.time.sleep", lambda s: sleep_calls.append(s))
    client = OpenRouterClient(
        DummyBuilder(),
        api_key="k",
        client=httpx.Client(transport=transport),
        max_retries=2,
    )
    manifest, markdown = client.format_chapter("<h1>One</h1>")
    assert markdown == "# One"
    expected_manifest = {
        "chapter_number": 1,
        "title": "One",
        "filename": "1.one.md",
        "slug": "one",
    }
    assert manifest == expected_manifest
    assert sleep_calls == [1]


def test_format_chapter_adds_extra_headers(monkeypatch) -> None:
    monkeypatch.setattr("doc2md.llm_client.HTTP_REFERER", "https://example.com")
    monkeypatch.setattr("doc2md.llm_client.APP_TITLE", "Example")

    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(
            {
                "Authorization": request.headers.get("Authorization", ""),
                "HTTP-Referer": request.headers.get("HTTP-Referer", ""),
                "X-Title": request.headers.get("X-Title", ""),
            }
        )
        return httpx.Response(200, json=_make_success_response())

    transport = httpx.MockTransport(handler)
    client = OpenRouterClient(
        DummyBuilder(), api_key="k", client=httpx.Client(transport=transport)
    )
    client.format_chapter("<h1>One</h1>")
    assert captured["Authorization"] == "Bearer k"
    assert captured["HTTP-Referer"] == "https://example.com"
    assert captured["X-Title"] == "Example"
