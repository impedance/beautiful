# AGENTS instructions

This repository implements a pipeline for converting DOCX documents to Markdown as described in `doc2md-plan.md`.

## Development workflow
- Python 3.11+ is required.
- Use [Poetry](https://python-poetry.org/) for dependency management. When Poetry is unavailable or a lighter setup is desired, you may alternatively create a virtual environment via `python -m venv .venv` and install dependencies with `pip`.
- Activate the environment before running any commands: `poetry shell` or `source .venv/bin/activate`.

## Project structure
- Source code belongs in the `src/` directory and tests in `tests/`.
- The `samples/` folder contains example Markdown outputs and should be used as guidance when implementing features.

## Coding standards
- Format code with `black` and lint with `ruff`.
- Type check with `mypy` when annotations are present.

## Testing
- Run `pytest` for unit tests. Ensure all tests pass before committing.
- Add tests for new modules or functionality.

## Commit checklist
- Run linters (`ruff`, `black --check`, `mypy`) and tests (`pytest`) locally.
- Include relevant updates to documentation when behavior changes.

