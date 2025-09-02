# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a document conversion toolkit repository focused on converting DOCX files to Markdown format with advanced features. The main component is a sophisticated DOCX-to-Markdown converter written in Python.

## Key Components

### Main Converter (`improved-docx-converter.py`)
- Advanced DOCX to Markdown converter with intelligent heading detection
- Handles tables, code blocks, lists, and inline formatting
- Supports custom heading mapping based on styles and font sizes
- Processes outline levels and formatting heuristics for heading detection
- Includes optional frontmatter generation for documentation systems
- Written in Python with extensive Russian language support

### Document Files
- `impro.md` - Sample converted document showing the output format
- `dev.docx` - Input DOCX file for conversion

## Commands

### Run the Converter
```bash
python3 improved-docx-converter.py input.docx [output.md]
```

### Add Frontmatter to Output
```bash
python3 improved-docx-converter.py input.docx output.md --frontmatter
```

### Split into Chapters
```bash
python3 improved-docx-converter.py input.docx --split-chapters
```

### Run Tests
```bash
# Run all tests
source venv/bin/activate && python3 -m pytest tests/ -v

# Run specific test categories
source venv/bin/activate && python3 -m pytest tests/unit/ -v          # Unit tests only
source venv/bin/activate && python3 -m pytest tests/integration/ -v  # Integration tests only

# Run with coverage
source venv/bin/activate && python3 -m pytest tests/ --tb=short -v
```

## Architecture Notes

The converter uses a multi-layered approach for document analysis:

1. **Heading Detection**: Uses style mapping, outline levels, font formatting, and text patterns
2. **Content Processing**: Handles paragraphs, tables, code blocks, and lists separately
3. **Formatting Preservation**: Maintains bold, italic, and code formatting in Markdown
4. **Language Detection**: Automatically detects code block languages (bash, yaml, sql, python, etc.)

The converter is designed specifically for technical documentation and handles Russian text extensively. It includes sophisticated heuristics for detecting document structure in Word documents that may not have proper styles applied.

## Test Structure

The project uses a well-organized test suite:

```
tests/
├── unit/                              # Unit tests for specific functionality
│   ├── test_converter_core.py         # Core converter functionality
│   ├── test_formatting_rules.py       # Formatting and rule validation
│   └── test_chapter_splitting.py      # Chapter splitting logic
└── integration/                       # Integration tests with real files
    ├── test_docx_processing.py        # Real DOCX file processing  
    ├── test_content_distribution.py   # Content distribution verification
    └── test_final_integration.py      # End-to-end integration tests
```

**Test Coverage:**
- ✅ 31 passing tests, 3 skipped
- ✅ Unit tests: Core conversion, formatting, chapter splitting
- ✅ Integration tests: Real DOCX processing, content distribution
- ✅ All main functionality covered with comprehensive test cases

## Dependencies

- `python-docx` - Core DOCX processing library
- `pytest` - Testing framework
- Standard Python libraries: `re`, `sys`, `pathlib`, `xml.etree.ElementTree`

## Development Notes

- The codebase is primarily in Russian with Russian comments
- Focuses on converting technical documentation and administrative guides
- Handles complex document structures including nested lists and tables
- Includes special processing for code blocks and technical content