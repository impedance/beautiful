#!/usr/bin/env python3
"""Test script to extract heading numbering from DOCX."""

import sys
from docx import Document
from docx.enum.style import WD_STYLE_TYPE


def analyze_docx_headings(docx_path: str):
    """Analyze DOCX headings and their numbering."""
    doc = Document(docx_path)
    
    print(f"Analyzing {docx_path}...")
    print("=" * 50)
    
    # Get all styles
    print("Available heading styles:")
    for style in doc.styles:
        if style.type == WD_STYLE_TYPE.PARAGRAPH and 'heading' in style.name.lower():
            print(f"  - {style.name}")
    
    print("\n" + "=" * 50)
    print("Paragraphs with heading styles:")
    
    for i, paragraph in enumerate(doc.paragraphs):
        if paragraph.style.name.startswith(('Heading', 'Заголовок')):
            # Check if paragraph has numbering
            numbering = None
            if paragraph._p.pPr is not None and paragraph._p.pPr.numPr is not None:
                # Has numbering
                num_id = paragraph._p.pPr.numPr.numId
                ilvl = paragraph._p.pPr.numPr.ilvl
                if num_id is not None and ilvl is not None:
                    numbering = f"numId: {num_id.val}, level: {ilvl.val}"
            
            print(f"Para {i:3d}: Style='{paragraph.style.name}' Numbering={numbering}")
            print(f"        Text: '{paragraph.text[:100]}{'...' if len(paragraph.text) > 100 else ''}'")
            print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_numbering.py <docx_file>")
        sys.exit(1)
    
    analyze_docx_headings(sys.argv[1])