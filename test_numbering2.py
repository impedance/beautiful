#!/usr/bin/env python3
"""Test script to extract heading numbering from DOCX - enhanced version."""

import sys
from docx import Document


def extract_numbering_text(paragraph):
    """Extract visible numbering text from a paragraph."""
    # Try to get the numbering text directly
    if paragraph._element.xpath('.//w:t'):
        text_elements = []
        for run in paragraph.runs:
            for elem in run._element.xpath('.//w:t'):
                text_elements.append(elem.text)
        full_text = ''.join(text_elements)
        
        # Look for patterns like "4.1.2.1" at the start
        import re
        number_match = re.match(r'^(\d+(?:\.\d+)*)\s+', full_text)
        if number_match:
            return number_match.group(1)
    
    return None


def analyze_docx_all_paragraphs(docx_path: str):
    """Analyze all DOCX paragraphs looking for numbering patterns."""
    doc = Document(docx_path)
    
    print(f"Analyzing all paragraphs in {docx_path}...")
    print("=" * 60)
    
    heading_count = 0
    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
            
        # Look for numbered headings
        import re
        if re.match(r'^\d+(?:\.\d+)*\s+\w', text):
            numbering = extract_numbering_text(paragraph)
            heading_count += 1
            
            print(f"Para {i:3d}: Style='{paragraph.style.name}'")
            print(f"        Numbering: {numbering}")
            print(f"        Text: '{text[:80]}{'...' if len(text) > 80 else ''}'")
            
            # Check for actual Word numbering
            has_word_numbering = False
            if paragraph._p.pPr is not None and paragraph._p.pPr.numPr is not None:
                num_id = paragraph._p.pPr.numPr.numId
                ilvl = paragraph._p.pPr.numPr.ilvl
                if num_id is not None and ilvl is not None:
                    has_word_numbering = True
                    print(f"        Word numbering: numId={num_id.val}, level={ilvl.val}")
            
            if not has_word_numbering:
                print(f"        Word numbering: None (text-based numbering)")
            
            print()
            
            if heading_count > 20:  # Limit output
                print("... (showing first 20 numbered headings)")
                break
    
    print(f"\nTotal numbered headings found: {heading_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_numbering2.py <docx_file>")
        sys.exit(1)
    
    analyze_docx_all_paragraphs(sys.argv[1])