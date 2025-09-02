#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексные тесты для проверки всех правил форматирования DOCX to Markdown конвертера
Основаны на анализе кода конвертера и требований к форматированию
"""

import re
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

# Добавляем путь к конвертеру
sys.path.insert(0, str(Path(__file__).parent))

try:
    from improved_docx_converter import ImprovedDocxToMarkdownConverter
except ImportError:
    print("Не удалось импортировать конвертер")
    sys.exit(1)


class TestFormattingRules(unittest.TestCase):
    """Тестирование правил форматирования"""
    
    def setUp(self):
        """Настройка для тестов"""
        # Создаем мок-документ для инициализации конвертера
        mock_doc = Mock()
        mock_doc.styles = []
        mock_doc.element.body = []
        
        # Создаем конвертер с мок-документом
        self.converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        self.converter.doc = mock_doc
        self.converter.markdown_lines = []
        self.converter.in_code_block = False
        self.converter.add_frontmatter = False
        self.converter.split_chapters = False
        self.converter.heading_map = {}
        self.converter.skip_next_paragraph = False
        self.converter.chapters = []
        self.converter.current_chapter = None

    def test_frontmatter_generation(self):
        """Тест генерации frontmatter согласно правилам форматирования"""
        self.converter.add_frontmatter = True
        self.converter._add_frontmatter()
        
        frontmatter_text = '\n'.join(self.converter.markdown_lines)
        
        # Проверяем структуру YAML frontmatter
        self.assertTrue(frontmatter_text.startswith("---"))
        self.assertIn("title:", frontmatter_text)
        self.assertIn("nextRead:", frontmatter_text)
        self.assertIn("  to:", frontmatter_text)
        self.assertIn("  label:", frontmatter_text)
        self.assertTrue(frontmatter_text.strip().endswith("---"))

    def test_heading_formatting_rules(self):
        """Тест правил форматирования заголовков"""
        # Тест H1 без номера
        result = self.converter._format_heading("Общие сведения", 1)
        self.assertEqual(result, "# Общие сведения")
        
        # Тест H2 с нумерацией X.Y
        result = self.converter._format_heading("1.1 Функциональное назначение", 2)
        self.assertEqual(result, "## 1.1 Функциональное назначение")
        
        # Тест очистки номеров страниц из заголовков
        result = self.converter._format_heading("2.2 Состав плагинов\t\t15", 2)
        self.assertEqual(result, "## 2.2 Состав плагинов")

    def test_app_annotation_block_formatting(self):
        """Тест форматирования блока AppAnnotation"""
        text = "Ключевые моменты раздела для понимания архитектуры системы"
        result = self.converter._format_app_annotation(text)
        
        expected = """::AppAnnotation
