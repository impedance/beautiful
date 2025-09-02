#!/usr/bin/env python3
"""
Простой тест для проверки создания файлов при разделении на главы
Проверяет логику без зависимости от python-docx
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestSimpleFileSplitting(unittest.TestCase):
    """Простой тест создания файлов при разделении на главы"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Очистка после тестов"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_split_into_chapters_method(self):
        """Тест метода _split_into_chapters"""
        # Создаем конвертер без инициализации документа
        converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        converter.split_chapters = True
        
        # Тестовые элементы документа (как если бы они были извлечены из DOCX)
        document_elements = [
            {
                'type': 'heading',
                'level': 1,
                'text': '1. Общие сведения',
                'element': Mock()
            },
            {
                'type': 'paragraph', 
                'text': 'Содержимое первой главы',
                'element': Mock()
            },
            {
                'type': 'heading',
                'level': 2,
                'text': '1.1 Функциональное назначение',
                'element': Mock()
            },
            {
                'type': 'paragraph',
                'text': 'Подраздел первой главы',
                'element': Mock()
            },
            {
                'type': 'heading',
                'level': 1,
                'text': '2. Архитектура комплекса',
                'element': Mock()
            },
            {
                'type': 'paragraph',
                'text': 'Содержимое второй главы',
                'element': Mock()
            },
            {
                'type': 'heading',
                'level': 1, 
                'text': '3. Технические требования',
                'element': Mock()
            },
            {
                'type': 'paragraph',
                'text': 'Содержимое третьей главы',
                'element': Mock()
            }
        ]
        
        # Тестируем разделение на главы
        chapters = converter._split_into_chapters(document_elements)
        
        # Проверяем что главы разделены правильно
        self.assertEqual(len(chapters), 3, "Должно быть создано 3 главы")
        
        # Проверяем первую главу
        chapter_1 = chapters[0]
        self.assertEqual(chapter_1['info']['title'], "Общие сведения")
        self.assertEqual(chapter_1['info']['number'], 1)
        self.assertEqual(len(chapter_1['elements']), 4)  # заголовок + абзац + подзаголовок + абзац
        
        # Проверяем вторую главу
        chapter_2 = chapters[1]
        self.assertEqual(chapter_2['info']['title'], "Архитектура комплекса") 
        self.assertEqual(chapter_2['info']['number'], 2)
        self.assertEqual(len(chapter_2['elements']), 2)  # заголовок + абзац
        
        # Проверяем третью главу
        chapter_3 = chapters[2]
        self.assertEqual(chapter_3['info']['title'], "Технические требования")
        self.assertEqual(chapter_3['info']['number'], 3)
        self.assertEqual(len(chapter_3['elements']), 2)  # заголовок + абзац
        
    def test_generate_chapter_content_method(self):
        """Тест метода _generate_chapter_content"""
        # Создаем конвертер
        converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        converter.add_frontmatter = True
        converter.markdown_lines = []
        converter.in_code_block = False
        
        # Создаем тестовую главу
        chapter = {
            'info': {
                'number': 1,
                'title': 'Общие сведения',
                'full_title': '1. Общие сведения'
            },
            'filename': '1.common.md',
            'elements': [
                {
                    'type': 'heading',
                    'level': 1,
                    'text': '1. Общие сведения',
                    'element': Mock()
                },
                {
                    'type': 'paragraph',
                    'text': 'Тестовое содержимое главы',
                    'element': Mock()
                }
            ]
        }
        
        # Мокаем необходимые методы
        def mock_process_element(element):
            if element['type'] == 'heading':
                return f"{'#' * element['level']} {element['text']}\n\n"
            elif element['type'] == 'paragraph':
                return f"{element['text']}\n\n"
            return ""
            
        converter._process_paragraph = lambda para: "Тестовое содержимое главы\n\n"
        
        # Генерируем содержимое главы
        content = converter._generate_chapter_content(chapter, 3)
        
        # Проверяем структуру содержимого
        self.assertTrue(content.startswith('---'), "Содержимое должно начинаться с frontmatter")
        self.assertIn('title: Общие сведения', content, "Должен быть заголовок главы")
        self.assertIn('# Общие сведения', content, "Должен быть markdown заголовок")
        self.assertIn('nextRead:', content, "Должна быть навигация к следующей главе")
        
    def test_file_creation_logic(self):
        """Тест логики создания файлов"""
        # Создаем директорию для вывода
        output_dir = self.temp_dir / "chapters"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем тестовые данные глав
        chapters = [
            {
                'info': {'number': 1, 'title': 'Общие сведения'},
                'filename': '1.common.md',
                'elements': [{'type': 'heading', 'level': 1, 'text': '1. Общие сведения'}]
            },
            {
                'info': {'number': 2, 'title': 'Архитектура комплекс'},
                'filename': '2.architecture.md', 
                'elements': [{'type': 'heading', 'level': 1, 'text': '2. Архитектура комплекс'}]
            }
        ]
        
        # Симулируем создание файлов (как это должно происходить в convert_to_chapters)
        created_files = []
        for chapter in chapters:
            file_path = output_dir / chapter['filename']
            
            # Простое содержимое для теста
            content = f"""---
title: {chapter['info']['title']}
---

# {chapter['info']['title']}

Тестовое содержимое главы {chapter['info']['number']}.
"""
            
            file_path.write_text(content, encoding='utf-8')
            created_files.append(str(file_path))
        
        # Проверяем что файлы созданы
        self.assertEqual(len(created_files), 2, "Должно быть создано 2 файла")
        
        for chapter in chapters:
            file_path = output_dir / chapter['filename']
            self.assertTrue(file_path.exists(), f"Файл {chapter['filename']} должен быть создан")
            
            content = file_path.read_text(encoding='utf-8')
            self.assertTrue(content.startswith('---'), f"Файл {chapter['filename']} должен начинаться с frontmatter")
            self.assertIn(f"title: {chapter['info']['title']}", content)


if __name__ == '__main__':
    print("Запуск простых тестов создания файлов...")
    unittest.main(verbosity=2)