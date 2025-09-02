#!/usr/bin/env python3
"""
Интеграционный тест для проверки методов конвертера
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestConverterIntegration(unittest.TestCase):
    """Тесты для интеграции методов конвертера"""
    
    def setUp(self):
        """Подготовка к тестам"""
        # Создаем мок-объект документа для тестирования
        self.mock_doc = Mock()
        
        # Создаем конвертер с мок-объектом
        self.converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        self.converter.doc = self.mock_doc
        self.converter.add_frontmatter = False
        self.converter.split_chapters = False
        
    def test_is_chapter_header_integration(self):
        """Тест метода _is_chapter_header из конвертера"""
        # Тестовые заголовки, которые должны определяться как начало новой главы
        chapter_headers = [
            "1. Общие сведения",
            "2. Архитектура комплекса", 
            "3. Технические требования",
            "4. Установка и настройка",
            "5. Эксплуатация системы"
        ]
        
        # Эти заголовки НЕ должны начинать новую главу
        section_headers = [
            "1.1 Функциональное назначение",
            "2.1 Основные компоненты",
            "3.1 Требования к ПО",
            "1.2 Требования к среде",
            "короткий",  # слишком короткий
            "АО \"НТЦ ИТ РОСА\"",  # исключенный паттерн
            "ПРОГРАММНЫЙ КОМПЛЕКС",  # исключенный паттерн
        ]
        
        for header in chapter_headers:
            result = self.converter._is_chapter_header(header)
            self.assertTrue(result, f"Заголовок '{header}' должен определяться как глава")
            
        for header in section_headers:
            result = self.converter._is_chapter_header(header)
            self.assertFalse(result, f"Заголовок '{header}' НЕ должен определяться как глава")
    
    def test_extract_chapter_info_integration(self):
        """Тест метода _extract_chapter_info из конвертера"""
        # Сбрасываем счетчик глав
        if hasattr(self.converter, '_chapter_counter'):
            del self.converter._chapter_counter
            
        test_cases = [
            ("1. Общие сведения", {"number": 1, "title": "Общие сведения"}),
            ("2. Архитектура комплекса", {"number": 2, "title": "Архитектура комплекса"}),
            ("3    Технические требования", {"number": 3, "title": "Технические требования"}),  # без точки
        ]
        
        for input_text, expected in test_cases:
            result = self.converter._extract_chapter_info(input_text)
            self.assertEqual(result['number'], expected['number'], 
                           f"Неверный номер для '{input_text}': ожидался {expected['number']}, получен {result['number']}")
            self.assertEqual(result['title'], expected['title'],
                           f"Неверный заголовок для '{input_text}': ожидался '{expected['title']}', получен '{result['title']}'")
    
    def test_generate_chapter_filename_integration(self):
        """Тест метода _generate_chapter_filename из конвертера"""
        test_cases = [
            ({"number": 1, "title": "Общие сведения"}, "1.common.md"),
            ({"number": 2, "title": "Архитектура комплекса"}, "2.architecture.md"),
            ({"number": 3, "title": "Технические и программные требования"}, "3.technical-requirements.md"),
            ({"number": 4, "title": "Установка и настройка"}, "4.installation-setup.md"),
        ]
        
        for chapter_info, expected_filename in test_cases:
            filename = self.converter._generate_chapter_filename(chapter_info)
            self.assertEqual(filename, expected_filename,
                           f"Для главы '{chapter_info['title']}' ожидался файл '{expected_filename}', получен '{filename}'")
    
    def test_generate_chapter_frontmatter_integration(self):
        """Тест метода _generate_chapter_frontmatter из конвертера"""
        # Тест для первой главы
        chapter_info_1 = {"number": 1, "title": "Общие сведения"}
        frontmatter_1 = self.converter._generate_chapter_frontmatter(chapter_info_1, 3)
        
        self.assertIn('title: Общие сведения', frontmatter_1)
        self.assertIn('nextRead:', frontmatter_1)
        self.assertNotIn('readPrev:', frontmatter_1)
        
        # Тест для средней главы
        chapter_info_2 = {"number": 2, "title": "Архитектура комплекса"}
        frontmatter_2 = self.converter._generate_chapter_frontmatter(chapter_info_2, 3)
        
        self.assertIn('title: Архитектура комплекса', frontmatter_2)
        self.assertIn('readPrev:', frontmatter_2)
        self.assertIn('nextRead:', frontmatter_2)
        
        # Тест для последней главы
        chapter_info_3 = {"number": 3, "title": "Технические требования"}
        frontmatter_3 = self.converter._generate_chapter_frontmatter(chapter_info_3, 3)
        
        self.assertIn('title: Технические требования', frontmatter_3)
        self.assertIn('readPrev:', frontmatter_3)
        self.assertNotIn('nextRead:', frontmatter_3)


if __name__ == '__main__':
    print("Запуск интеграционных тестов для конвертера...")
    unittest.main(verbosity=2)