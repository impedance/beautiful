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
    Восстанавливает нумерацию разделов согласно структуре
    
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

        # 2. Собираем блоки абзацев, заканчивающихся ';' или '.',
        #    без пустых строк между ними, и преобразуем их в списки
        lines = result.split('\n')
        preprocessed_lines = []
        block_lines: List[str] = []

        def flush_block(add_blank_line: bool = False) -> None:
            nonlocal block_lines, preprocessed_lines
            if block_lines:
                block_text = '\n\n'.join(block_lines)
                converted = convert_paragraphs_to_lists(block_text)
                preprocessed_lines.extend(converted.split('\n'))
                if add_blank_line:
                    preprocessed_lines.append('')
                block_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped == '':
                flush_block()
                preprocessed_lines.append('')
            elif not stripped.startswith('-') and stripped.endswith((';', '.')):
                block_lines.append(stripped)
            else:
                flush_block(add_blank_line=True)
                preprocessed_lines.append(line)

        flush_block()
        result = '\n'.join(preprocessed_lines).strip()

        # 3. Разбиваем на секции для обработки
        sections = result.split('\n\n')
        transformed_sections = []
        
        h2_sections = []  # Собираем H2 заголовки для нумерации
        
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
                
                if fixed_heading.startswith('##'):
                    h2_sections.append(fixed_heading)
                
                transformed_sections.append(fixed_heading)
            
            # Обрабатываем AppAnnotations
            elif len(section) > 100 and not section.startswith(('---', '::', '-', '|', '>')):
                wrapped = detect_and_wrap_appannotations(section)
                transformed_sections.append(wrapped)
            
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
        
        # 4. Восстанавливаем нумерацию разделов
        if h2_sections:
            # Определяем структуру для текущей главы
            chapter_structure = {chapter_number: len(h2_sections)}
            numbered_sections = restore_section_numbering(h2_sections, chapter_structure)
            
            # Заменяем в результате
            section_idx = 0
            for i, section in enumerate(transformed_sections):
                if section.startswith('##') and section_idx < len(numbered_sections):
                    transformed_sections[i] = numbered_sections[section_idx]
                    section_idx += 1
        
        return '\n\n'.join(transformed_sections)
