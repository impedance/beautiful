#!/usr/bin/env python3
"""
Скрипт для анализа XML структуры DOCX файла и извлечения информации о заголовках.
Этот скрипт поможет переписать алгоритм разделения на главы.
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Tuple
import re


def analyze_docx_structure(docx_path: str) -> Dict:
    """Полный анализ структуры DOCX файла."""
    
    if not Path(docx_path).exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
    
    analysis = {
        'file_path': docx_path,
        'styles': {},
        'heading_styles': {},
        'paragraphs': [],
        'headings': [],
        'toc_entries': [],
        'document_structure': []
    }
    
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx:
            # 1. Анализ стилей
            analysis['styles'] = analyze_styles(docx)
            
            # 2. Анализ заголовочных стилей
            analysis['heading_styles'] = extract_heading_styles(docx, analysis['styles'])
            
            # 3. Анализ основного документа
            doc_analysis = analyze_document(docx, analysis['heading_styles'])
            analysis.update(doc_analysis)
            
            # 4. Поиск TOC (Table of Contents)
            analysis['toc_entries'] = extract_toc_entries(docx)
            
    except Exception as e:
        print(f"Error analyzing DOCX: {e}")
        return analysis
    
    return analysis


def analyze_styles(docx: zipfile.ZipFile) -> Dict:
    """Анализ всех стилей в документе."""
    styles_info = {}
    
    try:
        styles_xml = docx.read('word/styles.xml')
        styles_root = ET.fromstring(styles_xml)
        
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        styles = styles_root.findall('.//w:style', namespaces)
        
        for style in styles:
            style_id = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
            style_type = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type')
            
            if style_id:
                # Получаем имя стиля
                name_elem = style.find('.//w:name', namespaces)
                name = name_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if name_elem is not None else ''
                
                # Получаем базовый стиль
                based_on_elem = style.find('.//w:basedOn', namespaces)
                based_on = based_on_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if based_on_elem is not None else ''
                
                # Получаем следующий стиль
                next_elem = style.find('.//w:next', namespaces)
                next_style = next_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if next_elem is not None else ''
                
                # Проверяем outline level (уровень заголовка)
                outline_lvl_elem = style.find('.//w:outlineLvl', namespaces)
                outline_level = outline_lvl_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '') if outline_lvl_elem is not None else ''
                
                styles_info[style_id] = {
                    'name': name,
                    'type': style_type,
                    'based_on': based_on,
                    'next': next_style,
                    'outline_level': outline_level
                }
                
    except Exception as e:
        print(f"Error analyzing styles: {e}")
    
    return styles_info


def extract_heading_styles(docx: zipfile.ZipFile, styles_info: Dict) -> Dict:
    """Извлечение стилей заголовков."""
    heading_styles = {}
    
    # Метод 1: По имени стиля
    for style_id, style_info in styles_info.items():
        name_lower = style_info['name'].lower()
        if 'heading' in name_lower or 'заголовок' in name_lower:
            # Определяем уровень заголовка
            level = 1  # по умолчанию
            
            # Попытка извлечь уровень из имени
            level_match = re.search(r'(\d+)', style_info['name'])
            if level_match:
                level = int(level_match.group(1))
            elif style_info['outline_level']:
                try:
                    level = int(style_info['outline_level']) + 1
                except:
                    pass
                    
            heading_styles[style_id] = {
                'name': style_info['name'],
                'level': level,
                'outline_level': style_info['outline_level']
            }
    
    # Метод 2: По outline level
    for style_id, style_info in styles_info.items():
        if style_info['outline_level'] and style_id not in heading_styles:
            try:
                outline_level = int(style_info['outline_level'])
                if 0 <= outline_level <= 8:  # Обычно заголовки имеют outline level 0-8
                    heading_styles[style_id] = {
                        'name': style_info['name'],
                        'level': outline_level + 1,
                        'outline_level': style_info['outline_level']
                    }
            except:
                pass
    
    return heading_styles


def analyze_document(docx: zipfile.ZipFile, heading_styles: Dict) -> Dict:
    """Анализ основного документа."""
    document_xml = docx.read('word/document.xml')
    root = ET.fromstring(document_xml)
    
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    }
    
    paragraphs = []
    headings = []
    document_structure = []
    
    # Найдем все параграфы
    paras = root.findall('.//w:p', namespaces)
    
    for i, para in enumerate(paras):
        para_info = {
            'index': i,
            'style': None,
            'text': '',
            'is_heading': False,
            'heading_level': None,
            'outline_level': None
        }
        
        # Получаем стиль параграфа
        style_element = para.find('.//w:pStyle', namespaces)
        if style_element is not None:
            style_val = style_element.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
            para_info['style'] = style_val
            
            # Проверяем, является ли это заголовком
            if style_val in heading_styles:
                para_info['is_heading'] = True
                para_info['heading_level'] = heading_styles[style_val]['level']
                para_info['outline_level'] = heading_styles[style_val]['outline_level']
        
        # Получаем прямой outline level из параграфа
        outline_lvl_elem = para.find('.//w:outlineLvl', namespaces)
        if outline_lvl_elem is not None:
            outline_level = outline_lvl_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')
            if outline_level:
                para_info['outline_level'] = outline_level
                para_info['is_heading'] = True
                try:
                    para_info['heading_level'] = int(outline_level) + 1
                except:
                    pass
        
        # Извлекаем текст
        text_elements = para.findall('.//w:t', namespaces)
        text = ''.join([t.text or '' for t in text_elements]).strip()
        para_info['text'] = text
        
        paragraphs.append(para_info)
        
        # Если это заголовок, добавляем в список заголовков
        if para_info['is_heading'] and text:
            heading_info = {
                'text': text,
                'level': para_info['heading_level'],
                'style': para_info['style'],
                'outline_level': para_info['outline_level'],
                'paragraph_index': i
            }
            headings.append(heading_info)
            document_structure.append(heading_info)
    
    return {
        'paragraphs': paragraphs,
        'headings': headings,
        'document_structure': document_structure
    }


def extract_toc_entries(docx: zipfile.ZipFile) -> List[Dict]:
    """Поиск записей в таблице содержания (TOC)."""
    toc_entries = []
    
    try:
        document_xml = docx.read('word/document.xml')
        root = ET.fromstring(document_xml)
        
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        }
        
        # Поиск TOC полей
        toc_fields = root.findall('.//w:fldSimple[@w:instr]', namespaces)
        for field in toc_fields:
            instr = field.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr', '')
            if 'TOC' in instr.upper():
                text_elements = field.findall('.//w:t', namespaces)
                text = ''.join([t.text or '' for t in text_elements]).strip()
                if text:
                    toc_entries.append({
                        'text': text,
                        'instruction': instr
                    })
        
        # Поиск сложных TOC полей
        fld_chars = root.findall('.//w:fldChar', namespaces)
        in_toc_field = False
        toc_text_parts = []
        
        for fld_char in fld_chars:
            fld_char_type = fld_char.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType')
            
            if fld_char_type == 'begin':
                # Проверяем, начинается ли TOC поле
                parent = fld_char.getparent()
                if parent is not None:
                    instr_text = parent.find('.//w:instrText', namespaces)
                    if instr_text is not None and 'TOC' in (instr_text.text or '').upper():
                        in_toc_field = True
                        toc_text_parts = []
            elif fld_char_type == 'end' and in_toc_field:
                in_toc_field = False
                if toc_text_parts:
                    toc_text = ''.join(toc_text_parts).strip()
                    if toc_text:
                        toc_entries.append({
                            'text': toc_text,
                            'instruction': 'TOC'
                        })
            elif in_toc_field:
                # Собираем текст внутри TOC поля
                parent = fld_char.getparent()
                if parent is not None:
                    text_elements = parent.findall('.//w:t', namespaces)
                    for t in text_elements:
                        if t.text:
                            toc_text_parts.append(t.text)
    
    except Exception as e:
        print(f"Error extracting TOC: {e}")
    
    return toc_entries


def print_analysis_report(analysis: Dict):
    """Выводит подробный отчет об анализе структуры документа."""
    print(f"\n=== АНАЛИЗ СТРУКТУРЫ DOCX: {analysis['file_path']} ===\n")
    
    # Статистика
    print("📊 СТАТИСТИКА:")
    print(f"  • Всего стилей: {len(analysis['styles'])}")
    print(f"  • Стилей заголовков: {len(analysis['heading_styles'])}")
    print(f"  • Всего параграфов: {len(analysis['paragraphs'])}")
    print(f"  • Найдено заголовков: {len(analysis['headings'])}")
    print(f"  • Записей TOC: {len(analysis['toc_entries'])}")
    
    # Стили заголовков
    print("\n📝 СТИЛИ ЗАГОЛОВКОВ:")
    for style_id, style_info in analysis['heading_styles'].items():
        print(f"  • {style_id}: {style_info['name']} (уровень {style_info['level']})")
    
    # Структура документа (заголовки)
    print("\n📋 СТРУКТУРА ДОКУМЕНТА:")
    for i, heading in enumerate(analysis['headings'], 1):
        indent = "  " * (heading['level'] - 1)
        print(f"{indent}{i}. [{heading['level']}] {heading['text'][:80]}{'...' if len(heading['text']) > 80 else ''}")
        print(f"{indent}   Стиль: {heading['style']}, Outline: {heading['outline_level']}")
    
    # Главы первого уровня
    level_1_headings = [h for h in analysis['headings'] if h['level'] == 1]
    print(f"\n🏷️  ГЛАВЫ ПЕРВОГО УРОВНЯ ({len(level_1_headings)}):")
    for i, heading in enumerate(level_1_headings, 1):
        print(f"  {i}. {heading['text']}")
    
    # TOC записи
    if analysis['toc_entries']:
        print(f"\n📑 ТАБЛИЦА СОДЕРЖАНИЯ ({len(analysis['toc_entries'])} записей):")
        for entry in analysis['toc_entries']:
            print(f"  • {entry['text'][:100]}{'...' if len(entry['text']) > 100 else ''}")


if __name__ == "__main__":
    import sys
    
    docx_file = sys.argv[1] if len(sys.argv) > 1 else "dev-portal-user.docx"
    
    if not Path(docx_file).exists():
        print(f"Файл не найден: {docx_file}")
        sys.exit(1)
    
    print(f"Анализируем файл: {docx_file}")
    
    try:
        analysis = analyze_docx_structure(docx_file)
        print_analysis_report(analysis)
        
        # Сохраняем результаты в JSON для дальнейшего использования
        import json
        output_file = f"{Path(docx_file).stem}_analysis.json"
        
        # Преобразуем для JSON сериализации
        json_analysis = {
            'file_path': analysis['file_path'],
            'statistics': {
                'total_styles': len(analysis['styles']),
                'heading_styles': len(analysis['heading_styles']),
                'total_paragraphs': len(analysis['paragraphs']),
                'total_headings': len(analysis['headings']),
                'toc_entries': len(analysis['toc_entries'])
            },
            'heading_styles': analysis['heading_styles'],
            'headings': analysis['headings'],
            'level_1_headings': [h for h in analysis['headings'] if h['level'] == 1],
            'toc_entries': analysis['toc_entries']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_analysis, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в: {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        sys.exit(1)