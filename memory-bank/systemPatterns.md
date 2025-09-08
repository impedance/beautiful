# System Patterns: doc2md

## Architecture Overview
The application follows a pipeline architecture with distinct, modular phases that can be executed independently or as a complete workflow.

## Core Architecture Patterns

### Pipeline Architecture
```
DOCX → HTML → Chapters → LLM Processing → Markdown → Validation → Navigation
```

1. **Preprocessing** (`preprocess.py`): DOCX to HTML conversion with Mammoth, image extraction
2. **Splitting** (`splitter.py`): Break HTML into chapters by H1 tags
3. **LLM Processing** (`llm_client.py`): Format each chapter using OpenRouter API
4. **Post-processing** (`postprocess.py`): Apply final transformations to Markdown
5. **Validation** (`validators.py`): Run quality checks on output
6. **Navigation** (`navigation.py`): Inject navigation links and create table of contents

### Key Design Patterns

#### Command Pattern
- CLI implemented with Typer for clean command structure
- Each major operation is a distinct command with clear parameters
- Easy extension for new commands and subcommands

#### Configuration Pattern
- Centralized configuration in `config.py`
- Environment-based configuration via `.env` file
- Default values with override capability
- Clear separation of static and dynamic configuration

#### Strategy Pattern
- Pluggable formatting rules via external files
- Customizable style mapping for DOCX processing
- Extensible validation rules
- Swappable LLM models via OpenRouter

#### Factory Pattern
- Prompt building with `prompt_builder.py`
- Dynamic prompt construction based on rules and examples
- Flexible template system for different formatting scenarios

## Component Relationships

### Data Flow
```
Input DOCX → Preprocessor → HTML + Images
                    ↓
            Splitter → Chapter HTML fragments
                    ↓
            LLM Client → Formatted Markdown chapters
                    ↓
            Postprocessor → Final Markdown
                    ↓
            Validator → Quality-checked Markdown
                    ↓
            Navigation → Markdown with TOC and links
                    ↓
            Output Directory
```

### Dependency Structure
- **CLI** depends on all processing modules
- **Preprocessor** depends on Mammoth and image handling
- **Splitter** depends on BeautifulSoup for HTML parsing
- **LLM Client** depends on OpenRouter API
- **Prompt Builder** depends on formatting rules and samples
- **Postprocessor** handles final Markdown cleanup
- **Validator** ensures output quality
- **Navigation** manages document structure and linking

## Critical Implementation Paths

### Error Handling
- Graceful degradation when LLM calls fail
- Comprehensive error reporting with context
- Retry mechanisms for API calls
- Validation failures prevent output corruption

### Extensibility Points
- Custom formatting rules via external files
- Pluggable style maps for different DOCX sources
- Configurable LLM models and parameters
- Modular validation rules

### Performance Considerations
- Chapter-level parallel processing potential
- Efficient HTML parsing with BeautifulSoup
- Caching of LLM responses when appropriate
- Memory-efficient processing of large documents
