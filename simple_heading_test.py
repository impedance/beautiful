#!/usr/bin/env python3
"""Simple test for heading extraction using regex."""

from bs4 import BeautifulSoup
import re
from src.doc2md.heading_numbering import extract_heading_structure_from_toc

def simple_heading_extraction(html_content: str, docx_path: str) -> str:
    """Simple approach to extract headings based on __RefHeading patterns."""
    
    # Get TOC structure
    heading_structure = extract_heading_structure_from_toc(docx_path)
    title_to_info = {}
    for level, number, title in heading_structure:
        title_to_info[title.lower()] = (level, number, title)
    
    # Use regex to find patterns like: <a id="__RefHeading___X"></a>TextHere
    # This pattern matches anchor + immediate heading text
    pattern = r'<a id="__RefHeading___\d+"></a>([А-ЯЁA-Z][а-яёa-z\s]+?)(?=Программный|[.!?]|[А-ЯЁA-Z]{3,}|<|\s{2,}|$)'
    
    def replace_heading(match):
        heading_text = match.group(1).strip()
        heading_lower = heading_text.lower()
        
        # Find match in TOC
        if heading_lower in title_to_info:
            level, number, original_title = title_to_info[heading_lower]
            return f'<h{level}>{number} {original_title}</h{level}>'
        
        return match.group(0)  # No change if not found
    
    # Apply replacement
    result = re.sub(pattern, replace_heading, html_content)
    return result


# Test
if __name__ == "__main__":
    # Read the actual HTML file
    with open("output_dir_fixed/html/full_document.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Extract a sample with headings - get full anchor tag
    start_pos = html_content.find('<a id="__RefHeading___4">')
    sample = html_content[start_pos:start_pos + 1000]
    print("Sample HTML:")
    print(sample)
    print("\n" + "="*60 + "\n")
    
    result = simple_heading_extraction(sample, "dev-portal-admin.docx")
    print("Processed HTML:")
    print(result)