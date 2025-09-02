#!/usr/bin/env python3
"""
Отладка распределения текста по главам
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from improved_docx_converter import ImprovedDocxToMarkdownConverter

def debug_text_distribution():
    """Отлаживает как текст распределяется по главам"""
    
    docx_file = "dev.docx"
    
    if not Path(docx_file).exists():
        print(f"❌ Файл {docx_file} не найден")
        return
    
    print(f"=== Отладка распределения текста по главам ===")
    
    try:
        converter = ImprovedDocxToMarkdownConverter(docx_file, split_chapters=True)
        
        # Собираем элементы документа
        document_elements = []
        
        for element in converter.doc.element.body:
            if element.tag.endswith('p'):
                from docx.text.paragraph import Paragraph
                para = Paragraph(element, converter.doc)
                text = para.text.strip()
                
                if text:
                    heading_level = converter._is_heading(para)
                    element_info = {
                        'type': 'heading' if heading_level else 'paragraph',
                        'level': heading_level if heading_level else 0,
                        'text': text,
                        'element': para
                    }
                    document_elements.append(element_info)
            elif element.tag.endswith('tbl'):
                from docx.table import Table
                table = Table(element, converter.doc)
                document_elements.append({
                    'type': 'table',
                    'element': table
                })
        
        print(f"Всего элементов в документе: {len(document_elements)}")
        
        # Разделяем на главы
        chapters = converter._split_into_chapters(document_elements)
        print(f"Найдено глав: {len(chapters)}")
        
        for i, chapter in enumerate(chapters):
            chapter_title = chapter['info']['title']
            elements_count = len(chapter['elements'])
            
            # Подсчитываем типы элементов
            headings = sum(1 for e in chapter['elements'] if e['type'] == 'heading')
            paragraphs = sum(1 for e in chapter['elements'] if e['type'] == 'paragraph')
            tables = sum(1 for e in chapter['elements'] if e['type'] == 'table')
            
            print(f"\nГлава {i+1}: '{chapter_title}'")
            print(f"  Всего элементов: {elements_count}")
            print(f"  Заголовки: {headings}")
            print(f"  Абзацы: {paragraphs}")
            print(f"  Таблицы: {tables}")
            
            # Показываем первые несколько элементов каждой главы
            print("  Первые элементы:")
            for j, elem in enumerate(chapter['elements'][:5]):
                elem_type = elem['type']
                if elem_type == 'heading':
                    text_preview = elem['text'][:60]
                elif elem_type == 'paragraph':
                    text_preview = elem['text'][:60] + "..." if len(elem['text']) > 60 else elem['text']
                else:
                    text_preview = "TABLE"
                    
                print(f"    {j+1}. {elem_type.upper()}: {text_preview}")
            
            if elements_count > 5:
                print(f"    ... и еще {elements_count - 5} элементов")
        
        # Ищем где начинается основной текст
        print(f"\n=== Анализ начала основного текста ===")
        main_text_start = -1
        for i, elem in enumerate(document_elements):
            if elem['type'] == 'heading' and elem['level'] == 3:
                # Заголовки уровня 3, которые не в содержании
                if "Общие сведения" in elem['text'] and "	" not in elem['text']:
                    main_text_start = i
                    break
        
        if main_text_start > 0:
            print(f"Основной текст начинается с элемента {main_text_start}: '{document_elements[main_text_start]['text']}'")
            print(f"До этого было {main_text_start} элементов содержания")
        else:
            print("❌ Не удалось найти начало основного текста")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_text_distribution()