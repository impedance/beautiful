#!/usr/bin/env python3
"""
Отладочный скрипт для проверки содержимого DOCX файла
"""

import sys
from pathlib import Path

# Добавляем в PATH для импорта конвертера
sys.path.insert(0, str(Path(__file__).parent))

from improved_docx_converter import ImprovedDocxToMarkdownConverter

def debug_docx_content():
    """Отлаживает содержимое DOCX файла"""
    
    docx_file = "dev.docx"
    
    if not Path(docx_file).exists():
        print(f"❌ Файл {docx_file} не найден")
        return
    
    print(f"=== Отладка содержимого {docx_file} ===")
    
    try:
        # Создаем конвертер
        converter = ImprovedDocxToMarkdownConverter(docx_file, split_chapters=True)
        
        print(f"✅ Конвертер создан успешно")
        
        # Проверяем элементы документа
        document_elements = []
        
        print(f"\n--- Анализ элементов документа ---")
        element_count = 0
        
        for element in converter.doc.element.body:
            element_count += 1
            
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
                    
                    element_type = f"HEADING-{heading_level}" if heading_level else "PARAGRAPH"
                    text_preview = text[:80] + "..." if len(text) > 80 else text
                    print(f"  {len(document_elements):2}: {element_type:12} | {text_preview}")
                    
                    # Проверяем, является ли заголовок главой
                    if heading_level == 1:
                        is_chapter = converter._is_chapter_header(text)
                        chapter_status = "✅ ГЛАВА" if is_chapter else "❌ НЕ ГЛАВА"
                        print(f"       -> {chapter_status}")
                        
                        if is_chapter:
                            chapter_info = converter._extract_chapter_info(text)
                            filename = converter._generate_chapter_filename(chapter_info)
                            print(f"       -> Файл: {filename}")
                            
            elif element.tag.endswith('tbl'):
                from docx.table import Table
                table = Table(element, converter.doc)
                document_elements.append({
                    'type': 'table',
                    'element': table
                })
                print(f"  {len(document_elements):2}: TABLE")
        
        print(f"\nВсего элементов в документе: {element_count}")
        print(f"Обработано элементов: {len(document_elements)}")
        
        # Тестируем разделение на главы
        print(f"\n--- Тестируем разделение на главы ---")
        chapters = converter._split_into_chapters(document_elements)
        print(f"Найдено глав: {len(chapters)}")
        
        for i, chapter in enumerate(chapters):
            print(f"\nГлава {i+1}:")
            print(f"  Номер: {chapter['info']['number']}")
            print(f"  Название: '{chapter['info']['title']}'")
            print(f"  Файл: {chapter['filename']}")
            print(f"  Элементов: {len(chapter['elements'])}")
        
        if len(chapters) == 0:
            print("❌ Главы не найдены! Проверяем причины:")
            
            heading_1_count = sum(1 for elem in document_elements if elem['type'] == 'heading' and elem['level'] == 1)
            print(f"  - Заголовков уровня 1: {heading_1_count}")
            
            if heading_1_count > 0:
                print("  - Заголовки уровня 1 найдены, проверяем _is_chapter_header:")
                for elem in document_elements:
                    if elem['type'] == 'heading' and elem['level'] == 1:
                        is_chapter = converter._is_chapter_header(elem['text'])
                        status = "✅" if is_chapter else "❌"
                        print(f"    {status} '{elem['text']}'")
            else:
                print("  - Заголовки уровня 1 не найдены")
                print("  - Проверяем все заголовки:")
                for elem in document_elements:
                    if elem['type'] == 'heading':
                        print(f"    Уровень {elem['level']}: '{elem['text']}'")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_docx_content()