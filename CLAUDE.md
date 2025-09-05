# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`doc2md` is a Python CLI tool that converts technical documentation from DOCX format to structured Markdown files using LLM-based formatting. It's built with Poetry for dependency management and uses Typer for the CLI interface.

## Development Commands

### Setup and Installation
```bash
poetry install
```

### Running the Application
```bash
# Main conversion command
poetry run doc2md run input.docx --out output_dir --model gpt-4o-mini --dry-run

# Available options:
# --out: Output directory (default: output)
# --model: OpenRouter model for formatting
# --dry-run: Preprocessing only, no LLM calls
# --style-map: Custom Mammoth style file path
# --rules-path: Custom formatting rules file
# --samples-dir: Directory with formatting examples
```

### Testing and Code Quality
```bash
# Linting and formatting
ruff .
black --check .
mypy .

# Run tests
pytest
```

## Architecture

The application follows a pipeline architecture with distinct phases:

1. **Preprocessing** (`preprocess.py`): Converts DOCX to HTML using Mammoth, extracts images
2. **Splitting** (`splitter.py`): Breaks HTML into chapters by H1 tags
3. **LLM Processing** (`llm_client.py`): Formats each chapter using OpenRouter API
4. **Post-processing** (`postprocess.py`): Applies final transformations to Markdown
5. **Validation** (`validators.py`): Runs quality checks on output
6. **Navigation** (`navigation.py`): Injects navigation links and creates table of contents

### Key Components

- **CLI Entry Point**: `src/doc2md/cli.py` - Main Typer application
- **Configuration**: `src/doc2md/config.py` - Default settings and model configuration
- **Prompt Building**: `src/doc2md/prompt_builder.py` - Constructs LLM prompts with rules and examples
- **Schema**: `src/doc2md/schema.py` - Data structure definitions

### Configuration Files

- **Environment**: `.env` file with OpenRouter API configuration
- **Formatting Rules**: `formatting_rules.md` - Detailed Markdown conversion guidelines
- **Style Mapping**: Custom Mammoth style map for DOCX processing
- **Examples**: `samples/` directory with formatting examples for LLM prompts

The pipeline is designed to be modular, allowing for dry-runs (preprocessing only) and customizable formatting rules through external configuration files.