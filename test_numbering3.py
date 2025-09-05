#!/usr/bin/env python3
"""Find actual headings (not TOC) with numbering."""

import sys
from docx import Document
import re


def analyze_headings_after_toc(docx_path: str):
    """Find actual headings after TOC section."""
    doc = Document(docx_path)
    
    print(f"Looking for actual headings in {docx_path}...")
    print("=" * 60)
    
    # Find where TOC ends and content begins
    toc_ended = False
    heading_count = 0
    
    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
        
        # Skip TOC entries
        if paragraph.style.name.startswith('toc'):
            continue
        
        # Mark when we hit actual content headings
        if not toc_ended and (
            text.startswith('1 Общие сведения') or 
            re.match(r'^\d+\s+[А-Я]', text)  # Russian heading pattern
        ):
            toc_ended = True
        
        if toc_ended:
            # Look for numbered headings in actual content
            if re.match(r'^\d+(?:\.\d+)*\s+[А-Я]', text):
                heading_count += 1
                
                # Determine heading level from number pattern
                number_part = re.match(r'^(\d+(?:\.\d+)*)', text).group(1)
                level = len(number_part.split('.'))
                
                print(f"Para {i:3d}: Level H{level} Style='{paragraph.style.name}'")
                print(f"        Number: '{number_part}'")
                print(f"        Text: '{text[:80]}{'...' if len(text) > 80 else ''}'")
                print()
                
                if heading_count > 15:  # Limit output
                    print("... (showing first 15 actual headings)")
                    break
    
    print(f"\nTotal actual headings found: {heading_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_numbering3.py <docx_file>")
        sys.exit(1)
    
    analyze_headings_after_toc(sys.argv[1])