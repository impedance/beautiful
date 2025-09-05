import logging
from pathlib import Path

import typer
from rich.console import Console

from . import preprocess, splitter

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
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    images_dir = output_path / "images"
    preprocess.extract_images(docx_path, str(images_dir))

    style_map_path = Path(__file__).with_name("mammoth_style_map.map")
    html = preprocess.convert_docx_to_html(docx_path, str(style_map_path))
    chapters = splitter.split_html_by_h1(html)

    temp_dir = output_path / "html"
    temp_dir.mkdir(parents=True, exist_ok=True)
    for idx, chapter in enumerate(chapters, start=1):
        (temp_dir / f"chapter_{idx}.html").write_text(chapter, encoding="utf-8")

    console.print(f"[bold green]Конвертация завершена. Результаты в:[/] {output_dir}")


if __name__ == "__main__":
    app()
