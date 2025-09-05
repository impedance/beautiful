import logging

import typer
from rich.console import Console

logging.basicConfig(level=logging.INFO)

app = typer.Typer(help="Convert DOCX documentation to Markdown.")
console = Console()


@app.callback()
def main() -> None:
    """Main entry point for the CLI."""
    # This function allows adding subcommands like `run`.
    # It does not execute any logic by itself.
    pass


@app.command()
def run(
    docx_path: str = typer.Argument(..., help="Путь к входному DOCX файлу."),
    output_dir: str = typer.Option(
        "output", "--out", "-o", help="Директория для сохранения Markdown файлов."
    ),
) -> None:
    """Run the conversion pipeline."""
    logging.getLogger(__name__).info("Running the pipeline")
    console.print(f"[bold green]Запуск конвертации для файла:[/] {docx_path}")
    # Here will be the pipeline logic
    console.print(f"[bold green]Конвертация завершена. Результаты в:[/] {output_dir}")


if __name__ == "__main__":
    app()
