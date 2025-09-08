# Product Context: doc2md

## Problem Statement
Technical documentation is often created in Word (DOCX) format but needs to be converted to Markdown for use in modern documentation systems, knowledge bases, and static site generators. Manual conversion is time-consuming and error-prone, especially for large documents with complex formatting, images, and hierarchical structures.

## Solution
`doc2md` automates the conversion process by:
1. Converting DOCX to HTML using Mammoth for accurate content extraction
2. Splitting content into logical chapters by H1 headings
3. Applying LLM-based formatting to ensure consistent, high-quality Markdown output
4. Preserving document structure, images, and navigation
5. Providing customizable formatting rules for different documentation styles

## User Experience Goals
- **Simple CLI Interface**: Easy-to-use command-line interface with clear options
- **Reliable Conversion**: Accurate preservation of document content and structure
- **Customizable Output**: Configurable formatting rules and style mapping
- **Transparent Process**: Dry-run capability to preview conversion without LLM calls
- **Quality Assurance**: Built-in validation and error checking
- **Developer Friendly**: Well-structured codebase with clear documentation

## Key User Journeys
1. **Basic Conversion**: User runs `doc2md run input.docx` to convert a document with default settings
2. **Custom Configuration**: User specifies custom formatting rules, style maps, and output directories
3. **Preview Mode**: User runs with `--dry-run` to see preprocessing results without LLM processing
4. **Quality Validation**: System automatically validates output and reports issues

## Success Metrics
- High accuracy in content conversion (minimal loss of information)
- Proper preservation of document hierarchy and structure
- Consistent formatting that meets technical documentation standards
- Fast processing times with efficient LLM usage
- Low error rates and clear error reporting
- Positive feedback from documentation teams and technical writers
