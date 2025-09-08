#!/usr/bin/env python3
"""Финальное исправление алгоритма разбиения HTML на главы."""

import sys
import re
from typing import List, Optional, Dict, Any
sys.path.append('./src')

from bs4 import BeautifulSoup, Tag, NavigableString
from pathlib import Path


def improved_extract_main_chapters_from_docx(docx_path: str, limit: int = 4) -> List[Dict[str, Any]]:
    """
    Извлекает только первые N основных глав (первого уровня) из DOCX документа.
    
    Возвращает список словарей с информацией о главах включая их позицию.
    """
    import zipfile
    from xml.etree import ElementTree as ET
    
    try:
        headings = []
        
        with zipfile.ZipFile(docx_path, "r") as docx:
            # Анализ стилей
            heading_styles = _analyze_heading_styles(docx)
            
            # Чтение основного документа
            document_xml = docx.read("word/document.xml")
            root = ET.fromstring(document_xml)
            
            namespaces = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            }
            
            paragraphs = root.findall(".//w:p", namespaces)
            
            for i, para in enumerate(paragraphs):
                heading_info = _extract_heading_from_paragraph(
                    para, heading_styles, namespaces, i
                )
                if heading_info:
                    headings.append(heading_info)
        
        # Фильтруем только основные главы первого уровня
        main_chapters = []
        for heading in headings:
            if (heading["is_main_chapter"] and 
                heading["level"] == 1 and 
                _is_meaningful_chapter_heading(heading["text"])):
                main_chapters.append({
                    'title': heading["text"],
                    'position': heading["paragraph_index"],
                    'style': heading["style"]
                })
        
        # Сортируем по позиции в документе и берём первые N
        main_chapters.sort(key=lambda x: x['position'])
        return main_chapters[:limit]
        
    except Exception as e:
        print(f"Warning: Could not extract main chapters: {e}")
        return []


def _analyze_heading_styles(docx):
    """Анализ заголовочных стилей."""
    heading_styles = {}
    
    try:
        styles_xml = docx.read("word/styles.xml")
        styles_root = ET.fromstring(styles_xml)
        
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        styles = styles_root.findall(".//w:style", namespaces)
        
        for style in styles:
            style_id = style.get(f"{{{namespaces['w']}}}styleId")
            style_type = style.get(f"{{{namespaces['w']}}}type")
            
            if style_id and style_type == "paragraph":
                name_elem = style.find(".//w:name", namespaces)
                name = name_elem.get(f"{{{namespaces['w']}}}val", "") if name_elem is not None else ""
                
                outline_lvl_elem = style.find(".//w:outlineLvl", namespaces)
                outline_level = outline_lvl_elem.get(f"{{{namespaces['w']}}}val", "") if outline_lvl_elem is not None else ""
                
                is_heading = _is_heading_style(name, outline_level)
                level = _determine_heading_level(name, outline_level)
                
                if is_heading:
                    heading_styles[style_id] = {
                        "name": name,
                        "level": level,
                        "outline_level": outline_level,
                        "is_main_chapter": _is_main_chapter_style(style_id, name),
                    }
    except Exception as e:
        print(f"Warning: Could not analyze heading styles: {e}")
    
    return heading_styles


def _is_heading_style(name: str, outline_level: str) -> bool:
    """Определяет, является ли стиль заголовочным."""
    name_lower = name.lower()
    heading_keywords = ["heading", "заголовок", "rosa"]
    if any(keyword in name_lower for keyword in heading_keywords):
        return True
    
    if outline_level and outline_level.isdigit():
        level = int(outline_level)
        return 0 <= level <= 8
    
    return False


def _determine_heading_level(name: str, outline_level: str) -> int:
    """Определяет уровень заголовка."""
    if outline_level and outline_level.isdigit():
        return int(outline_level) + 1
    
    level_match = re.search(r"(\d+)", name)
    if level_match:
        return int(level_match.group(1))
    
    return 1


def _is_main_chapter_style(style_id: str, name: str) -> bool:
    """Определяет, является ли стиль стилем основных глав документа."""
    rosa_main_styles = {"ROSA13", "ROSAf1"}
    if style_id in rosa_main_styles:
        return True
    
    standard_main_styles = {"13", "1"}
    if style_id in standard_main_styles:
        return True
    
    excluded_patterns = [
        "таблица", "table", "аннотация", "annotation",
        "содержание", "toc", "столбец", "column", "перечень", "приложение",
    ]
    
    name_lower = name.lower()
    if any(pattern in name_lower for pattern in excluded_patterns):
        return False
    
    return False


def _extract_heading_from_paragraph(para, heading_styles: Dict, namespaces: Dict, para_index: int):
    """Извлекает информацию о заголовке из параграфа."""
    from xml.etree import ElementTree as ET
    
    style_element = para.find(".//w:pStyle", namespaces)
    if style_element is None:
        return None
    
    style_val = style_element.get(f"{{{namespaces['w']}}}val")
    if not style_val or style_val not in heading_styles:
        return None
    
    text_elements = para.findall(".//w:t", namespaces)
    text = "".join([t.text or "" for t in text_elements]).strip()
    
    if not text:
        return None
    
    style_info = heading_styles[style_val]
    
    return {
        "text": text,
        "level": style_info["level"],
        "style": style_val,
        "style_name": style_info["name"],
        "outline_level": style_info["outline_level"],
        "is_main_chapter": style_info["is_main_chapter"],
        "paragraph_index": para_index,
    }


