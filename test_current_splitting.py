#!/usr/bin/env python3
"""Тестирование текущего процесса разбиения документов."""

import sys
import os
sys.path.append('./src')

from doc2md.preprocess import convert_docx_to_html
from doc2md.splitter import split_html_using_docx_structure

def test_current_splitting(docx_path: str, style_map_path: str = "src/doc2md/mammoth_style_map.map"):
    print(f"\n{'='*60}")
    print(f"ТЕСТИРОВАНИЕ РАЗБИЕНИЯ: {docx_path}")
    print(f"{'='*60}")
    
    try:
        # Шаг 1: Конвертация DOCX в HTML
        print("1. Конвертация DOCX в HTML...")
        html_content = convert_docx_to_html(docx_path, style_map_path)
        print(f"   HTML длина: {len(html_content)} символов")
        
        # Шаг 2: Разбиение HTML на главы
        print("2. Разбиение HTML на главы...")
        chapters = split_html_using_docx_structure(html_content, docx_path)
        print(f"   Найдено глав: {len(chapters)}")
        
        # Показать информацию о каждой главе
        print("\n3. ИНФОРМАЦИЯ О ГЛАВАХ:")
        for i, chapter in enumerate(chapters):
            # Извлекаем заголовок главы
            start = chapter.find('<h1>') + 4
            end = chapter.find('</h1>')
            if start > 3 and end > start:
                title = chapter[start:end]
            else:
                title = chapter[:100] + "..."
            
            print(f"   Глава {i+1}: {title}")
            print(f"   Размер: {len(chapter)} символов")
            
            # Показываем первые 200 символов содержимого
            preview = chapter[:200].replace('\n', ' ').replace('\r', ' ')
            print(f"   Превью: {preview}...")
            print()
        
        return chapters
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    files_to_test = [
        "input/dev-portal-admin.docx",
        "input/dev-portal-user.docx"
    ]
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            chapters = test_current_splitting(file_path)
            if len(chapters) < 4:
                print(f"\n⚠️  ПРОБЛЕМА: Найдено только {len(chapters)} глав вместо ожидаемых 4+ глав")
        else:
            print(f"❌ Файл не найден: {file_path}")

if __name__ == "__main__":
    main()