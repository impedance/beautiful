#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для исправления ошибок форматирования в DOCX to Markdown конвертации

Реализует функции для преобразования неправильно сконвертированного markdown
(как в chapters/) в правильный формат (как в samples/)
"""

import re
from typing import List, Dict, Any

def fix_heading_levels(text: str, is_main_chapter: bool = False) -> str:
    """
    Исправляет уровни заголовков: H3 -> H1 или H2
    
    Args:
        text: Строка с заголовком
        is_main_chapter: True если это основной заголовок главы
    
    Returns:
        Исправленный заголовок
    """
    if text.startswith('###'):
        # Убираем один # для H3 -> H2, или два # для H3 -> H1
        if is_main_chapter:
            return text[2:]  # ### -> #
        else:
            return text[1:]  # ### -> ##
    
    # Возвращаем без изменений если уже правильный
    return text

def restore_section_numbering(sections: List[str], chapter_structure: Dict[int, int]) -> List[str]:
    """
    Восстанавливает нумерацию разделов согласно структуре (старая плоская версия)
    
    Args:
        sections: Список заголовков разделов
        chapter_structure: {номер_главы: количество_разделов}
    
    Returns:
        Список заголовков с добавленной нумерацией
    """
    result = []
    section_idx = 0
    
    for chapter, section_count in chapter_structure.items():
        for section_num in range(1, section_count + 1):
            if section_idx < len(sections):
                section_text = sections[section_idx]
                
                # Проверяем есть ли уже нумерация
                if re.match(r'^## \d+\.\d+', section_text):
                    result.append(section_text)  # Уже есть нумерация
                else:
                    # Добавляем нумерацию
                    section_name = section_text.replace('##', '').strip()
                    result.append(f"## {chapter}.{section_num} {section_name}")
                
                section_idx += 1
    
    return result

def restore_hierarchical_numbering(headings: List[str], chapter_number: int = 4) -> List[str]:
    """
    Восстанавливает иерархическую нумерацию заголовков
    
    Args:
        headings: Список заголовков с уровнями (##, ###, ####)
        chapter_number: Номер главы
    
    Returns:
        Список заголовков с правильной иерархической нумерацией
    """
    result = []
    counters = [chapter_number, 0, 0, 0]  # [глава, раздел, подраздел, подподраздел]
    
    for heading in headings:
        if not heading.strip():
            continue
            
        # Определяем уровень заголовка
        if heading.startswith('####'):
            level = 4
        elif heading.startswith('###'):  
            level = 3
        elif heading.startswith('##'):
            level = 2
        else:
            result.append(heading)
            continue
        
        # Обновляем счетчики
        if level == 2:
            counters[1] += 1
            counters[2] = 0
            counters[3] = 0
        elif level == 3:
            counters[2] += 1
            counters[3] = 0
        elif level == 4:
            counters[3] += 1
        
        # Извлекаем название заголовка без разметки и старой нумерации
        heading_text = heading
        heading_text = re.sub(r'^#+\s*', '', heading_text)  # убираем ##
        heading_text = re.sub(r'^\d+(\.\d+)*\s+', '', heading_text)  # убираем старую нумерацию
        
        # Формируем новую нумерацию
        if level == 2:
            new_number = f"{counters[0]}.{counters[1]}"
            new_heading = f"## {new_number} {heading_text}"
        elif level == 3:
            new_number = f"{counters[0]}.{counters[1]}.{counters[2]}"
            new_heading = f"### {new_number} {heading_text}"
        elif level == 4:
            new_number = f"{counters[0]}.{counters[1]}.{counters[2]}.{counters[3]}"
            new_heading = f"#### {new_number} {heading_text}"
        
        result.append(new_heading)
    
    return result

def fix_appannotation_usage(markdown_text: str) -> str:
    """
    Исправляет использование AppAnnotation блоков - убирает их из середины документа,
    оставляя только в самом начале (если необходимо)
    
    Args:
        markdown_text: Текст markdown с AppAnnotation блоками
        
    Returns:
        Исправленный текст без лишних AppAnnotation блоков
    """
    lines = markdown_text.split('\n')
    result_lines = []
    in_appannotation = False
    first_content_line = False  # Отслеживаем первый содержательный блок
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Пропускаем frontmatter
        if line.strip() == '---':
            result_lines.append(line)
            i += 1
            continue
        
        # Пропускаем заголовок документа
        if line.startswith('# '):
            result_lines.append(line)
            first_content_line = True
            i += 1
            continue
            
        # Обрабатываем AppAnnotation блоки
        if line.strip() == '::AppAnnotation':
            in_appannotation = True
            
            # Если это не самый первый контентный блок, просто убираем блок
            if first_content_line:
                # Ищем закрывающий тег и просто добавляем содержимое как обычный текст
                i += 1
                annotation_content = []
                while i < len(lines) and lines[i].strip() != '::':
                    annotation_content.append(lines[i])
                    i += 1
                
                # Добавляем содержимое как обычный параграф
                if annotation_content:
                    result_lines.extend(annotation_content)
                
                # Пропускаем закрывающий ::
                if i < len(lines) and lines[i].strip() == '::':
                    i += 1
                
                in_appannotation = False
                continue
            else:
                # Это первый блок - убираем AppAnnotation но оставляем содержимое
                i += 1
                annotation_content = []
                while i < len(lines) and lines[i].strip() != '::':
                    annotation_content.append(lines[i])
                    i += 1
                
                # Добавляем содержимое как обычный параграф
                result_lines.extend(annotation_content)
                first_content_line = True
                
                # Пропускаем закрывающий ::
                if i < len(lines) and lines[i].strip() == '::':
                    i += 1
                
                in_appannotation = False
                continue
        
        elif line.strip() == '::' and in_appannotation:
            in_appannotation = False
            i += 1
            continue
            
        else:
            if not in_appannotation:
                result_lines.append(line)
                if line.strip() and not line.startswith(('---', '#')):
                    first_content_line = True
        
        i += 1
    
    return '\n'.join(result_lines)

def detect_and_wrap_appannotations(text: str) -> str:
    """
    Детектирует описательные абзацы и оборачивает их в AppAnnotation блоки
    
    Args:
        text: Текст абзаца
        
    Returns:
        Текст, обернутый в AppAnnotation блок или без изменений
    """
    # Уже есть AppAnnotation - не трогаем
    if text.startswith('::AppAnnotation'):
        return text
    
    # Слишком короткий текст - не оборачиваем
    if len(text) < 100:
        return text
    
    # Проверяем наличие ключевых слов описательного характера
    keywords = ['комплекс', 'система', 'раздел', 'архитектура', 'предназначен', 'содержит']
    if any(keyword in text.lower() for keyword in keywords):
        return f"::AppAnnotation\n{text}\n::"
    
    return text

def convert_paragraphs_to_lists(text: str) -> str:
    """
    Преобразует последовательные абзацы в маркированный список
    
    Args:
        text: Текст с абзацами
        
    Returns:
        Текст с маркированным списком или без изменений
    """
    # Уже список - не трогаем
    if text.strip().startswith('- '):
        return text
    
    # Разбиваем на абзацы
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Проверяем что это последовательность элементов списка
    if len(paragraphs) >= 2:
        # Все элементы должны заканчиваться на ; кроме последнего на .
        is_list = True
        for i, para in enumerate(paragraphs):
            if i < len(paragraphs) - 1:
                if not para.endswith(';'):
                    is_list = False
                    break
            else:
                if not para.endswith('.'):
                    is_list = False
                    break
        
        if is_list:
            # Преобразуем в список
            result = []
            for para in paragraphs:
                result.append(f"- {para}")
            return '\n'.join(result)
    
    return text

def format_technical_components(text: str) -> str:
    """
    Форматирует технические компоненты в виде списка с обратными кавычками
    
    Args:
        text: Текст с компонентами
        
    Returns:
        Отформатированный список компонентов
    """
    # Уже правильно оформлен
    if text.strip().startswith('- `'):
        return text
    
    # Разбиваем на абзацы
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Проверяем что это компоненты (содержат технические термины)
    tech_indicators = ['CMS', 'сервер', 'плагин', 'СУБД', 'система', '—']
    
    if len(paragraphs) >= 2:
        is_tech_components = all(
            any(indicator in para for indicator in tech_indicators) 
            for para in paragraphs
        )
        
        if is_tech_components:
            result = []
            for para in paragraphs:
                # Находим технические термины и оборачиваем в кавычки
                para_formatted = para
                
                # Простая обработка для основных терминов
                tech_terms = ['CMS-сервер', 'Winter CMS', 'PostgreSQL', 'Redis', 'Docker', 'Traefik']
                for term in tech_terms:
                    if term in para_formatted and f'`{term}`' not in para_formatted:
                        para_formatted = para_formatted.replace(term, f'`{term}`')
                
                # Обеспечиваем правильную пунктуацию для всех элементов
                para_formatted = para_formatted.rstrip('.') + ';'
                
                result.append(f"- {para_formatted}")
            
            return '\n'.join(result)
    
    return text

def fix_table_structure(text: str) -> str:
    """
    Исправляет структуру таблиц: перемещает подпись после таблицы
    
    Args:
        text: Текст с таблицей
        
    Returns:
        Исправленная структура таблицы
    """
    lines = text.split('\n')
    
    # Ищем паттерн: подпись таблицы -> пустая строка -> таблица
    caption_idx = None
    table_start_idx = None
    
    for i, line in enumerate(lines):
        if line.startswith('Таблица') and '–' in line:
            caption_idx = i
        elif line.startswith('|') and caption_idx is not None:
            table_start_idx = i
            break
    
    if caption_idx is not None and table_start_idx is not None:
        # Извлекаем подпись
        caption = lines[caption_idx]
        
        # Находим конец таблицы
        table_end_idx = table_start_idx
        for i in range(table_start_idx + 1, len(lines)):
            if lines[i].startswith('|'):
                table_end_idx = i
            elif lines[i].strip() == '':
                continue
            else:
                break
        
        # Перестраиваем: таблица + пустая строка + подпись
        result_lines = []
        
        # Добавляем все до подписи (исключая её)
        result_lines.extend(lines[:caption_idx])
        
        # Пропускаем пустую строку после подписи если есть
        skip_idx = caption_idx + 1
        if skip_idx < len(lines) and lines[skip_idx].strip() == '':
            skip_idx += 1
        
        # Добавляем таблицу
        result_lines.extend(lines[skip_idx:table_end_idx + 1])
        
        # Добавляем пустую строку и подпись в формате blockquote
        result_lines.append('')
        result_lines.append(f"> {caption}")
        
        # Добавляем остальной текст если есть
        if table_end_idx + 1 < len(lines):
            result_lines.extend(lines[table_end_idx + 1:])
        
        return '\n'.join(result_lines)
    
    return text

def fix_frontmatter_format(text: str) -> str:
    """
    Исправляет формат YAML frontmatter: убирает лишние пустые строки
    
    Args:
        text: Текст с frontmatter
        
    Returns:
        Исправленный frontmatter
    """
    if not text.startswith('---'):
        return text
    
    # Находим границы frontmatter
    lines = text.split('\n')
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i] == '---':
            end_idx = i
            break
    
    if end_idx == -1:
        return text
    
    # Обрабатываем содержимое frontmatter
    frontmatter_lines = lines[1:end_idx]
    clean_frontmatter = []
    
    for line in frontmatter_lines:
        if line.strip() == '':
            # Пропускаем пустые строки в frontmatter
            continue
        clean_frontmatter.append(line)
    
    # Собираем обратно
    result_lines = ['---'] + clean_frontmatter + ['---'] + lines[end_idx + 1:]
    return '\n'.join(result_lines)

class MarkdownFormatter:
    """Основной класс для полной трансформации markdown документа"""
    
    def __init__(self):
        # Определяем структуру документа (глава -> количество разделов)
        self.document_structure = {
            1: 2,  # Глава 1: 2 раздела (Назначение, Функции)  
            2: 9,  # Глава 2: 9 разделов (Компоненты, Плагины, и т.д.)
            3: 3,  # Глава 3: 3 раздела (ПО, Аппаратура, Клиенты)
            4: 6,  # И так далее...
        }
    
    def transform_document(self, markdown_text: str, chapter_number: int = 1) -> str:
        """
        Полная трансформация документа из chapters формата в samples формат

        Args:
            markdown_text: Исходный markdown из chapters
            chapter_number: Номер главы, используемый при восстановлении нумерации

        Returns:
            Преобразованный markdown в формате samples
        """
        # 1. Исправляем frontmatter
        result = fix_frontmatter_format(markdown_text)
        
        # 2. Исправляем использование AppAnnotation блоков
        result = fix_appannotation_usage(result)
        
        # 3. Разбиваем на секции и группируем последовательные абзацы
        raw_sections = result.split('\n\n')
        sections = []
        buffer = []
        for sec in raw_sections:
            sec = sec.strip()
            if not sec:
                continue

            is_list_candidate = (
                (sec.endswith(';') or (buffer and sec.endswith('.')))
                and not sec.startswith(('#', '-', '::', '|', '>'))
            )

            if is_list_candidate:
                buffer.append(sec)
                continue

            if buffer:
                sections.append('\n\n'.join(buffer))
                buffer = []

            sections.append(sec)

        if buffer:
            sections.append('\n\n'.join(buffer))

        transformed_sections = []

        all_headings = []  # Собираем ВСЕ заголовки для иерархической нумерации

        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Исправляем заголовки
            if section.startswith('###'):
                # Определяем это главный заголовок или раздел
                # Простая эвристика: первый H3 - это главный заголовок
                is_main = len([s for s in transformed_sections if s.startswith('#')]) == 0
                fixed_heading = fix_heading_levels(section, is_main)
                all_headings.append(fixed_heading)
                transformed_sections.append(fixed_heading)
            elif section.startswith('##') or section.startswith('####'):
                # Собираем ВСЕ заголовки для иерархической обработки
                all_headings.append(section)
                transformed_sections.append(section)
            
            # Обрабатываем списки
            elif ';' in section and not section.startswith('-'):
                list_section = convert_paragraphs_to_lists(section)
                if list_section != section:
                    # Добавляем вводную фразу для списков функций
                    if 'предоставление' in section and 'разработчикам' in section:
                        transformed_sections.append("Комплекс реализует следующие основные функции:")
                        transformed_sections.append('')
                        transformed_sections.append(list_section)
                    else:
                        transformed_sections.append(list_section)
                else:
                    # Это просто многоабзацный текст со списковой структурой
                    # Проверяем можно ли преобразовать в список
                    if '\n\n' in section:
                        list_attempt = convert_paragraphs_to_lists(section)
                        if list_attempt != section:
                            transformed_sections.append("Комплекс реализует следующие основные функции:")
                            transformed_sections.append('')
                            transformed_sections.append(list_attempt)
                        else:
                            transformed_sections.append(section)
                    else:
                        transformed_sections.append(section)
            # Обрабатываем AppAnnotations
            elif len(section) > 100 and not section.startswith(('---', '::', '-', '|', '>')):
                wrapped = detect_and_wrap_appannotations(section)
                transformed_sections.append(wrapped)

            # Обрабатываем технические компоненты
            elif 'сервер' in section or 'плагин' in section:
                tech_formatted = format_technical_components(section)
                transformed_sections.append(tech_formatted)

            # Обрабатываем таблицы
            elif 'Таблица' in section and '|' in section:
                table_fixed = fix_table_structure(section)
                transformed_sections.append(table_fixed)

            else:
                transformed_sections.append(section)
        
        # 5. Восстанавливаем иерархическую нумерацию заголовков
        if all_headings:
            numbered_headings = restore_hierarchical_numbering(all_headings, chapter_number)
            
            # Заменяем заголовки в результате
            heading_idx = 0
            for i, section in enumerate(transformed_sections):
                if (section.startswith('##') or section.startswith('###') or section.startswith('####')) and heading_idx < len(numbered_headings):
                    transformed_sections[i] = numbered_headings[heading_idx]
                    heading_idx += 1
        
        return '\n\n'.join(transformed_sections)
