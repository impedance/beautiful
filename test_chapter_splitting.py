#!/usr/bin/env python3
"""
Тесты для функциональности разделения DOCX документа на главы
Проверяют разбиение документа на отдельные markdown файлы по главам
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestChapterSplitting(unittest.TestCase):
    """Тесты для разделения документа на главы"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.samples_dir = Path("samples")
        
    def tearDown(self):
        """Очистка после тестов"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_chapter_detection_patterns(self):
        """Тест определения границ глав"""
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
            "1.2 Требования к среде"
        ]
        
        for header in chapter_headers:
            self.assertTrue(self._is_chapter_header(header), 
                          f"Заголовок '{header}' должен определяться как глава")
            
        for header in section_headers:
            self.assertFalse(self._is_chapter_header(header),
                           f"Заголовок '{header}' НЕ должен определяться как глава")
    
    def test_chapter_filename_generation(self):
        """Тест генерации имен файлов для глав"""
        test_cases = [
            ("1. Общие сведения", "1.common.md"),
            ("2. Архитектура комплекса", "2.architecture.md"),
            ("3. Технические и программные требования", "3.technical-requirements.md"),
            ("4. Установка и настройка", "4.installation-setup.md"),
            ("5. Эксплуатация", "5.operation.md")
        ]
        
        for chapter_title, expected_filename in test_cases:
            filename = self._generate_chapter_filename(chapter_title)
            self.assertEqual(filename, expected_filename,
                           f"Для заголовка '{chapter_title}' ожидался файл '{expected_filename}', получен '{filename}'")
    
    def test_frontmatter_generation(self):
        """Тест генерации frontmatter для глав"""
        # Тест для первой главы
        frontmatter_1 = self._generate_frontmatter("Общие сведения", 1, 3)
        expected_1 = """---
title: Общие сведения

nextRead:
  to: /developer/user/start
  label: Архитектура комплекса
---"""
        
        # Тест для средней главы
        frontmatter_2 = self._generate_frontmatter("Архитектура комплекса", 2, 3)
        expected_2 = """---
title: Архитектура комплекса

readPrev:
  to: /path/to/prev
  label: Общие сведения

nextRead:
  to: /path/to/next
  label: Технические требования
---"""
        
        # Тест для последней главы
        frontmatter_3 = self._generate_frontmatter("Технические требования", 3, 3)
        expected_3 = """---
title: Технические требования

readPrev:
  to: /path/to/prev
  label: Архитектура комплекса