Ключевые моменты раздела для понимания архитектуры системы
::"""
        self.assertEqual(result, expected)

    def test_list_formatting_rules(self):
        """Тест правил форматирования списков"""
        # Маркированные списки с правильной пунктуацией
        list_items = [
            "обеспечение разработчиков каталогом документации;",
            "предоставление API для интеграции;", 
            "поддержка многоязычности."
        ]
        
        result = self.converter._format_list(list_items)
        lines = result.split('\n')
        
        # Проверяем структуру списка
        for i, line in enumerate(lines):
            self.assertTrue(line.startswith("- "))
            if i < len(lines) - 1:
                self.assertTrue(line.endswith(";"))
            else:
                self.assertTrue(line.endswith("."))

    def test_component_list_formatting(self):
        """Тест форматирования описательных списков компонентов"""
        components = [
            ("Компонент1", "описание первого компонента;"),
            ("Компонент2", "описание второго компонента;"),
            ("Компонент3", "описание третьего компонента.")
        ]
        
        result = self.converter._format_component_list(components)
        lines = result.split('\n')
        
        for line in lines:
            self.assertTrue(re.match(r'^- `[^`]+` — [^;]+[;.]$', line))

    def test_table_formatting_with_captions(self):
        """Тест форматирования таблиц с подписями"""
        headers = ["Заголовок 1", "Заголовок 2", "Заголовок 3"]
        rows = [
            ["Данные 1.1", "Данные 1.2", "Данные 1.3"],
            ["Данные 2.1", "Данные 2.2", "Данные 2.3"]
        ]
        caption = "Таблица 1 – Описание таблицы"
        
        result = self.converter._format_table_with_caption(headers, rows, caption)
        lines = result.split('\n')
        
        # Проверяем структуру таблицы
        self.assertTrue(lines[0].startswith('|') and lines[0].endswith('|'))
        self.assertIn('---', lines[1])
        self.assertTrue(all(line.startswith('|') and line.endswith('|') 
                           for line in lines[2:4]))
        
        # Проверяем подпись к таблице
        self.assertTrue(any(line.startswith(f"> {caption}") for line in lines))

    def test_line_breaks_in_table_cells(self):
        """Тест переносов строк в ячейках таблиц"""
        cell_content = "Строка 1\nСтрока 2\nСтрока 3"
        result = self.converter._clean_cell_text(Mock(text=cell_content))
        
        expected = "Строка 1<br>Строка 2<br>Строка 3"
        self.assertEqual(result, expected)

    def test_blockquote_notes_formatting(self):
        """Тест форматирования примечаний в blockquote"""
        note_text = "Примечание – Текст важного примечания к разделу."
        result = self.converter._format_note(note_text)
        
        expected = "> _Примечание_ – Текст важного примечания к разделу."
        self.assertEqual(result, expected)

    def test_inline_code_formatting(self):
        """Тест форматирования inline кода и технических терминов"""
        # Названия ПО в обратных кавычках
        software_names = ["Winter CMS", "PostgreSQL", "Docker", "Ubuntu"]
        
        for name in software_names:
            result = self.converter._format_software_name(name)
            self.assertEqual(result, f"`{name}`")
            
        # Аббревиатуры без кавычек
        abbreviations = ["HTML5", "CSS3", "JavaScript", "REST API"]
        
        for abbr in abbreviations:
            result = self.converter._format_abbreviation(abbr)
            self.assertEqual(result, abbr)

    def test_internal_links_formatting(self):
        """Тест форматирования внутренних ссылок"""
        link_text = "разделе 7"
        link_path = "/developer/administrator/winter-cms"
        
        result = self.converter._format_internal_link(link_text, link_path)
        expected = f"[{link_text}]({link_path})"
        
        self.assertEqual(result, expected)
        self.assertTrue(re.match(r'\[[^\]]+\]\([^)]+\)', result))

    def test_section_numbering_validation(self):
        """Тест проверки правильности нумерации разделов"""
        valid_numbers = ["1.1", "1.2", "2.1", "2.9", "3.1", "10.15"]
        invalid_numbers = ["1", "1.1.1", "a.1", "1.a"]
        
        for number in valid_numbers:
            self.assertTrue(self.converter._is_valid_section_number(number))
            
        for number in invalid_numbers:
            self.assertFalse(self.converter._is_valid_section_number(number))

    def test_punctuation_in_lists_validation(self):
        """Тест правильности пунктуации в списках"""
        list_items = [
            "- первый элемент;",
            "- второй элемент;", 
            "- третий элемент;",
            "- последний элемент."
        ]
        
        result = self.converter._validate_list_punctuation(list_items)
        self.assertTrue(result["is_valid"])
        
        # Проверяем неправильную пунктуацию
        incorrect_items = [
            "- первый элемент.",
            "- второй элемент;",
            "- последний элемент;"
        ]
        
        result = self.converter._validate_list_punctuation(incorrect_items)
        self.assertFalse(result["is_valid"])

    def test_image_block_formatting(self):
        """Тест форматирования блоков изображений"""
        src = "/images/architecture-diagram.png"
        caption = "Диаграмма архитектуры системы"
        
        result = self.converter._format_image_block(src, caption)
        
        expected = f"""::sign-image
