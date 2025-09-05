#!/usr/bin/env python3
"""Search for specific text in DOCX."""

import sys
from docx import Document

def search_text_in_docx(docx_path: str, search_text: str):
    """Search for text in DOCX paragraphs."""
    doc = Document(docx_path)
    
    matches = []
    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        if search_text.lower() in text.lower():
            matches.append((i, text, paragraph.style.name))
    
    return matches

if __name__ == "__main__":
    docx_path = "rosa-mr.docx"
    
    search_terms = [
        "подготовка конфигурационных файлов",
        "4.1.2.1",
        "подготовка",
        "конфигурационных файлов",
        "traefik"
    ]
    
    for term in search_terms:
        print(f"Searching for: '{term}'")
        matches = search_text_in_docx(docx_path, term)
        
        if matches:
            print(f"  Found {len(matches)} matches:")
            for i, (para_num, text, style) in enumerate(matches[:5]):  # Show first 5
                print(f"    {i+1}. Para {para_num}: Style='{style}'")
                print(f"       Text: '{text[:80]}{'...' if len(text) > 80 else ''}'")
        else:
            print(f"  No matches found")
        print()