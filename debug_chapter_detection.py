#!/usr/bin/env python3
"""
Отладочный скрипт для проверки определения заголовков глав
"""

from improved_docx_converter import ImprovedDocxToMarkdownConverter
import re

def test_chapter_header_detection():
    """Тестирует определение заголовков глав"""
    
    # Создаем экземпляр конвертера для тестирования методов
    converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
    
    # Тестовые заголовки
    test_headers = [
        "1. Общие сведения",
        "2. Архитектура комплекса",
        "3. Технические требования",
        "1.1 Функциональное назначение",  # НЕ должен быть главой
        "2.1 Основные компоненты",        # НЕ должен быть главой
        "АО \"НТЦ ИТ РОСА\"",             # НЕ должен быть главой
        "ПРОГРАММНЫЙ КОМПЛЕКС",           # НЕ должен быть главой
        "4. Установка и настройка",
        "5. Эксплуатация системы"
    ]
    
    print("=== Тест определения заголовков глав ===")
    
    for header in test_headers:
        is_chapter = converter._is_chapter_header(header)
        status = "✅ ГЛАВА" if is_chapter else "❌ НЕ ГЛАВА"
        print(f"{status}: '{header}'")
        
        if is_chapter:
            chapter_info = converter._extract_chapter_info(header)
            filename = converter._generate_chapter_filename(chapter_info)
            print(f"    → Номер: {chapter_info['number']}, Название: '{chapter_info['title']}'")
            print(f"    → Файл: {filename}")
        print()

def test_regex_patterns():
    """Тестирует regex паттерны"""
    
    print("=== Тест regex паттернов ===")
    
    test_cases = [
        "1. Общие сведения",
        "2. Архитектура комплекса", 
        "3. Технические требования",
        "10. Десятая глава",
        "1.1 Подраздел",
        "АО \"НТЦ ИТ РОСА\"",
        "ПРОГРАММНЫЙ КОМПЛЕКС"
    ]
    
    pattern = r'^\d+\.\s+[А-ЯA-Z]'
    
    for text in test_cases:
        match = bool(re.match(pattern, text))
        status = "✅ СООТВЕТСТВУЕТ" if match else "❌ НЕ СООТВЕТСТВУЕТ"
        print(f"{status}: '{text}'")
    print()

def test_extract_chapter_info():
    """Тестирует извлечение информации о главе"""
    
    print("=== Тест извлечения информации о главе ===")
    
    converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
    # Сбрасываем счетчик
    if hasattr(converter, '_chapter_counter'):
        del converter._chapter_counter
    
    test_headers = [
        "1. Общие сведения",
        "2. Архитектура комплекса",
        "3. Технические требования"
    ]
    
    for header in test_headers:
        info = converter._extract_chapter_info(header)
        print(f"Заголовок: '{header}'")
        print(f"  → Номер: {info['number']}")
        print(f"  → Название: '{info['title']}'")
        print(f"  → Полный заголовок: '{info['full_title']}'")
        print()

if __name__ == '__main__':
    test_regex_patterns()
    test_chapter_header_detection()
    test_extract_chapter_info()