import logging
import typer

logging.basicConfig(level=logging.INFO)

app = typer.Typer(help="Convert DOCX documentation to Markdown.")


@app.callback()
def main() -> None:
    """Main entry point for the CLI."""
    # This function allows adding subcommands like `run`.
    # It does not execute any logic by itself.
    pass


@app.command()
def run() -> None:
    """Run the conversion pipeline."""
    logging.getLogger(__name__).info("Running the pipeline")
    typer.echo("Hello, World!")


if __name__ == "__main__":
    app()
