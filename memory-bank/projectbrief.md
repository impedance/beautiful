# Project Brief: doc2md

## Overview
`doc2md` is a Python CLI tool that converts technical documentation from DOCX format to structured Markdown files using LLM-based formatting. It's built with Poetry for dependency management and uses Typer for the CLI interface.

## Core Purpose
Convert technical documentation from DOCX format to well-structured Markdown using LLM-based formatting while maintaining document hierarchy, images, and navigation.

## Key Features
- DOCX to HTML conversion using Mammoth
- HTML to Markdown processing with LLM formatting
- Chapter splitting by H1 tags
- Image extraction and management
- Navigation link injection
- Table of contents generation
- Customizable formatting rules
- Dry-run capability for preprocessing only
- Quality validation of output

## Target Audience
Technical documentation writers, content managers, and developers who need to convert Word documents to structured Markdown for documentation systems, knowledge bases, or static site generators.

## Success Criteria
- Accurate conversion of DOCX content to Markdown
- Proper preservation of document structure and hierarchy
- High-quality LLM-based formatting that follows specified rules
- Maintainable, testable codebase following SOLID principles
- Clean, readable output suitable for technical documentation
