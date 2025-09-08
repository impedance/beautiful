# Technical Context: doc2md

## Technology Stack

### Core Technologies
- **Python 3.11+**: Primary programming language
- **Poetry**: Dependency management and packaging
- **Typer**: CLI framework for command-line interface
- **Mammoth**: DOCX to HTML conversion library
- **BeautifulSoup**: HTML parsing and manipulation
- **OpenRouter API**: LLM-based formatting service
- **Pydantic**: Data validation and schema definition

### Development Tools
- **Black**: Code formatting
- **Ruff**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **Coverage.py**: Test coverage reporting

### Key Libraries and Dependencies
- `python-mammoth`: DOCX processing
- `beautifulsoup4`: HTML parsing
- `typer`: CLI interface
- `pydantic`: Data validation
- `python-dotenv`: Environment configuration
- `requests`: HTTP client for API calls
- `jinja2`: Template rendering (if used)

## Development Environment

### Setup Requirements
- Python 3.11 or higher
- Poetry for dependency management
- OpenRouter API key (configured in `.env`)

### Development Workflow
```bash
# Setup
poetry install
poetry shell  # or source .venv/bin/activate

# Development commands
ruff .        # Linting
black .       # Formatting
mypy .        # Type checking
pytest        # Run tests

# Running the application
poetry run doc2md run input.docx --out output_dir
```

## Project Structure
```
src/
  doc2md/
    __init__.py
    cli.py          # CLI entry point
    config.py       # Configuration management
    preprocess.py   # DOCX to HTML conversion
    splitter.py     # HTML chapter splitting
    llm_client.py   # LLM API integration
    prompt_builder.py # Prompt construction
    postprocess.py  # Markdown finalization
    validators.py   # Quality validation
    navigation.py   # TOC and navigation
    schema.py       # Data structures
tests/
  test_*.py         # Unit tests for each module
samples/            # Formatting examples
scripts/            # Utility scripts
```

## Configuration Files
- **`.env`**: API keys and environment variables
- **`formatting_rules.md`**: LLM formatting guidelines
- **`mammoth_style_map.map`**: DOCX style mapping
- **`pyproject.toml`**: Poetry configuration and dependencies

## Testing Strategy
- Unit tests for each module in `tests/`
- Example-based testing with `samples/` directory
- Integration testing of the full pipeline
- Validation of output quality and structure
- Error handling and edge case testing

## Deployment Considerations
- Poetry-managed dependencies ensure reproducible builds
- CLI interface makes tool easy to integrate into workflows
- Environment-based configuration for different deployments
- Self-contained package structure
