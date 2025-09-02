#!/usr/bin/env python3
"""
Финальный интеграционный тест для проверки исправления разделения на главы
"""

import unittest
import tempfile
import shutil
from pathlib import Path


class TestFinalIntegration(unittest.TestCase):
    """Финальный тест исправления функциональности разделения на главы"""
    
    def test_chapter_splitting_with_docx_format(self):
        """Тест разделения на главы с форматом заголовков из DOCX"""
        
        from improved_docx_converter import ImprovedDocxToMarkdownConverter
        
        # Создаем временную директорию
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # Создаем конвертер без документа для тестирования методов
            converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
            converter.split_chapters = True
            
            # Реальные заголовки из DOCX файла (с табами и номерами страниц)
            real_document_elements = [
                {
                    'type': 'heading',
                    'level': 1,
                    'text': '1    Общие сведения	5',  # содержит табы и номер страницы
                    'element': None
                },
                {
                    'type': 'paragraph',
                    'text': 'Содержимое первой главы...',
                    'element': None
                },
                {
                    'type': 'heading',
                    'level': 2,
                    'text': '1.1    Назначение',
                    'element': None
                },
                {
                    'type': 'heading',
                    'level': 1,
                    'text': '2    Архитектура комплекса	6',
                    'element': None
                },
                {
                    'type': 'paragraph',
                    'text': 'Содержимое второй главы...',
                    'element': None
                },
                {
                    'type': 'heading',
                    'level': 1,
                    'text': '3    Технические и программные требования	10',
                    'element': None
                },
                {
                    'type': 'paragraph',
                    'text': 'Содержимое третьей главы...',
                    'element': None
                }
            ]
            
            # Тестируем разделение на главы
            chapters = converter._split_into_chapters(real_document_elements)
            
            # Проверяем что главы найдены
            self.assertEqual(len(chapters), 3, "Должно быть найдено 3 главы")
            
            # Проверяем первую главу
            chapter_1 = chapters[0]
            self.assertEqual(chapter_1['info']['number'], 1)
            self.assertEqual(chapter_1['info']['title'], "Общие сведения")
            self.assertEqual(chapter_1['filename'], "1.common.md")
            
            # Проверяем вторую главу
            chapter_2 = chapters[1]
            self.assertEqual(chapter_2['info']['number'], 2)
            self.assertEqual(chapter_2['info']['title'], "Архитектура комплекса")
            self.assertEqual(chapter_2['filename'], "2.architecture.md")
            
            # Проверяем третью главу
            chapter_3 = chapters[2]
            self.assertEqual(chapter_3['info']['number'], 3)
            self.assertEqual(chapter_3['info']['title'], "Технические и программные требования")
            self.assertEqual(chapter_3['filename'], "3.technical-requirements.md")
            
            print(f"✅ Успешно найдено {len(chapters)} глав:")
            for i, chapter in enumerate(chapters, 1):
                print(f"  {i}. {chapter['info']['title']} -> {chapter['filename']}")
            
        finally:
            # Очищаем временную директорию
            shutil.rmtree(temp_dir)
    
    def test_regex_patterns_with_real_content(self):
        """Тест regex паттернов с реальным содержимым"""
        
        from improved_docx_converter import ImprovedDocxToMarkdownConverter
        
        converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        
        # Тестовые случаи с реальными заголовками
        test_cases = [
            # Должны быть главами
            ("1    Общие сведения	5", True),
            ("2    Архитектура комплекса	6", True),
            ("3    Технические и программные требования	10", True),
            ("7    Управление контентом через Winter CMS	41", True),
            
            # НЕ должны быть главами
            ("1.1    Назначение", False),
            ("2.1    Основные компоненты", False),
            ("АО \"НТЦ ИТ РОСА\"", False),
            ("ПРОГРАММНЫЙ КОМПЛЕКС", False),
            ("АННОТАЦИЯ", False),
        ]
        
        for text, expected_is_chapter in test_cases:
            actual_is_chapter = converter._is_chapter_header(text)
            self.assertEqual(actual_is_chapter, expected_is_chapter,
                           f"Заголовок '{text}' - ожидался {'ГЛАВА' if expected_is_chapter else 'НЕ ГЛАВА'}, получился {'ГЛАВА' if actual_is_chapter else 'НЕ ГЛАВА'}")


if __name__ == '__main__':
    print("Запуск финального интеграционного теста...")
    unittest.main(verbosity=2)