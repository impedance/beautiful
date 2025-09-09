#!/usr/bin/env python3
"""Анализ XML структуры DOCX файлов для понимания заголовков глав."""

import zipfile
import re
from pathlib import Path
from xml.etree import ElementTree as ET
import argparse


def analyze_docx_structure(docx_path: str):
    """Анализ XML структуры DOCX файла."""
    print(f"\n{'='*60}")
    print(f"АНАЛИЗ ФАЙЛА: {docx_path}")
    print(f"{'='*60}")
    
    try:
        with zipfile.ZipFile(docx_path, "r") as docx:
            # Получаем список всех файлов в архиве
            print("\nФАЙЛЫ В АРХИВЕ:")
            for file_info in docx.filelist:
                print(f"  {file_info.filename}")
            
            # Анализируем styles.xml
            if "word/styles.xml" in docx.namelist():
                print("\n" + "-"*40)
                print("АНАЛИЗ СТИЛЕЙ (styles.xml):")
                print("-"*40)
                analyze_styles(docx)
            
            # Анализируем document.xml
            if "word/document.xml" in docx.namelist():
                print("\n" + "-"*40)
                print("АНАЛИЗ ДОКУМЕНТА (document.xml):")
                print("-"*40)
                analyze_document(docx)
                
    except Exception as e:
        print(f"ОШИБКА при анализе {docx_path}: {e}")


def analyze_styles(docx: zipfile.ZipFile):
    """Анализ стилей документа."""
    try:
        styles_xml = docx.read("word/styles.xml")
        styles_root = ET.fromstring(styles_xml)
        
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        
        print("НАЙДЕННЫЕ СТИЛИ:")
        styles = styles_root.findall(".//w:style", namespaces)
        
        heading_styles = {}
        
        for style in styles:
            style_id = style.get(f"{{{namespaces['w']}}}styleId")
            style_type = style.get(f"{{{namespaces['w']}}}type")
            
            if style_id and style_type == "paragraph":
                # Получаем имя стиля
                name_elem = style.find(".//w:name", namespaces)
                name = name_elem.get(f"{{{namespaces['w']}}}val", "") if name_elem is not None else ""
                
                # Проверяем outline level
                outline_lvl_elem = style.find(".//w:outlineLvl", namespaces)
                outline_level = outline_lvl_elem.get(f"{{{namespaces['w']}}}val", "") if outline_lvl_elem is not None else ""
                
                # Определяем, является ли стиль заголовочным
                if is_heading_style(name, outline_level):
                    heading_styles[style_id] = {
                        "name": name,
                        "outline_level": outline_level
                    }
                    print(f"  ЗАГОЛОВОК: ID='{style_id}', Name='{name}', OutlineLevel='{outline_level}'")
        
        print(f"\nВСЕГО НАЙДЕНО ЗАГОЛОВОЧНЫХ СТИЛЕЙ: {len(heading_styles)}")
        return heading_styles
        
    except Exception as e:
        print(f"ОШИБКА при анализе стилей: {e}")
        return {}


def is_heading_style(name: str, outline_level: str) -> bool:
    """Определяет, является ли стиль заголовочным."""
    name_lower = name.lower()
    
    # Проверка по имени стиля
    heading_keywords = ["heading", "заголовок", "rosa"]
    if any(keyword in name_lower for keyword in heading_keywords):
        return True
    
    # Проверка по outline level
    if outline_level and outline_level.isdigit():
        level = int(outline_level)
        return 0 <= level <= 8
    
    return False


def analyze_document(docx: zipfile.ZipFile):
    """Анализ основного документа."""
    try:
        document_xml = docx.read("word/document.xml")
        root = ET.fromstring(document_xml)
        
        namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        }
        
        # Найти все параграфы с стилями
        paragraphs = root.findall(".//w:p", namespaces)
        
        print("НАЙДЕННЫЕ ЗАГОЛОВКИ В ДОКУМЕНТЕ:")
        print(f"Всего параграфов: {len(paragraphs)}")
        
        headings_found = []
        
        for i, para in enumerate(paragraphs):
            # Проверяем стиль параграфа
            style_element = para.find(".//w:pStyle", namespaces)
            if style_element is None:
                continue
            
            style_val = style_element.get(f"{{{namespaces['w']}}}val")
            if not style_val:
                continue
            
            # Извлекаем текст
            text_elements = para.findall(".//w:t", namespaces)
            text = "".join([t.text or "" for t in text_elements]).strip()
            
            if not text:
                continue
            
            # Проверяем, является ли стиль заголовочным по ID
            if is_likely_heading_style_id(style_val):
                headings_found.append({
                    "index": i,
                    "style": style_val,
                    "text": text[:100] + "..." if len(text) > 100 else text
                })
                print(f"  #{i:3d}: style='{style_val}' | text='{text[:80]}'")
        
        print(f"\nВСЕГО НАЙДЕНО ЗАГОЛОВКОВ: {len(headings_found)}")
        
        # Анализируем первые 10 заголовков детально
        print(f"\nПЕРВЫЕ 10 ЗАГОЛОВКОВ (детально):")
        for heading in headings_found[:10]:
            print(f"  {heading['index']:3d}. [{heading['style']}] {heading['text']}")
            
        return headings_found
        
    except Exception as e:
        print(f"ОШИБКА при анализе документа: {e}")
        return []


def is_likely_heading_style_id(style_id: str) -> bool:
    """Определяет, является ли ID стиля заголовочным."""
    # РОСА стили
    rosa_patterns = [
        r"ROSA.*",
        r".*[Зз]аголовок.*",
        r".*[Hh]eading.*",
    ]
    
    # Стандартные стили заголовков
    standard_patterns = [
        r"^1\d?$",  # 1, 13, и т.д.
        r"^[Hh]eading\d*$",
        r"^Title.*",
    ]
    
    all_patterns = rosa_patterns + standard_patterns
    
    for pattern in all_patterns:
        if re.match(pattern, style_id, re.IGNORECASE):
            return True
    
    return False


def main():
    parser = argparse.ArgumentParser(description='Анализ DOCX файлов для понимания структуры заголовков')
    parser.add_argument('files', nargs='*', help='DOCX файлы для анализа')
    parser.add_argument('--dir', default='input', help='Директория с DOCX файлами')
    
    args = parser.parse_args()
    
    if args.files:
        docx_files = args.files
    else:
        # Ищем все DOCX файлы в указанной директории
        input_dir = Path(args.dir)
        if not input_dir.exists():
            print(f"Директория {input_dir} не существует")
            return
        
        docx_files = list(input_dir.glob("*.docx"))
        if not docx_files:
            print(f"В директории {input_dir} не найдено DOCX файлов")
            return
    
    print("АНАЛИЗ DOCX ФАЙЛОВ")
    print("="*60)
    
    for docx_file in docx_files:
        analyze_docx_structure(str(docx_file))
    
    print(f"\n{'='*60}")
    print("АНАЛИЗ ЗАВЕРШЕН")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()