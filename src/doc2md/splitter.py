"""HTML splitting utilities."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
import json


def split_html_by_h1(html_content: str) -> List[str]:
    """Split HTML content into fragments by <h1> headings."""
    soup = BeautifulSoup(html_content, "lxml")
    chapters: List[str] = []
    
    # First try standard H1 tags
    h1_tags = soup.find_all("h1")
    if h1_tags:
        for h1 in h1_tags:
            parts = [str(h1)]
            for sibling in h1.next_siblings:
                if getattr(sibling, "name", None) == "h1":
                    break
                parts.append(str(sibling))
            chapters.append("".join(parts))
        return chapters
    
    # If no H1 tags found, try to detect chapters by numbered TOC anchors
    return _split_by_toc_anchors(soup)


def _split_by_toc_anchors(soup: BeautifulSoup) -> List[str]:
    """Split HTML by TOC anchor patterns like <a id="_Toc..."></a>."""
    # Find all anchor tags with TOC IDs that appear to be chapter markers
    toc_anchors = soup.find_all("a", id=re.compile(r"_Toc\d+"))
    
    if not toc_anchors:
        return []
    
    # Look for chapter markers - either numbered or major section headings
    chapter_markers = []
    for anchor in toc_anchors:
        # Get the text that follows this anchor
        next_text = _get_text_after_anchor(anchor)
        
        # Check if it starts with a number followed by space or dot (numbered chapters)
        if re.match(r'^\d+[\s\.]+', next_text.strip()):
            chapter_markers.append(anchor)
        # Or check if it's a major section heading (like "Общие сведения", "Веб-интерфейс", etc.)
        elif _is_major_section_heading(next_text.strip()):
            chapter_markers.append(anchor)
    
    if not chapter_markers:
        return []
    
    chapters: List[str] = []
    
    for i, marker in enumerate(chapter_markers):
        # Find the parent element of the marker (usually a <p> tag)
        marker_parent = marker.parent if marker.parent else marker
        
        chapter_parts = [str(marker_parent)]
        
        # Find all content until the next chapter marker
        current_element = marker_parent
        next_marker = chapter_markers[i + 1] if i + 1 < len(chapter_markers) else None
        next_marker_parent = next_marker.parent if next_marker and next_marker.parent else next_marker
        
        # Collect all sibling elements until we hit the next chapter
        while current_element.next_sibling:
            current_element = current_element.next_sibling
            
            # Skip whitespace-only text nodes
            if isinstance(current_element, str) and not current_element.strip():
                continue
                
            # Stop if we reached the next chapter marker or its parent
            if next_marker_parent and (current_element == next_marker_parent or
                                      (hasattr(current_element, 'find') and 
                                       current_element.find(lambda tag: tag == next_marker))):
                break
                
            chapter_parts.append(str(current_element))
        
        if chapter_parts:
            chapters.append("".join(chapter_parts))
    
    return chapters


def _is_major_section_heading(text: str) -> bool:
    """Check if text looks like a major section heading."""
    # Only recognize specific known major sections to avoid too much splitting
    major_section_patterns = [
        r'^Общие сведения$',
        r'^Установка и настройка',
        r'^Веб-интерфейс',
        r'^Настройка параметров$',
        r'^Управление поставщиками$',
        r'^Управление ресурсами$',
        r'^Контроль$',
        r'^Управление автоматизацией$',
        r'^Мониторинг',  # May have ", отчеты и оповещения" after it
        r'^Тарифы$',
        r'^Службы$',
        r'^Предоставление ВМ$',
        r'^API$',
    ]
    
    # First clean the text - remove trailing content that might be attached
    clean_text = text.strip()
    
    # For real document: split on common delimiters that indicate content continuation
    # But be careful not to split on the heading text itself
    for delimiter in ['Для доступа', 'РОСА Менеджер', 'предназначено', 'описаны в документе']:
        if delimiter in clean_text and not clean_text.startswith(delimiter):
            clean_text = clean_text.split(delimiter)[0].strip()
    
    # Check against our specific patterns
    for pattern in major_section_patterns:
        if re.match(pattern, clean_text, re.IGNORECASE):
            # Additional validation - make sure it's not too long (likely noise)
            if len(clean_text.split()) <= 4:
                return True
    
    return False


def _get_text_after_anchor(anchor) -> str:
    """Get text content immediately following an anchor tag."""
    text_parts = []
    current = anchor
    
    # Look through next siblings for text content
    for _ in range(10):  # Limit search to avoid infinite loops
        if current.next_sibling:
            current = current.next_sibling
            if hasattr(current, 'get_text'):
                text = current.get_text().strip()
                if text:
                    text_parts.append(text)
                    break
            elif isinstance(current, str) and current.strip():
                text_parts.append(current.strip())
                break
    
    return " ".join(text_parts) if text_parts else ""


def extract_headings_from_docx(docx_path: str) -> List[Dict]:
    """
    Extract chapter headings directly from DOCX XML structure with level information.
    
    Returns a list of dictionaries with heading text, level, and style information.
    This provides more reliable chapter detection than HTML parsing.
    """
    try:
        headings = []
        
        with zipfile.ZipFile(docx_path, 'r') as docx:
            # First, analyze styles to get comprehensive heading information
            heading_styles = _analyze_heading_styles(docx)
            
            # Read the main document
            document_xml = docx.read('word/document.xml')
            root = ET.fromstring(document_xml)
            
            # Define namespaces for Word XML
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            }
            
            # Find all paragraphs
            paragraphs = root.findall('.//w:p', namespaces)
            
            for i, para in enumerate(paragraphs):
                heading_info = _extract_heading_from_paragraph(para, heading_styles, namespaces, i)
                if heading_info:
                    headings.append(heading_info)
            
            return headings
    
    except Exception as e:
        print(f"Warning: Could not extract headings from DOCX: {e}")
        return []


def split_html_using_docx_structure(html_content: str, docx_path: str) -> List[str]:
    """
    Split HTML using heading structure extracted from original DOCX file.
    
    This provides a more accurate splitting by using the original document's
    heading structure rather than trying to parse converted HTML.
    """
    if not Path(docx_path).exists():
        # Fall back to HTML-only approach
        return split_html_by_h1(html_content)
    
    # Extract main chapters from DOCX using the new algorithm
    main_chapters = extract_main_chapters_from_docx(docx_path)
    if not main_chapters:
        print(f"Warning: No main chapters found in {docx_path}, falling back to HTML parsing")
        return split_html_by_h1(html_content)
    
    print(f"Found {len(main_chapters)} main chapters in DOCX: {main_chapters}")
    
    # Now split HTML based on these main chapter headings
    soup = BeautifulSoup(html_content, "lxml")
    chapters = []
    
    for i, chapter_title in enumerate(main_chapters):
        # Find this chapter title in the HTML
        chapter_elements = soup.find_all(text=re.compile(re.escape(chapter_title[:30]), re.IGNORECASE))
        
        if chapter_elements:
            # Find the element containing this text
            heading_element = chapter_elements[0].parent
            while heading_element and heading_element.name not in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading_element = heading_element.parent
            
            if heading_element:
                chapter_parts = [str(heading_element)]
                
                # Collect content until next chapter
                next_chapter = main_chapters[i + 1] if i + 1 < len(main_chapters) else None
                current_element = heading_element
                
                while current_element.next_sibling:
                    current_element = current_element.next_sibling
                    
                    # Skip whitespace-only text nodes
                    if isinstance(current_element, str) and not current_element.strip():
                        continue
                    
                    # Stop if we find the next chapter
                    if next_chapter and hasattr(current_element, 'get_text'):
                        element_text = current_element.get_text()
                        if next_chapter[:30] in element_text:
                            break
                    
                    chapter_parts.append(str(current_element))
                
                if chapter_parts:
                    chapters.append("".join(chapter_parts))
        else:
            print(f"Warning: Could not find chapter '{chapter_title}' in HTML content")
    
    return chapters if chapters else split_html_by_h1(html_content)


def _analyze_heading_styles(docx: zipfile.ZipFile) -> Dict[str, Dict]:
    """
    Анализ всех заголовочных стилей в DOCX документе.
    
    Возвращает словарь со стилями заголовков и их метаданными.
    """
    heading_styles = {}
    
    try:
        styles_xml = docx.read('word/styles.xml')
        styles_root = ET.fromstring(styles_xml)
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        styles = styles_root.findall('.//w:style', namespaces)
        
        for style in styles:
            style_id = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
            style_type = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type')
            
            if style_id and style_type == 'paragraph':
                # Получаем имя стиля
                name_elem = style.find('.//w:name', namespaces)
                name = name_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if name_elem is not None else ''
                
                # Проверяем outline level (уровень заголовка)
                outline_lvl_elem = style.find('.//w:outlineLvl', namespaces)
                outline_level = outline_lvl_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if outline_lvl_elem is not None else ''
                
                # Определяем, является ли стиль заголовочным
                is_heading = _is_heading_style(name, outline_level)
                level = _determine_heading_level(name, outline_level)
                
                if is_heading:
                    heading_styles[style_id] = {
                        'name': name,
                        'level': level,
                        'outline_level': outline_level,
                        'is_main_chapter': _is_main_chapter_style(style_id, name)
                    }
                    
    except Exception as e:
        print(f"Warning: Could not analyze heading styles: {e}")
    
    return heading_styles


def _is_heading_style(name: str, outline_level: str) -> bool:
    """Определяет, является ли стиль заголовочным."""
    name_lower = name.lower()
    
    # Проверка по имени стиля
    heading_keywords = ['heading', 'заголовок', 'rosa_заголовок']
    if any(keyword in name_lower for keyword in heading_keywords):
        return True
    
    # Проверка по outline level
    if outline_level and outline_level.isdigit():
        level = int(outline_level)
        return 0 <= level <= 8  # Обычно заголовки имеют outline level 0-8
    
    return False


def _determine_heading_level(name: str, outline_level: str) -> int:
    """Определяет уровень заголовка."""
    # Сначала пробуем определить по outline level
    if outline_level and outline_level.isdigit():
        return int(outline_level) + 1
    
    # Затем пробуем извлечь из имени стиля
    level_match = re.search(r'(\d+)', name)
    if level_match:
        return int(level_match.group(1))
    
    # По умолчанию уровень 1
    return 1


def _is_main_chapter_style(style_id: str, name: str) -> bool:
    """
    Определяет, является ли стиль стилем основных глав документа.
    
    Основные главы - это заголовки первого уровня, которые должны использоваться 
    для разделения документа на отдельные файлы.
    """
    # Для РОСА документов основные главы используют специфические стили
    rosa_main_styles = {'ROSA13', 'ROSAf1'}  # ROSA_Заголовок 1, ROSA_Заголовок_Перечень|Приложение
    if style_id in rosa_main_styles:
        return True
    
    # Стандартные стили заголовков первого уровня
    standard_main_styles = {'13', '1'}  # heading 1, ! Заголовок 1
    if style_id in standard_main_styles:
        return True
    
    # Исключаем служебные заголовки (таблицы, аннотации и т.д.)
    excluded_patterns = [
        'таблица', 'table', 'аннотация', 'annotation', 'содержание', 'toc',
        'столбец', 'column', 'перечень', 'приложение'
    ]
    
    name_lower = name.lower()
    if any(pattern in name_lower for pattern in excluded_patterns):
        return False
    
    return False


def _extract_heading_from_paragraph(para, heading_styles: Dict, namespaces: Dict, para_index: int) -> Optional[Dict]:
    """
    Извлекает информацию о заголовке из параграфа, если он является заголовком.
    """
    # Проверяем стиль параграфа
    style_element = para.find('.//w:pStyle', namespaces)
    if style_element is None:
        return None
    
    style_val = style_element.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
    if not style_val or style_val not in heading_styles:
        return None
    
    # Извлекаем текст
    text_elements = para.findall('.//w:t', namespaces)
    text = ''.join([t.text or '' for t in text_elements]).strip()
    
    if not text:
        return None
    
    style_info = heading_styles[style_val]
    
    return {
        'text': text,
        'level': style_info['level'],
        'style': style_val,
        'style_name': style_info['name'],
        'outline_level': style_info['outline_level'],
        'is_main_chapter': style_info['is_main_chapter'],
        'paragraph_index': para_index
    }


def extract_main_chapters_from_docx(docx_path: str) -> List[str]:
    """
    Извлекает только основные главы (первого уровня) из DOCX документа.
    
    Возвращает список текстов заголовков основных глав, которые должны 
    использоваться для разделения документа на отдельные файлы.
    """
    try:
        all_headings = extract_headings_from_docx(docx_path)
        
        # Фильтруем только основные главы
        main_chapters = []
        for heading in all_headings:
            if heading['is_main_chapter'] and heading['level'] == 1:
                # Дополнительная фильтрация по содержанию заголовка
                if _is_meaningful_chapter_heading(heading['text']):
                    main_chapters.append(heading['text'])
        
        return main_chapters
        
    except Exception as e:
        print(f"Warning: Could not extract main chapters: {e}")
        return []


def _is_meaningful_chapter_heading(text: str) -> bool:
    """
    Проверяет, является ли заголовок содержательной главой документа.
    
    Исключает служебные заголовки типа "Содержание", "Аннотация" и т.д.
    """
    text_lower = text.lower().strip()
    
    # Исключаем служебные разделы
    excluded_headings = {
        'аннотация', 'содержание', 'оглавление', 'перечень сокращений',
        'список сокращений', 'сокращение', 'расшифровка', 'пояснение',
        'список терминов', 'термины', 'глоссарий'
    }
    
    if text_lower in excluded_headings:
        return False
    
    # Исключаем заголовки таблиц
    if any(word in text_lower for word in ['версия ос', 'операционная система', 'процессор',
                                          'google chrome', 'yandex browser', 'mozilla firefox',
                                          'safari', 'браузер']):
        return False
    
    # Включаем только содержательные главы
    meaningful_patterns = [
        r'^общие сведения',
        r'^начало работы',
        r'^компоненты',
        r'^функции',
        r'^установка',
        r'^настройка',
        r'^управление',
        r'^администрирование',
        r'^использование',
        r'интерфейс',
        r'описание',
        r'руководство'
    ]
    
    for pattern in meaningful_patterns:
        if re.match(pattern, text_lower):
            return True
    
    # Если заголовок достаточно длинный (больше одного слова), скорее всего это содержательная глава
    return len(text.split()) > 1