src: {src}
sign: {caption}
::"""
        self.assertEqual(result, expected)

    def test_code_block_language_detection(self):
        """Тест определения языков в блоках кода"""
        test_cases = [
            ("sudo systemctl start docker", "bash"),
            ("SELECT * FROM users WHERE active = true;", "sql"),
            ("version: '3.8'\nservices:", "yaml"),
            ("def process_data(items):", "python"),
            ("[database]\nhost = localhost", "ini"),
            ("#!/bin/bash\necho 'Hello'", "bash"),
        ]
        
        for code_text, expected_lang in test_cases:
            result = self.converter._detect_code_language(code_text)
            self.assertEqual(result, expected_lang)

    def test_heading_level_detection(self):
        """Тест определения уровней заголовков"""
        # Создаем мок-параграф для тестирования
        def create_mock_paragraph(text, style_name=None, font_size=None, is_bold=False):
            para = Mock()
            para.text = text
            para.style = Mock()
            para.style.name = style_name
            para.runs = [Mock()]
            para.runs[0].bold = is_bold
            para.runs[0].font.size = Mock()
            para.runs[0].font.size.pt = font_size if font_size else 12
            para._element = Mock()
            para._element.xpath = Mock(return_value=[])
            return para
        
        # Тест определения по стилю
        para1 = create_mock_paragraph("Заголовок", "Heading 1")
        self.converter.heading_map = {"Heading 1": 1}
        result = self.converter._is_heading(para1)
        self.assertEqual(result, 1)
        
        # Тест определения по размеру шрифта и жирности
        para2 = create_mock_paragraph("Заголовок", font_size=18, is_bold=True)
        result = self.converter._is_heading(para2)
        self.assertIsNotNone(result)
        
        # Тест определения по паттерну нумерации
        para3 = create_mock_paragraph("1.1 Функциональное назначение")
        result = self.converter._is_heading(para3)
        self.assertEqual(result, 2)

    def test_list_item_detection_and_processing(self):
        """Тест определения и обработки элементов списков"""
        def create_mock_list_paragraph(text, style_name=None):
            para = Mock()
            para.text = text
            para.style = Mock()
            para.style.name = style_name
            para.paragraph_format = Mock()
            para.paragraph_format.left_indent = Mock()
            para.paragraph_format.left_indent.pt = 0
            return para
        
        # Маркированный список
        para1 = create_mock_list_paragraph("- Элемент списка")
        self.assertTrue(self.converter._is_list_item(para1))
        
        # Нумерованный список
        para2 = create_mock_list_paragraph("1) Элемент списка")
        self.assertTrue(self.converter._is_list_item(para2))
        
        # Буквенный список
        para3 = create_mock_list_paragraph("а) Элемент списка")
        self.assertTrue(self.converter._is_list_item(para3))

    def test_code_block_detection(self):
        """Тест определения блоков кода"""
        def create_mock_code_paragraph(text, style_name=None, font_name=None):
            para = Mock()
            para.text = text
            para.style = Mock()
            para.style.name = style_name
            para.runs = [Mock()]
            para.runs[0].font.name = font_name
            para.runs[0].text = text
            return para
        
        # По стилю
        para1 = create_mock_code_paragraph("code example", "Code")
        self.assertTrue(self.converter._is_code_block(para1))
        
        # По шрифту
        para2 = create_mock_code_paragraph("code example", font_name="Courier New")
        self.assertTrue(self.converter._is_code_block(para2))
        
        # По содержимому
        para3 = create_mock_code_paragraph("sudo apt update")
        self.assertTrue(self.converter._is_code_block(para3))


class TestChapterSplitting(unittest.TestCase):
    """Тестирование разделения документа на главы"""
    
    def setUp(self):
        # Аналогичная настройка как в TestFormattingRules
        mock_doc = Mock()
        mock_doc.styles = []
        mock_doc.element.body = []
        
        self.converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        self.converter.doc = mock_doc
        self.converter.markdown_lines = []
        self.converter.in_code_block = False
        self.converter.add_frontmatter = False
        self.converter.split_chapters = True
        self.converter.heading_map = {}
        self.converter.skip_next_paragraph = False
        self.converter.chapters = []
        self.converter.current_chapter = None

    def test_chapter_header_detection(self):
        """Тест определения заголовков глав"""
        # Правильные заголовки глав
        valid_headers = [
            "1. Общие сведения",
            "2. Архитектура комплекса", 
            "Установка и настройка"
        ]
        
        for header in valid_headers:
            self.assertTrue(self.converter._is_chapter_header(header))
        
        # Неправильные заголовки (служебная информация)
        invalid_headers = [
            'АО "НТЦ ИТ РОСА"',
            "ПРОГРАММНЫЙ КОМПЛЕКС",
            "Версия 2.0",
            "АННОТАЦИЯ"
        ]
        
        for header in invalid_headers:
            self.assertFalse(self.converter._is_chapter_header(header))

    def test_chapter_info_extraction(self):
        """Тест извлечения информации о главе"""
        # Формат "1. Название"
        result = self.converter._extract_chapter_info("1. Общие сведения")
        self.assertEqual(result['number'], 1)
        self.assertEqual(result['title'], "Общие сведения")
        
        # Формат "2    Архитектура"
        result = self.converter._extract_chapter_info("2\t\tАрхитектура комплекса")
        self.assertEqual(result['number'], 2)
        self.assertEqual(result['title'], "Архитектура комплекса")
        
        # Без номера
        result = self.converter._extract_chapter_info("Установка и настройка")
        self.assertIsNotNone(result['number'])
        self.assertEqual(result['title'], "Установка и настройка")

    def test_chapter_filename_generation(self):
        """Тест генерации имен файлов для глав"""
        test_cases = [
            ({"number": 1, "title": "Общие сведения"}, "1.common.md"),
            ({"number": 2, "title": "Архитектура комплекса"}, "2.architecture.md"),
            ({"number": 3, "title": "Установка и настройка"}, "3.installation-setup.md")
        ]
        
        for chapter_info, expected in test_cases:
            result = self.converter._generate_chapter_filename(chapter_info)
            self.assertEqual(result, expected)

    def test_chapter_frontmatter_generation(self):
        """Тест генерации frontmatter для глав"""
        chapter_info = {"number": 2, "title": "Архитектура"}
        result = self.converter._generate_chapter_frontmatter(chapter_info, 5)
        
        self.assertIn("title: Архитектура", result)
        self.assertIn("readPrev:", result)
        self.assertIn("nextRead:", result)


if __name__ == "__main__":
    # Запускаем тесты
    unittest.main(verbosity=2)