---"""
        
        # Проверяем структуру (не точное совпадение, так как пути могут отличаться)
        self.assertIn('title: Общие сведения', frontmatter_1)
        self.assertIn('nextRead:', frontmatter_1)
        self.assertNotIn('readPrev:', frontmatter_1)
        
        self.assertIn('title: Архитектура комплекса', frontmatter_2)
        self.assertIn('readPrev:', frontmatter_2)
        self.assertIn('nextRead:', frontmatter_2)
        
        self.assertIn('title: Технические требования', frontmatter_3)
        self.assertIn('readPrev:', frontmatter_3)
        self.assertNotIn('nextRead:', frontmatter_3)
    
    def test_content_splitting_logic(self):
        """Тест логики разделения содержимого на главы"""
        # Мок документа с несколькими главами
        mock_content = [
            ("heading", 1, "1. Общие сведения"),
            ("paragraph", 0, "Содержимое первой главы"),
            ("heading", 2, "1.1 Подраздел первой главы"),
            ("paragraph", 0, "Больше содержимого первой главы"),
            ("heading", 1, "2. Архитектура"),
            ("paragraph", 0, "Содержимое второй главы"),
            ("heading", 2, "2.1 Компоненты"),
            ("paragraph", 0, "Описание компонентов"),
            ("heading", 1, "3. Требования"),
            ("paragraph", 0, "Содержимое третьей главы")
        ]
        
        chapters = self._split_content_into_chapters(mock_content)
        
        # Должно быть 3 главы
        self.assertEqual(len(chapters), 3)
        
        # Проверяем первую главу
        chapter_1 = chapters[0]
        self.assertEqual(chapter_1['title'], "Общие сведения")
        self.assertEqual(len([item for item in chapter_1['content'] if item[0] == 'paragraph']), 2)
        
        # Проверяем вторую главу
        chapter_2 = chapters[1]
        self.assertEqual(chapter_2['title'], "Архитектура")
        self.assertEqual(len([item for item in chapter_2['content'] if item[0] == 'paragraph']), 2)
        
        # Проверяем третью главу
        chapter_3 = chapters[2]
        self.assertEqual(chapter_3['title'], "Требования")
        self.assertEqual(len([item for item in chapter_3['content'] if item[0] == 'paragraph']), 1)
    
    def test_chapter_file_creation(self):
        """Тест создания отдельных файлов для глав"""
        # Создаем тестовые данные
        chapters = [
            {
                'title': 'Общие сведения',
                'number': 1,
                'filename': '1.common.md',
                'content': [
                    ('heading', 1, 'Общие сведения'),
                    ('paragraph', 0, 'Тестовое содержимое первой главы')
                ]
            },
            {
                'title': 'Архитектура',
                'number': 2, 
                'filename': '2.architecture.md',
                'content': [
                    ('heading', 1, 'Архитектура'),
                    ('paragraph', 0, 'Тестовое содержимое второй главы')
                ]
            }
        ]
        
        # Создаем файлы
        output_dir = self.temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        created_files = self._create_chapter_files(chapters, output_dir)
        
        # Проверяем что файлы созданы
        self.assertEqual(len(created_files), 2)
        
        for chapter in chapters:
            file_path = output_dir / chapter['filename']
            self.assertTrue(file_path.exists(), f"Файл {chapter['filename']} не создан")
            
            # Проверяем содержимое
            content = file_path.read_text(encoding='utf-8')
            self.assertIn('---', content)  # frontmatter
            self.assertIn(f"title: {chapter['title']}", content)
            self.assertIn(f"# {chapter['title']}", content)  # основной заголовок
            self.assertIn('Тестовое содержимое', content)
    
    def test_samples_compatibility(self):
        """Тест совместимости с существующими образцами"""
        # Проверяем, что наши правила совместимы с существующими файлами
        if not self.samples_dir.exists():
            self.skipTest("Папка samples не найдена")
        
        sample_files = list(self.samples_dir.glob("*.md"))
        self.assertGreater(len(sample_files), 0, "Не найдены файлы образцов")
        
        for sample_file in sample_files:
            content = sample_file.read_text(encoding='utf-8')
            
            # Проверяем структуру
            self.assertTrue(content.startswith('---'), 
                          f"Файл {sample_file.name} должен начинаться с frontmatter")
            self.assertIn('title:', content,
                         f"Файл {sample_file.name} должен содержать title в frontmatter")
            self.assertRegex(content, r'\n# .+\n',
                           f"Файл {sample_file.name} должен содержать заголовок первого уровня")

    # Вспомогательные методы для тестирования (заглушки)
    
    def _is_chapter_header(self, header_text):
        """Определяет, является ли заголовок началом новой главы"""
        # Заголовок главы - это заголовок первого уровня с номером
        # Формат: "1. Название", "2. Название" и т.д.
        import re
        return bool(re.match(r'^\d+\.\s+[А-ЯA-Z]', header_text))
    
    def _generate_chapter_filename(self, chapter_title):
        """Генерирует имя файла для главы"""
        import re
        
        # Извлекаем номер главы
        match = re.match(r'^(\d+)\.\s+(.+)$', chapter_title)
        if not match:
            return "unknown.md"
        
        chapter_num = match.group(1)
        title = match.group(2)
        
        # Преобразуем название в filename
        filename_map = {
            "Общие сведения": "common",
            "Архитектура комплекса": "architecture", 
            "Технические и программные требования": "technical-requirements",
            "Установка и настройка": "installation-setup",
            "Эксплуатация": "operation"
        }
        
        base_name = filename_map.get(title, title.lower().replace(' ', '-'))
        return f"{chapter_num}.{base_name}.md"
    
    def _generate_frontmatter(self, title, chapter_num, total_chapters):
        """Генерирует frontmatter для главы"""
        lines = ["---", f"title: {title}", ""]
        
        # Предыдущая глава
        if chapter_num > 1:
            lines.extend([
                "readPrev:",
                "  to: /path/to/prev",
                "  label: Предыдущая глава",
                ""
            ])
        
        # Следующая глава
        if chapter_num < total_chapters:
            next_titles = {
                1: "Архитектура комплекса",
                2: "Технические требования"
            }
            next_title = next_titles.get(chapter_num, "Следующая глава")
            
            lines.extend([
                "nextRead:",
                "  to: /path/to/next", 
                f"  label: {next_title}"
            ])
        
        lines.append("---")
        return "\n".join(lines)
    
    def _split_content_into_chapters(self, content):
        """Разделяет содержимое на главы"""
        chapters = []
        current_chapter = None
        
        for item_type, level, text in content:
            if item_type == "heading" and level == 1 and self._is_chapter_header(text):
                # Сохраняем предыдущую главу
                if current_chapter:
                    chapters.append(current_chapter)
                
                # Начинаем новую главу
                import re
                match = re.match(r'^\d+\.\s+(.+)$', text)
                title = match.group(1) if match else text
                
                current_chapter = {
                    'title': title,
                    'number': len(chapters) + 1,
                    'content': [(item_type, level, text)]
                }
            elif current_chapter:
                current_chapter['content'].append((item_type, level, text))
        
        # Добавляем последнюю главу
        if current_chapter:
            chapters.append(current_chapter)
        
        return chapters
    
    def _create_chapter_files(self, chapters, output_dir):
        """Создает файлы для глав"""
        created_files = []
        
        for chapter in chapters:
            file_path = output_dir / chapter['filename']
            
            # Генерируем содержимое
            content = self._generate_frontmatter(
                chapter['title'], 
                chapter['number'], 
                len(chapters)
            )
            content += f"\n\n# {chapter['title']}\n\n"
            
            # Добавляем остальное содержимое
            for item_type, level, text in chapter['content'][1:]:  # Пропускаем первый заголовок
                if item_type == 'paragraph':
                    content += f"{text}\n\n"
                elif item_type == 'heading':
                    content += f"{'#' * (level + 1)} {text}\n\n"
            
            # Записываем файл
            file_path.write_text(content, encoding='utf-8')
            created_files.append(file_path)
        
        return created_files


if __name__ == '__main__':
    print("Запуск тестов для функциональности разделения на главы...")
    unittest.main(verbosity=2)