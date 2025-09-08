#!/usr/bin/env python3
"""Исправление алгоритма разбиения HTML на главы."""

import sys
import re
sys.path.append('./src')

from bs4 import BeautifulSoup, Tag
from doc2md.splitter import extract_main_chapters_from_docx
from doc2md.preprocess import convert_docx_to_html
from typing import List, Optional


def improved_split_html_using_docx_structure(html_content: str, docx_path: str) -> List[str]:
    """
    Улучшенный алгоритм разбиения HTML на главы.
    
    Исправляет проблему, когда каждая глава содержит полное содержимое документа.
    """
    # Extract main chapters from DOCX using the existing algorithm
    main_chapters = extract_main_chapters_from_docx(docx_path)
    if not main_chapters:
        print(f"Warning: No main chapters found in {docx_path}")
        return []

    print(f"Found {len(main_chapters)} main chapters: {main_chapters}")

    # Parse HTML
    soup = BeautifulSoup(html_content, "lxml")
    
    # Find heading elements for all chapters
    heading_elements = []
    for i, title in enumerate(main_chapters):
        # Search for text that matches the chapter title
        pattern = re.compile(re.escape(title), re.IGNORECASE)
        
        # Find all text nodes that match the pattern
        matching_nodes = soup.find_all(string=pattern)
        
        found_element = None
        for text_node in matching_nodes:
            # Check if this text is part of a heading (not table of contents)
            parent = text_node.find_parent(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if parent:
                # Skip table of contents entries
                parent_text = parent.get_text(strip=True)
                # If the parent contains the title but also contains page numbers or tabs, skip it
                if re.search(r'\t|\d+\s*$', parent_text) and len(parent_text) > len(title) + 10:
                    continue
                
                found_element = parent
                break
        
        if found_element:
            heading_elements.append((i, title, found_element))
            print(f"Found chapter {i+1}: '{title}' in element: {found_element.name}")
        else:
            print(f"Warning: Could not find chapter '{title}' in HTML")

    if not heading_elements:
        print("No heading elements found")
        return []

    # Sort by document order
    heading_elements.sort(key=lambda x: list(soup.descendants).index(x[2]))

    # Split content between headings
    chapters = []
    for i, (chapter_idx, title, heading_element) in enumerate(heading_elements):
        next_heading_element = heading_elements[i + 1][2] if i + 1 < len(heading_elements) else None
        
        # Create chapter content
        chapter_content = []
        
        # Add chapter heading with numbering
        chapter_content.append(f"<h1>{chapter_idx + 1} {title}</h1>")
        
        # Find all content between this heading and the next
        current = heading_element.next_sibling
        while current:
            # If we reached the next chapter heading, stop
            if next_heading_element and current == next_heading_element:
                break
            
            # If we reached the next chapter heading (element or its parent), stop
            if next_heading_element and hasattr(current, 'find_parent'):
                if current.find_parent(lambda x: x == next_heading_element):
                    break
                if next_heading_element in current.descendants if hasattr(current, 'descendants') else []:
                    break
            
            # Skip whitespace-only text nodes
            if isinstance(current, str) and not current.strip():
                current = current.next_sibling
                continue
            
            # Add content to chapter
            chapter_content.append(str(current))
            current = current.next_sibling
        
        # Join chapter content
        chapter_html = "".join(chapter_content)
        chapters.append(chapter_html)
        print(f"Chapter {chapter_idx + 1} content length: {len(chapter_html)} chars")

    return chapters


def test_improved_splitting():
    """Тестирование улучшенного алгоритма разбиения."""
    files_to_test = [
        "input/dev-portal-admin.docx",
        "input/dev-portal-user.docx"
    ]
    
    for docx_path in files_to_test:
        print(f"\n{'='*60}")
        print(f"ТЕСТИРОВАНИЕ УЛУЧШЕННОГО АЛГОРИТМА: {docx_path}")
        print(f"{'='*60}")
        
        try:
            # Convert DOCX to HTML
            html_content = convert_docx_to_html(docx_path, "src/doc2md/mammoth_style_map.map")
            print(f"HTML content length: {len(html_content)} chars")
            
            # Split using improved algorithm
            chapters = improved_split_html_using_docx_structure(html_content, docx_path)
            print(f"Generated {len(chapters)} chapters")
            
            # Show preview of each chapter
            for i, chapter in enumerate(chapters[:4]):  # Show first 4 chapters
                # Extract title from chapter
                start = chapter.find('<h1>') + 4
                end = chapter.find('</h1>')
                title = chapter[start:end] if start > 3 and end > start else f"Chapter {i+1}"
                
                # Show preview
                preview = chapter[:500].replace('\n', ' ').replace('\r', ' ')
                print(f"\nГлава {i+1}: {title}")
                print(f"Размер: {len(chapter)} символов")
                print(f"Превью: {preview}...")
                
        except Exception as e:
            print(f"ОШИБКА: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_improved_splitting()