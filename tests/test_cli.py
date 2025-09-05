from typer.testing import CliRunner

from doc2md.cli import app

runner = CliRunner()


def test_run_shows_conversion_messages(monkeypatch, tmp_path) -> None:
    def fake_convert(docx_path: str, style_map_path: str) -> str:
        return "<h1>Chap</h1><p>Body</p>"

    def fake_extract(docx_path: str, output_dir: str) -> None:
        pass

    def fake_split(html: str):
        return ["<h1>Chap</h1><p>Body</p>"]

    monkeypatch.setattr("doc2md.preprocess.convert_docx_to_html", fake_convert)
    monkeypatch.setattr("doc2md.preprocess.extract_images", fake_extract)
    monkeypatch.setattr("doc2md.splitter.split_html_by_h1", fake_split)

    result = runner.invoke(app, ["run", "input.docx", "--out", str(tmp_path)])
    assert result.exit_code == 0
    assert "Запуск конвертации для файла:" in result.stdout
    assert "Конвертация завершена. Результаты в:" in result.stdout
