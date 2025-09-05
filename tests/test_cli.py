from typer.testing import CliRunner

from doc2md.cli import app

runner = CliRunner()


def _patch_preprocess(monkeypatch) -> None:
    def fake_convert(docx_path: str, style_map_path: str) -> str:
        return "<h1>Chap</h1><p>Body</p>"

    def fake_extract(docx_path: str, output_dir: str) -> None:
        pass

    def fake_split(html: str):
        return ["<h1>Chap</h1><p>Body</p>"]

    monkeypatch.setattr("doc2md.preprocess.convert_docx_to_html", fake_convert)
    monkeypatch.setattr("doc2md.preprocess.extract_images", fake_extract)
    monkeypatch.setattr("doc2md.splitter.split_html_by_h1", fake_split)


def test_run_dry_run_skips_llm(monkeypatch, tmp_path) -> None:
    _patch_preprocess(monkeypatch)

    called = {"client": False}

    class DummyClient:
        def __init__(self, *a, **k):
            called["client"] = True

    monkeypatch.setattr("doc2md.cli.OpenRouterClient", DummyClient)

    result = runner.invoke(
        app, ["run", "input.docx", "--out", str(tmp_path), "--dry-run"]
    )

    assert result.exit_code == 0
    assert "Dry run completed" in result.stdout
    assert not called["client"]


def test_run_passes_model_option(monkeypatch, tmp_path) -> None:
    _patch_preprocess(monkeypatch)

    class FakeBuilder:
        def build_for_chapter(self, html: str):
            return []

    class DummyPost:
        def __init__(self, md: str, idx: int, slug: str) -> None:
            self.md = md

        def run(self) -> str:
            return self.md

    captured = {}

    class DummyClient:
        def __init__(self, builder, api_key=None, *, model, **kw):
            captured["model"] = model

        def format_chapter(self, chapter_html: str):
            return (
                {
                    "chapter_number": 1,
                    "title": "Chap",
                    "filename": "chap.md",
                    "slug": "chap",
                },
                "## Heading\nBody",
            )

    monkeypatch.setattr(
        "doc2md.prompt_builder.PromptBuilder", lambda *a, **k: FakeBuilder()
    )
    monkeypatch.setattr("doc2md.cli.OpenRouterClient", DummyClient)
    monkeypatch.setattr("doc2md.postprocess.PostProcessor", DummyPost)
    monkeypatch.setattr(
        "doc2md.navigation.inject_navigation_and_create_toc", lambda *a, **k: None
    )
    monkeypatch.setattr("doc2md.validators.run_all_validators", lambda text: [])

    result = runner.invoke(
        app, ["run", "input.docx", "--out", str(tmp_path), "--model", "test-model"]
    )

    assert result.exit_code == 0
    assert captured["model"] == "test-model"
