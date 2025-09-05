import random

from doc2md.prompt_builder import PromptBuilder


def test_build_for_chapter_includes_rules_examples_and_html(monkeypatch) -> None:
    monkeypatch.setattr(random, "sample", lambda seq, k: list(seq)[:k])
    builder = PromptBuilder("formatting_rules.md", "samples")
    messages = builder.build_for_chapter("<h1>Chap</h1>")

    assert len(messages) == 2
    system = messages[0]
    user = messages[1]

    assert system["role"] == "system"
    assert "FORMATTING RULES:" in system["content"]
    assert "EXAMPLES:" in system["content"]
    assert "# Общие сведения" in system["content"]

    assert user["role"] == "user"
    assert "CHAPTER HTML:" in user["content"]
    assert "<h1>Chap</h1>" in user["content"]
