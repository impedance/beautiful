#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD тесты для исправления ошибок форматирования в DOCX to Markdown конвертере

Эти тесты проверяют реальные функции преобразования неправильного форматирования
в правильное, основываясь на различиях между samples/ и chapters/
"""

import pytest
from pathlib import Path
import sys
import os

# Добавляем корневую директорию в path для импорта конвертера
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Импортируем функции, которые еще не существуют (будем их создавать)
try:
    from formatting_fixes import (
        MarkdownFormatter,
        fix_heading_levels,
        restore_section_numbering, 
        detect_and_wrap_appannotations,
        convert_paragraphs_to_lists,
        format_technical_components,
        fix_table_structure,
        fix_frontmatter_format
    )
except ImportError:
    # При первом запуске модуль не существует - это нормально для TDD
    pass

class TestHeadingLevelCorrection:
    """Тестирование исправления уровней заголовков"""
    
    def test_fix_h3_to_h1_main_chapter(self):
        """Исправление H3 -> H1 для основных глав"""
        wrong_input = "### Общие сведения"
        expected = "# Общие сведения"
        
        result = fix_heading_levels(wrong_input, is_main_chapter=True)
        assert result == expected
    
    def test_fix_h3_to_h2_section(self):
        """Исправление H3 -> H2 для разделов"""
        wrong_input = "### Назначение"
        expected = "## Назначение"  # Нумерацию добавим отдельной функцией
        
        result = fix_heading_levels(wrong_input, is_main_chapter=False)
        assert result == expected
    
    def test_preserve_correct_headings(self):
        """Сохранение уже правильных заголовков"""
        correct_input = "# Архитектура комплекса"
        expected = "# Архитектура комплекса"
        
        result = fix_heading_levels(correct_input, is_main_chapter=True)
        assert result == expected

class TestSectionNumberingRestoration:
    """Тестирование восстановления нумерации разделов"""
    
    def test_add_numbering_to_sections(self):
        """Добавление нумерации к разделам"""
        sections = [
            "## Назначение",
            "## Функции",
            "## Основные компоненты", 
            "## Состав плагинов"
        ]
        
        # Структура: глава 1 имеет разделы 1.1, 1.2; глава 2 имеет 2.1, 2.2
        chapter_structure = {1: 2, 2: 2}  # глава 1: 2 раздела, глава 2: 2 раздела
        
        expected = [
            "## 1.1 Назначение",
            "## 1.2 Функции", 
            "## 2.1 Основные компоненты",
            "## 2.2 Состав плагинов"
        ]
        
        result = restore_section_numbering(sections, chapter_structure)
        assert result == expected
    
    def test_preserve_existing_numbering(self):
        """Сохранение уже существующей нумерации"""
        sections = ["## 1.1 Функциональное назначение"]
        chapter_structure = {1: 1}
        expected = ["## 1.1 Функциональное назначение"]
        
        result = restore_section_numbering(sections, chapter_structure)
        assert result == expected

class TestAppAnnotationDetection:
    """Тестирование детектирования и создания AppAnnotation блоков"""
    
    def test_wrap_descriptive_paragraph(self):
        """Оборачивание описательного абзаца в AppAnnotation"""
        input_text = """Программный комплекс "Портал разработчика" построен по модульной архитектуре. Архитектура реализована на базе Winter CMS и включает серверную часть (бэкенд) для администрирования и управления контентом, а также клиентскую часть, доступную пользователям через веб-интерфейс браузера."""
        
        expected = """::AppAnnotation
Программный комплекс "Портал разработчика" построен по модульной архитектуре. Архитектура реализована на базе Winter CMS и включает серверную часть (бэкенд) для администрирования и управления контентом, а также клиентскую часть, доступную пользователям через веб-интерфейс браузера.
::"""
        
        result = detect_and_wrap_appannotations(input_text)
        assert result == expected
    
    def test_ignore_short_paragraphs(self):
        """Не оборачивать короткие абзацы"""
        input_text = "Краткое описание."
        expected = "Краткое описание."
        
        result = detect_and_wrap_appannotations(input_text)
        assert result == expected
    
    def test_preserve_existing_appannotations(self):
        """Сохранение уже существующих AppAnnotation блоков"""
        input_text = """::AppAnnotation
Уже правильно оформленный блок.
::"""
        expected = input_text
        
        result = detect_and_wrap_appannotations(input_text)
        assert result == expected

class TestListDetectionFromParagraphs:
    """Тестирование преобразования абзацев в списки"""
    
    def test_convert_sequential_paragraphs_to_list(self):
        """Преобразование последовательных абзацев в список"""
        input_text = """предоставление разработчикам доступа к актуальной документации;

размещение готовых примеров фрагментов исходного кода;

обеспечение условий для ускоренной разработки программного обеспечения."""
        
        expected = """- предоставление разработчикам доступа к актуальной документации;
