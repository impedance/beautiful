# AGENTS.md

This file provides instructions for AI agents contributing to the **beautiful** project.

## Repository Overview
- Toolkit for converting DOCX documents to Markdown with advanced heading and formatting heuristics.
- Primary script: `improved_docx_converter.py`.
- Example inputs and outputs live in `dev.docx`, `samples/`, and `chapters/`.

## Key Commands
- Basic conversion: `python3 improved_docx_converter.py input.docx [output.md]`
- Add YAML frontmatter: `python3 improved_docx_converter.py input.docx output.md --frontmatter`
- Split DOCX into chapters: `python3 improved_docx_converter.py input.docx --split-chapters`

## Code Quality Principles
- Follow SOLID to keep modules cohesive and extensible.
- Keep implementations straightforward (KISS) and avoid over-engineering.
- Eliminate repetition; prefer abstractions that embody DRY.
- Review every change for clarity and maintainability before committing.

## Testing and Linting
- Сначала прогоните линтер:
  ```bash
  make lint
  ```
- Tests cover both unit and integration behaviour under `tests/`.
- Always run the linter and full test suite before committing:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -U pip python-docx pytest flake8 --exclude=venv . flake8
  make lint
  python3 -m pytest tests/ -v
  ```

## Formatting Guidelines
- Each Markdown file must start with YAML frontmatter specifying `title` and optional `nextRead` block.
- Top-level heading (`#`) matches the `title`; sections use numbered `##` headings like `## 1.1 Section`.
- Descriptive opening paragraphs may need to be wrapped in `::AppAnnotation` blocks.
- Use `-` for bullet lists and wrap component descriptions as `` `Component` — description ``.
- Tables follow standard Markdown syntax with optional alignment markers; multi-line cell content uses `<br>`.
- After every table, include a caption as a blockquote: `> Table X – Description`.
- See `formatting_rules.md` and `samples/` for detailed examples.

## Development Notes
- Code and documentation contain Russian comments and text; maintain existing language style.
- When editing converter logic or formatting rules, ensure chapter numbering, lists, tables, and annotations match the rules above.
- Commit only changes with all tests passing and keep commit messages descriptive.

