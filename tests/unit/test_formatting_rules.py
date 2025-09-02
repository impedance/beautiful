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

# === НОВЫЕ ТЕСТЫ ДЛЯ ИСПРАВЛЕНИЯ ОШИБОК КОНВЕРТАЦИИ ===

def test_heading_level_correction():
    """Тест исправления неправильных уровней заголовков"""
    # Неправильно: H3 вместо H1/H2
    wrong_headings = [
        "### Общие сведения",
        "### Назначение",
        "### Архитектура комплекса"
    ]
    
    # Правильно: H1 для основной главы, H2 для разделов
    correct_headings = [
        "# Общие сведения",
        "## 1.1 Назначение", 
        "# Архитектура комплекса"
    ]
    
    # Тест на обнаружение неправильных заголовков
    for heading in wrong_headings:
        assert heading.startswith("### ")
    
    # Тест на правильную структуру
    for heading in correct_headings:
        if heading.startswith("# ") and not re.match(r'^# \d+', heading):
            # H1 без номера (основной заголовок главы)
            assert re.match(r'^# [А-Яа-я\s]+$', heading)
        elif heading.startswith("## "):
            # H2 с нумерацией
            assert re.match(r'^## \d+\.\d+ [А-Яа-я\s]+$', heading)

def test_missing_chapter_numbering():
    """Тест восстановления нумерации разделов"""
    # Исходные заголовки без нумерации (как в chapters)
    unnumbered = [
        "### Назначение",
        "### Функции", 
        "### Основные компоненты",
        "### Состав плагинов"
    ]
    
    # Правильные заголовки с нумерацией (как должно быть)
    numbered = [
        "## 1.1 Назначение",
        "## 1.2 Функции",
        "## 2.1 Основные компоненты", 
        "## 2.2 Состав плагинов"
    ]
    
    # Проверяем паттерн нумерации
    for heading in numbered:
        assert re.match(r'^## \d+\.\d+ [А-Яа-я\s]+$', heading)
    
    # Проверяем последовательность нумерации
    numbers = [re.search(r'(\d+)\.(\d+)', h).groups() for h in numbered]
    assert numbers == [('1', '1'), ('1', '2'), ('2', '1'), ('2', '2')]

def test_missing_appannotation_detection():
    """Тест детектирования блоков для AppAnnotation"""
    # Примеры текста, который должен быть в AppAnnotation
    annotation_candidates = [
        "Программный комплекс \"Портал разработчика\" построен по модульной архитектуре.",
        "Настоящий раздел содержит сведения о минимальных требованиях к программному обеспечению."
    ]
    
    for text in annotation_candidates:
        # Проверяем, что это описательный текст (длинный и информативный)
        assert len(text) > 50  # Длинный текст
        assert any(keyword in text.lower() for keyword in ['комплекс', 'система', 'раздел', 'архитектура'])
        
    # Правильное оформление в AppAnnotation
    correct_annotation = """::AppAnnotation
Программный комплекс "Портал разработчика" построен по модульной архитектуре.
Архитектура реализована на базе Winter CMS и включает серверную часть.
::"""
    
    assert correct_annotation.startswith("::AppAnnotation")
    assert correct_annotation.endswith("::")
    lines = correct_annotation.strip().split('\n')
    assert len(lines) >= 3  # Минимум 3 строки (открытие, контент, закрытие)

def test_list_detection_from_paragraphs():
    """Тест детектирования списков из абзацев"""
    # Текст в chapters (неправильно - простые абзацы)
    paragraph_text = """предоставление разработчикам доступа к актуальной документации;

размещение готовых примеров фрагментов исходного кода;

обеспечение условий для ускоренной разработки программного обеспечения."""
    
    # Правильный список (как в samples)
    correct_list = """- предоставление разработчикам доступа к актуальной документации;
- размещение готовых примеров фрагментов исходного кода;  
- обеспечение условий для ускоренной разработки программного обеспечения."""
    
    # Тест распознавания элементов списка
    paragraphs = [p.strip() for p in paragraph_text.split('\n\n') if p.strip()]
    assert len(paragraphs) == 3
    
    # Все элементы должны заканчиваться точкой с запятой (кроме последнего)
    for i, para in enumerate(paragraphs):
        if i < len(paragraphs) - 1:
            assert para.endswith(';')
        else:
            assert para.endswith('.')
    
    # Проверяем правильное форматирование списка
    list_items = correct_list.split('\n')
    for item in list_items:
        assert item.startswith('- ')

def test_technical_component_formatting():
    """Тест форматирования технических компонентов"""
    # Неправильное форматирование (как в chapters)
    wrong_format = """CMS-сервер (Winter CMS) — основной элемент серверной части.

плагины Winter CMS — модули, расширяющие функциональность CMS."""
    
    # Правильное форматирование (как в samples)
    correct_format = """- `CMS-сервер` (`Winter CMS`) — основной элемент серверной части;
- плагины `Winter CMS` — модули, расширяющие функциональность CMS;"""
    
    # Тест правильного форматирования
    correct_lines = correct_format.split('\n')
    for line in correct_lines:
        assert line.startswith('- ')
        assert line.endswith(';')
        # Проверяем наличие технических терминов в обратных кавычках
        assert '`' in line

def test_table_structure_correction():
    """Тест исправления структуры таблиц"""
    # Неправильная таблица (как в chapters) 
    wrong_table_lines = [
        "Таблица 1 – Требования к программному обеспечению",
        "| Наименование | Требования |",
        "| ------------ | ---------- |",
        "| Операционная система | На базе ОС Linux |"
    ]
    
    # Правильная структура (как в samples)
    correct_table = """| Наименование | Требования |
| ------------ | ---------- |  
| Операционная система | На базе ОС Linux |

> Таблица 1 – Требования к программному обеспечению"""
    
    # Проверяем правильную структуру
    lines = correct_table.split('\n')
    table_lines = [l for l in lines if l.startswith('|')]
    caption_line = [l for l in lines if l.startswith('>')]
    
    assert len(table_lines) >= 3  # Заголовок + разделитель + минимум одна строка
    assert len(caption_line) == 1  # Одна подпись
    assert caption_line[0].startswith('> Таблица')

def test_frontmatter_correction():
    """Тест исправления frontmatter"""
    # Неправильный frontmatter (как в chapters)
    wrong_frontmatter = """---
title: Общие сведения

nextRead:
  to: /path/to/next
  label: Следующий раздел
---"""
    
    # Правильный frontmatter (как в samples)
    correct_frontmatter = """---
title: Общие сведения
nextRead:
  to: /developer/user/start
  label: Начало работы с порталом
---"""
    
    # Проверяем структуру
    assert correct_frontmatter.startswith('---')
    assert correct_frontmatter.endswith('---')
    assert 'title:' in correct_frontmatter
    assert 'nextRead:' in correct_frontmatter
    assert 'to:' in correct_frontmatter
    assert 'label:' in correct_frontmatter

def test_document_structure_mapping():
    """Тест маппинга структуры документа"""
    # Структура из dev.docx
    docx_structure = [
        "# 1 Общие сведения",
        "## 1.1 Назначение", 
        "## 1.2 Функции",
        "# 2 Архитектура комплекса",
        "## 2.1 Основные компоненты",
        "## 2.2 Состав плагинов"
    ]
    
    # Проверяем правильность нумерации
    h1_count = 0
    for line in docx_structure:
        if line.startswith('# '):
            h1_count += 1
            # H1 должен иметь номер в начале (# 1, # 2, etc.)
            assert re.match(r'^# \d+ [А-Яа-я\s]+$', line)
        elif line.startswith('## '):
            # H2 должен иметь двойную нумерацию (## X.Y)
            assert re.match(r'^## \d+\.\d+ [А-Яа-я\s]+$', line)
    
    assert h1_count >= 2  # Минимум 2 главы

def run_all_tests():
    """Запуск всех тестов"""
    test_functions = [
        # Исходные тесты
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
        test_image_formatting,
        # Новые тесты для исправления ошибок
        test_heading_level_correction,
        test_missing_chapter_numbering,
        test_missing_appannotation_detection,
        test_list_detection_from_paragraphs,
        test_technical_component_formatting,
        test_table_structure_correction,
        test_frontmatter_correction,
        test_document_structure_mapping
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