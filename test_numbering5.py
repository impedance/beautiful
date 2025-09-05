#!/usr/bin/env python3
"""Find headings after TOC section."""

import sys
from docx import Document
import re


def find_headings_after_toc(docx_path: str):
    """Find actual content headings after TOC."""
    doc = Document(docx_path)
    
    print(f"Looking for content headings after TOC in {docx_path}...")
    print("=" * 60)
    
    # Skip to after TOC - look for paragraphs after para 250
    for i, paragraph in enumerate(doc.paragraphs[250:], 250):
        text = paragraph.text.strip()
        if not text:
            continue
        
        # Look for numbered text that could be headings
        if re.match(r'^\d+(?:\.\d+)*\s+[А-Я]', text) and not paragraph.style.name.startswith('toc'):
            number_part = re.match(r'^(\d+(?:\.\d+)*)', text).group(1)
            level = len(number_part.split('.'))
            
            # Check if this looks like the "4.1.2.1 Подготовка" pattern
            if '4.1.2' in number_part or 'Подготовка' in text or level >= 3:
                print(f"Para {i:4d}: Level H{level} Style='{paragraph.style.name}'")
                print(f"         Number: '{number_part}'")
                print(f"         Text: '{text[:80]}{'...' if len(text) > 80 else ''}'")
                print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_numbering5.py <docx_file>")
        sys.exit(1)
    
    find_headings_after_toc(sys.argv[1])