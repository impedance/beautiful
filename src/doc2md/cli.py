import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress
from slugify import slugify

from . import navigation, postprocess, preprocess, prompt_builder, splitter, validators
from .config import DEFAULT_MODEL, DEFAULT_PROVIDER, OPENROUTER_DEFAULT_MODEL, MISTRAL_DEFAULT_MODEL
from .llm_client import ClientFactory

logging.basicConfig(level=logging.INFO)

app = typer.Typer(help="Convert DOCX documentation to Markdown.")
console = Console()


def get_default_model_for_provider(provider: str) -> str:
    """Get the default model for a given provider."""
    if provider.lower() == "mistral":
        return MISTRAL_DEFAULT_MODEL
    else:  # openrouter or default
        return OPENROUTER_DEFAULT_MODEL


@app.callback()
def main() -> None:
    """Main entry point for the CLI."""
    pass


@app.command()
def run(
    docx_path: str = typer.Argument(..., help="Путь к входному DOCX файлу."),
    output_dir: str = typer.Option(
        "output", "--out", "-o", help="Директория для сохранения Markdown файлов."
    ),
    style_map: Path = typer.Option(
        Path(__file__).with_name("mammoth_style_map.map"),
        help="Путь к файлу style-map для Mammoth.",
    ),
    rules_path: Path = typer.Option(
        Path(__file__).resolve().parents[2] / "formatting_rules.md",
        help="Путь к правилам форматирования.",
    ),
    samples_dir: Path = typer.Option(
        Path(__file__).resolve().parents[2] / "samples",
        help="Каталог с примерами форматирования.",
    ),
    model: str = typer.Option(
        DEFAULT_MODEL, "--model", help="Имя модели для форматирования."
    ),
    provider: str = typer.Option(
        DEFAULT_PROVIDER, "--provider", help="API провайдер (openrouter или mistral)."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run/--no-dry-run", help="Запуск без обращения к LLM."
    ),
) -> None:
    """Run the conversion pipeline."""
    logging.getLogger(__name__).info("Running the pipeline")
    console.print(f"[bold green]Запуск конвертации для файла:[/] {docx_path}")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    images_dir = output_path / "images"
    preprocess.extract_images(docx_path, str(images_dir))

    html = preprocess.convert_docx_to_html(docx_path, str(style_map))
    # Remove table of contents to clean up the document
    html = preprocess.remove_table_of_contents(html)
    chapters = splitter.split_html_by_h1(html)

    # Temporary fix: only send the 4th chapter to the model
    if len(chapters) >= 4:
        chapters = [chapters[3]]
    else:
        chapters = []

    if dry_run:
        temp_dir = output_path / "html"
        temp_dir.mkdir(parents=True, exist_ok=True)

        if chapters:
            for idx, chapter in enumerate(chapters, start=1):
                (temp_dir / f"chapter_{idx}.html").write_text(chapter, encoding="utf-8")
            console.print(
                f"[yellow]Dry run completed. {len(chapters)} HTML chapters saved to {temp_dir}.[/]"
            )
        else:
            # No H1 tags found, save the entire HTML as a single file
            (temp_dir / "full_document.html").write_text(html, encoding="utf-8")
            console.print(
                f"[yellow]Dry run completed. No H1 tags found, full HTML saved as full_document.html in {temp_dir}.[/]"
            )
        return

    doc_slug = slugify(Path(docx_path).stem)
    builder = prompt_builder.PromptBuilder(rules_path, samples_dir)
    
    # If model is the default and doesn't match provider, use provider's default model
    if model == DEFAULT_MODEL:
        model = get_default_model_for_provider(provider)
    
    client = ClientFactory.create_client(provider, builder, model=model)

    with Progress() as progress:
        task = progress.add_task("Formatting chapters", total=len(chapters))
        for idx, chapter in enumerate(chapters, start=1):
            manifest, md = client.format_chapter(chapter)
            processed = postprocess.PostProcessor(md, idx, doc_slug).run()
            warnings = validators.run_all_validators(processed)
            for w in warnings:
                logging.warning(w)
            file_path = output_path / manifest["filename"]
            file_path.write_text(processed, encoding="utf-8")
            progress.advance(task)

    navigation.inject_navigation_and_create_toc(str(output_path))
    console.print(f"[bold green]Конвертация завершена. Результаты в:[/] {output_dir}")


if __name__ == "__main__":
    app()
