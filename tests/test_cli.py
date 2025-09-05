from typer.testing import CliRunner

from doc2md.cli import app

runner = CliRunner()


def test_run_shows_conversion_messages() -> None:
    result = runner.invoke(app, ["run", "input.docx"])
    assert result.exit_code == 0
    assert "Запуск конвертации для файла:" in result.stdout
    assert "Конвертация завершена. Результаты в:" in result.stdout
