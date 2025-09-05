from typer.testing import CliRunner
from doc2md.cli import app

runner = CliRunner()


def test_run_outputs_hello_world() -> None:
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout
