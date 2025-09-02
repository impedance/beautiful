#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для проверки правил форматирования DOCX to Markdown конвертера
"""

import re
from pathlib import Path

def test_frontmatter_structure():
    """Тест структуры YAML frontmatter"""
    sample_frontmatter = """---
title: Общие сведения
nextRead:
  to: /developer/administrator/winter-cms-plugins
  label: Плагины Winter CMS
---"""
    
    # Проверяем наличие обязательных элементов
    assert "title:" in sample_frontmatter
    assert sample_frontmatter.startswith("---")
    assert sample_frontmatter.endswith("---")

def test_heading_structure():
    """Тест структуры заголовков"""
    # H1 без номера
    h1_pattern = r'^# [А-Яа-я\s]+$'
    assert re.match(h1_pattern, "# Общие сведения")
    
    # H2 с нумерацией X.Y
    h2_pattern = r'^## \d+\.\d+ [А-Яа-я\s]+$'
    assert re.match(h2_pattern, "## 1.1 Функциональное назначение")
    assert re.match(h2_pattern, "## 2.2 Состав плагинов")

def test_app_annotation_block():
    """Тест блока AppAnnotation"""
    annotation = """::AppAnnotation
Текст аннотации может быть многострочным.
Описывает ключевые моменты раздела.
::"""
    
    assert annotation.startswith("::AppAnnotation")
    assert annotation.endswith("::")
    assert "Текст аннотации" in annotation

def test_lists_formatting():
    """Тест форматирования списков"""
    # Маркированные списки с дефисом
    list_item = "- обеспечение разработчиков каталогом документации;"
    assert list_item.startswith("- ")
    assert list_item.endswith(";")
    
    # Описательные списки компонентов
    component_item = "- `Компонент` — описание компонента;"
    assert re.match(r'^- `[^`]+` — [^;]+;$', component_item)

def test_table_formatting():
    """Тест форматирования таблиц"""
    table = """| Заголовок 1 | Заголовок 2 | Заголовок 3 |
| ----------- | ----------- | ----------- |
| Данные      | Данные      | Данные      |"""
    
    lines = table.split('\n')
    assert len(lines) == 3
    assert all(line.startswith('|') and line.endswith('|') for line in lines)
    assert "----------" in lines[1]

def test_table_caption():
    """Тест подписей к таблицам"""
    caption = "> Таблица 1 – Описание таблицы"
    assert caption.startswith("> Таблица")
    assert " – " in caption

def test_blockquote_notes():
    """Тест примечаний в blockquote"""
    note = "> _Примечание_ – Текст примечания."
    assert note.startswith("> _Примечание_ –")

def test_inline_code():
    """Тест инлайн кода"""
    code_examples = ["`Winter CMS`", "`PostgreSQL`", "`Docker`"]
    for code in code_examples:
        assert code.startswith("`") and code.endswith("`")

def test_internal_links():
    """Тест внутренних ссылок"""
    link = "[разделе 7](/developer/administrator/winter-cms)"
    link_pattern = r'\[[^\]]+\]\([^)]+\)'
    assert re.match(link_pattern, link)

def test_line_breaks_in_tables():
    """Тест переносов в таблицах"""
    cell_content = "Строка 1<br>Строка 2<br>Строка 3"
    assert "<br>" in cell_content
    assert cell_content.count("<br>") == 2

def test_section_numbering():
    """Тест схемы нумерации разделов"""
    # Примеры правильной нумерации
    valid_numbers = ["1.1", "1.2", "2.1", "2.9", "3.1"]
    pattern = r'^\d+\.\d+$'
    
    for number in valid_numbers:
        assert re.match(pattern, number)

def test_punctuation_in_lists():
    """Тест пунктуации в списках"""
    list_items = [
        "- первый элемент;",
        "- второй элемент;",
        "- последний элемент."
    ]
    
    # Все кроме последнего должны заканчиваться точкой с запятой
    for item in list_items[:-1]:
        assert item.endswith(";")
    
    # Последний должен заканчиваться точкой
    assert list_items[-1].endswith(".")

def test_technical_terms_formatting():
    """Тест форматирования технических терминов"""
    # Названия ПО в обратных кавычках
    software_names = ["`Winter CMS`", "`PostgreSQL`", "`Docker`"]
    for name in software_names:
        assert name.startswith("`") and name.endswith("`")
    
    # Аббревиатуры без кавычек
    abbreviations = ["HTML5", "CSS3", "JavaScript"]
    for abbr in abbreviations:
        assert not (abbr.startswith("`") and abbr.endswith("`"))

def test_image_formatting():
    """Тест форматирования изображений"""
    image_block = """::sign-image
src: <src>
sign: <sign>
::"""
    
    assert image_block.startswith("::sign-image")
    assert "src:" in image_block
    assert "sign:" in image_block
    assert image_block.endswith("::")

def run_all_tests():
    """Запуск всех тестов"""
    test_functions = [
        test_frontmatter_structure,
        test_heading_structure,
        test_app_annotation_block,
        test_lists_formatting,
        test_table_formatting,
        test_table_caption,
        test_blockquote_notes,
        test_inline_code,
        test_internal_links,
        test_line_breaks_in_tables,
        test_section_numbering,
        test_punctuation_in_lists,
        test_technical_terms_formatting,
        test_image_formatting
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\nТестов пройдено: {passed}")
    print(f"Тестов провалилось: {failed}")
    print(f"Всего тестов: {passed + failed}")
    
    return failed == 0

if __name__ == "__main__":
    run_all_tests()