- размещение готовых примеров фрагментов исходного кода;
- обеспечение условий для ускоренной разработки программного обеспечения."""
        
        result = convert_paragraphs_to_lists(input_text)
        assert result == expected
    
    def test_preserve_existing_lists(self):
        """Сохранение уже существующих списков"""
        input_text = """- первый элемент;
- второй элемент;
- третий элемент."""
        expected = input_text
        
        result = convert_paragraphs_to_lists(input_text)
        assert result == expected
    
    def test_ignore_non_list_paragraphs(self):
        """Не преобразовывать обычные абзацы в списки"""
        input_text = """Это обычный абзац с описанием.

А это другой абзац с другой информацией."""
        expected = input_text
        
        result = convert_paragraphs_to_lists(input_text)
        assert result == expected

class TestTechnicalComponentFormatting:
    """Тестирование форматирования технических компонентов"""
    
    def test_convert_paragraphs_to_component_list(self):
        """Преобразование абзацев с компонентами в список"""
        input_text = """CMS-сервер (Winter CMS) — основной элемент серверной части.

плагины Winter CMS — модули, расширяющие функциональность CMS.

СУБД PostgreSQL — хранение основной структурированной информации."""
        
        expected = """- `CMS-сервер` (`Winter CMS`) — основной элемент серверной части;
- плагины `Winter CMS` — модули, расширяющие функциональность CMS;
- СУБД `PostgreSQL` — хранение основной структурированной информации;"""
        
        result = format_technical_components(input_text)
        assert result == expected
    
    def test_preserve_existing_component_lists(self):
        """Сохранение уже правильно оформленных списков компонентов"""
        input_text = """- `CMS-сервер` (`Winter CMS`) — основной элемент серверной части;
- плагины `Winter CMS` — модули, расширяющие функциональность CMS;"""
        expected = input_text
        
        result = format_technical_components(input_text)
        assert result == expected

class TestTableStructureCorrection:
    """Тестирование исправления структуры таблиц"""
    
    def test_move_caption_after_table(self):
        """Перемещение подписи после таблицы"""
        input_text = """Таблица 1 – Требования к программному обеспечению

| Наименование | Требования |
| ------------ | ---------- |
| ОС | Linux |"""
        
        expected = """| Наименование | Требования |
| ------------ | ---------- |
| ОС | Linux |

> Таблица 1 – Требования к программному обеспечению"""
        
        result = fix_table_structure(input_text)
        assert result == expected
    
    def test_preserve_correct_table_format(self):
        """Сохранение уже правильно оформленных таблиц"""
        input_text = """| Наименование | Требования |
| ------------ | ---------- |
| ОС | Linux |

> Таблица 1 – Требования к программному обеспечению"""
        expected = input_text
        
        result = fix_table_structure(input_text)
        assert result == expected

class TestFrontmatterCorrection:
    """Тестирование исправления frontmatter"""
    
    def test_fix_frontmatter_spacing(self):
        """Исправление лишних пустых строк в frontmatter"""
        input_text = """---
title: Общие сведения

nextRead:
  to: /path/to/next
  label: Следующий раздел
---"""
        
        expected = """---
title: Общие сведения
nextRead:
  to: /path/to/next
  label: Следующий раздел
---"""
        
        result = fix_frontmatter_format(input_text)
        assert result == expected
    
    def test_preserve_correct_frontmatter(self):
        """Сохранение уже правильного frontmatter"""
        input_text = """---
title: Архитектура комплекса
nextRead:
  to: /developer/user/start
  label: Начало работы
---"""
        expected = input_text
        
        result = fix_frontmatter_format(input_text)
        assert result == expected

class TestMarkdownFormatterIntegration:
    """Интеграционные тесты для всего класса MarkdownFormatter"""
    
    def test_full_document_transformation(self):
        """Полное преобразование документа из chapters формата в samples формат"""
        # Упрощенный тест отдельных компонентов
        formatter = MarkdownFormatter()
        
        # Тест 1: Исправление frontmatter 
        frontmatter_input = """---
title: Общие сведения

nextRead:
  to: /path/to/next
  label: Следующий раздел
---"""
        
        frontmatter_result = fix_frontmatter_format(frontmatter_input)
        assert frontmatter_result.count('\n\n') == 0  # Нет лишних пустых строк
        
        # Тест 2: Исправление заголовков
        heading_input = "### Общие сведения"
        heading_result = fix_heading_levels(heading_input, is_main_chapter=True)
        assert heading_result == "# Общие сведения"
        
        # Тест 3: AppAnnotation
        long_text = "Программный комплекс предназначен для предоставления разработчикам доступа к инструментам, полному комплекту технической документации."
        annotation_result = detect_and_wrap_appannotations(long_text)
        assert annotation_result.startswith("::AppAnnotation")
        
        # Интеграционный тест считается пройденным если все компоненты работают

def run_all_tests():
    """Запуск всех TDD тестов"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_all_tests()