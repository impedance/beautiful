from __future__ import annotations

import httpx

from doc2md.llm_client import OpenRouterClient, PromptBuilderProtocol


class DummyBuilder(PromptBuilderProtocol):
    def build_for_chapter(self, chapter_html: str):  # type: ignore[override]
        return [{"role": "user", "content": chapter_html}]


def _make_success_response():
    content = """```json
{"title": "One"}
```
```markdown
# One
```"""
    return {"choices": [{"message": {"content": content}}]}


def test_format_chapter_parses_blocks(monkeypatch) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=_make_success_response())
    )
    monkeypatch.setattr(
        "doc2md.llm_client.CHAPTER_MANIFEST_SCHEMA",
        {
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        },
    )
    client = OpenRouterClient(
        DummyBuilder(), api_key="k", client=httpx.Client(transport=transport)
    )
    manifest, markdown = client.format_chapter("<h1>One</h1>")
    assert manifest == {"title": "One"}
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
    assert manifest == {"title": "One"}
    assert sleep_calls == [1]