def _is_meaningful_chapter_heading(text: str) -> bool:
    """Проверяет, является ли заголовок содержательной главой документа."""
    text_lower = text.lower().strip()
    
    excluded_headings = {
        "аннотация", "содержание", "оглавление", "перечень сокращений",
        "список сокращений", "сокращение", "расшифровка", "пояснение",
        "список терминов", "термины", "глоссарий",
    }
    
    if text_lower in excluded_headings:
        return False
    
    if any(word in text_lower for word in [
        "версия ос", "операционная система", "процессор", "google chrome",
        "yandex browser", "mozilla firefox", "safari", "браузер",
    ]):
        return False
    
    meaningful_patterns = [
        r"^общие сведения", r"^начало работы", r"^компоненты", r"^функции",
        r"^установка", r"^настройка", r"^управление", r"^администрирование",
        r"^использование", r"интерфейс", r"описание", r"руководство",
    ]
    
    for pattern in meaningful_patterns:
        if re.match(pattern, text_lower):
            return True
    
    return len(text.split()) > 1


def final_improved_split_html_using_docx_structure(html_content: str, docx_path: str) -> List[str]:
    """
    Финальная улучшенная версия алгоритма разбиения HTML на главы.
    
    Исправляет все найденные проблемы и извлекает первые 4 главы.
    """
    if not Path(docx_path).exists():
        print(f"Warning: DOCX file not found: {docx_path}")
        return []
    
    # Извлекаем только первые 4 основные главы
    main_chapters = improved_extract_main_chapters_from_docx(docx_path, limit=4)
    if not main_chapters:
        print(f"Warning: No main chapters found in {docx_path}")
        return []
    
    print(f"Found {len(main_chapters)} main chapters:")
    for i, chapter in enumerate(main_chapters):
        print(f"  {i+1}. [{chapter['style']}] {chapter['title']}")
    
    # Парсим HTML
    soup = BeautifulSoup(html_content, "lxml")
    
    # Находим элементы заголовков для каждой главы
    heading_elements = []
    for chapter_info in main_chapters:
        title = chapter_info['title']
        
        # Ищем точное совпадение в HTML
        found_element = None
        
        # Поиск по тексту заголовка
        all_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        
        for elem in all_elements:
            elem_text = elem.get_text(strip=True)
            
            # Точное совпадение
            if elem_text == title:
                # Проверяем, что это не оглавление (содержит номер страницы)
                if not re.search(r'\t\d+\s*$', elem_text) and 'toc' not in elem.get('class', []):
                    found_element = elem
                    break
            
            # Частичное совпадение для случаев с нумерацией
            if title in elem_text and len(elem_text) - len(title) < 10:
                if not re.search(r'\t\d+\s*$', elem_text) and 'toc' not in elem.get('class', []):
                    found_element = elem
                    break
        
        if found_element:
            heading_elements.append((chapter_info, found_element))
            print(f"Found heading for '{title}' in <{found_element.name}>")
        else:
            print(f"Warning: Could not find heading for '{title}' in HTML")
    
    if not heading_elements:
        print("No heading elements found")
        return []
    
    # Сортируем по порядку в документе
    def element_position(elem_tuple):
        _, element = elem_tuple
        return list(soup.descendants).index(element)
    
    heading_elements.sort(key=element_position)
    
    # Разбиваем контент между заголовками
    chapters = []
    for i, (chapter_info, heading_element) in enumerate(heading_elements):
        next_heading_element = heading_elements[i + 1][1] if i + 1 < len(heading_elements) else None
        
        chapter_content = []
        
        # Добавляем заголовок главы с нумерацией
        chapter_content.append(f"<h1>{i + 1} {chapter_info['title']}</h1>")
        
        # Собираем весь контент между текущим и следующим заголовком
        current = heading_element
        
        while current:
            current = current.next_sibling
            
            if not current:
                break
            
            # Если дошли до следующего заголовка, останавливаемся
            if next_heading_element and current == next_heading_element:
                break
            
            # Пропускаем пустые текстовые узлы
            if isinstance(current, NavigableString) and not str(current).strip():
                continue
            
            # Добавляем контент
            chapter_content.append(str(current))
        
        # Объединяем контент главы
        chapter_html = "".join(chapter_content)
        chapters.append(chapter_html)
        
        print(f"Chapter {i + 1} '{chapter_info['title']}' content length: {len(chapter_html)} chars")
    
    return chapters


def test_final_algorithm():
    """Тестирование финального алгоритма."""
    from doc2md.preprocess import convert_docx_to_html
    
    files_to_test = [
        "input/dev-portal-admin.docx",
        "input/dev-portal-user.docx"
    ]
    
    for docx_path in files_to_test:
        print(f"\n{'='*70}")
        print(f"ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ: {docx_path}")
        print(f"{'='*70}")
        
        try:
            # Конвертируем DOCX в HTML
            html_content = convert_docx_to_html(docx_path, "src/doc2md/mammoth_style_map.map")
            print(f"HTML content length: {len(html_content)} chars")
            
            # Разбиваем с помощью финального алгоритма
            chapters = final_improved_split_html_using_docx_structure(html_content, docx_path)
            print(f"Generated {len(chapters)} chapters")
            
            # Показываем информацию о каждой главе
            for i, chapter in enumerate(chapters):
                # Извлекаем заголовок
                start = chapter.find('<h1>') + 4
                end = chapter.find('</h1>')
                title = chapter[start:end] if start > 3 and end > start else f"Chapter {i+1}"
                
                # Показываем превью
                preview = chapter[:300].replace('\n', ' ').replace('\r', ' ')
                print(f"\n--- Глава {i+1}: {title} ---")
                print(f"Размер: {len(chapter)} символов")
                print(f"Превью: {preview}...")
                
                # Проверяем уникальность содержимого
                unique_content = set(chapter.split())
                print(f"Уникальных слов: {len(unique_content)}")
        
        except Exception as e:
            print(f"ОШИБКА: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_final_algorithm()