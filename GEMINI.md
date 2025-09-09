# Project Overview

This project contains a command-line tool named `doc2md` that converts technical documentation from DOCX format to a set of Markdown files. It is written in Python and uses the `typer` library for its command-line interface and `poetry` for dependency management.

The conversion process is as follows:
1.  The DOCX file is preprocessed, which includes extracting images and converting the document to HTML.
2.  The HTML is split into chapters. The tool first attempts to split the document based on its structure, and if that fails, it falls back to splitting by `<h1>` tags.
3.  Each chapter is then processed by a Large Language Model (LLM) to convert the HTML to Markdown. The tool supports both the OpenRouter and Mistral APIs.
4.  The generated Markdown is post-processed, and navigation is injected to create a table of contents.

## Building and Running

To build and run the project, you need to have Python 3.11+ and Poetry installed.

1.  Install the dependencies:
    ```bash
    poetry install
    ```
2.  Run the tool:
    ```bash
    poetry run doc2md run input.docx --out output_dir
    ```

## Development Conventions

The project uses `ruff` for linting, `black` for code formatting, and `mypy` for static type checking. The tests are written using `pytest`.

To run the linters and tests, use the following commands:
```bash
ruff .
black --check .
mypy .
pytest
```
