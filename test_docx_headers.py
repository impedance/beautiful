#!/usr/bin/env python3
"""
Тест с реальными заголовками из DOCX файла
"""

from improved_docx_converter import ImprovedDocxToMarkdownConverter

def test_real_headers():
    """Тестирует с реальными заголовками из DOCX"""
    
    converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
    
    # Реальные заголовки из DOCX файла
    real_headers = [
        "1    Общие сведения	5",
        "2    Архитектура комплекса	6", 
        "3    Технические и программные требования	10",
        "4    Установка и запуск комплекса	14",
        "5    Тонкая настройка операционной системы	21",
        "6    Мониторинг и диагностика	33",
        "7    Управление контентом через Winter CMS	41"
    ]
    
    print("=== Тест с реальными заголовками из DOCX ===")
    
    for header in real_headers:
        is_chapter = converter._is_chapter_header(header)
        status = "✅ ГЛАВА" if is_chapter else "❌ НЕ ГЛАВА"
        print(f"{status}: '{header}'")
        
        if is_chapter:
            chapter_info = converter._extract_chapter_info(header)
            filename = converter._generate_chapter_filename(chapter_info)
            print(f"    → Номер: {chapter_info['number']}, Название: '{chapter_info['title']}'")
            print(f"    → Файл: {filename}")
        print()

if __name__ == '__main__':
    test_real_headers()