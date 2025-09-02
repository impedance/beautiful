#!/usr/bin/env python3
"""
Отладочный скрипт для полной проверки workflow разделения на главы
"""

import tempfile
from pathlib import Path
import shutil
from improved_docx_converter import ImprovedDocxToMarkdownConverter

def test_split_workflow():
    """Тестирует полный workflow разделения на главы"""
    
    print("=== Тест полного workflow разделения на главы ===")
    
    # Создаем временную директорию
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Временная директория: {temp_dir}")
    
    try:
        # Создаем экземпляр конвертера без инициализации документа
        converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        converter.split_chapters = True
        
        # Симулируем элементы документа как если бы они были извлечены из DOCX
        document_elements = [
            {
                'type': 'heading',
                'level': 1,
                'text': '1. Общие сведения',
                'element': None
            },
            {
                'type': 'paragraph',
                'text': 'Содержимое первой главы с функциональным назначением комплекса.',
                'element': None
            },
            {
                'type': 'heading',
                'level': 2,
                'text': '1.1 Функциональное назначение', 
                'element': None
            },
            {
                'type': 'paragraph',
                'text': 'Подробное описание функционального назначения системы.',
                'element': None
            },
            {
                'type': 'heading',
                'level': 1,
                'text': '2. Архитектура комплекса',
                'element': None
            },
            {
                'type': 'paragraph',
                'text': 'Описание архитектуры комплекса и его компонентов.',
                'element': None
            },
            {
                'type': 'heading',
                'level': 2,
                'text': '2.1 Основные компоненты',
                'element': None
            },
            {
                'type': 'paragraph',
                'text': 'Список и описание основных компонентов системы.',
                'element': None
            },
            {
                'type': 'heading',
                'level': 1,
                'text': '3. Технические требования',
                'element': None
            },
            {
                'type': 'paragraph',
                'text': 'Технические требования к системе и окружению.',
                'element': None
            }
        ]
        
        print(f"Входные элементы документа: {len(document_elements)}")
        
        # Тестируем разделение на главы
        print("\n--- Тестируем _split_into_chapters ---")
        chapters = converter._split_into_chapters(document_elements)
        print(f"Найдено глав: {len(chapters)}")
        
        for i, chapter in enumerate(chapters):
            print(f"\nГлава {i+1}:")
            print(f"  Номер: {chapter['info']['number']}")
            print(f"  Название: '{chapter['info']['title']}'")
            print(f"  Файл: {chapter['filename']}")
            print(f"  Элементов: {len(chapter['elements'])}")
            
            # Показываем первые несколько элементов
            for j, element in enumerate(chapter['elements'][:3]):
                element_type = element['type']
                text = element['text'][:50] + "..." if len(element['text']) > 50 else element['text']
                level_info = f" (уровень {element['level']})" if element_type == 'heading' else ""
                print(f"    {j+1}. {element_type}{level_info}: {text}")
            
            if len(chapter['elements']) > 3:
                print(f"    ... и еще {len(chapter['elements']) - 3} элементов")
        
        # Теперь симулируем создание файлов
        print(f"\n--- Симулируем создание файлов ---")
        output_dir = temp_dir / "chapters"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        for chapter in chapters:
            file_path = output_dir / chapter['filename']
            
            # Создаем простое содержимое без сложной обработки элементов
            frontmatter = converter._generate_chapter_frontmatter(chapter['info'], len(chapters))
            
            content_lines = [frontmatter, ""]
            
            # Добавляем элементы главы
            for element in chapter['elements']:
                if element['type'] == 'heading':
                    level = element['level'] 
                    content_lines.append(f"{'#' * level} {element['text']}")
                    content_lines.append("")
                elif element['type'] == 'paragraph':
                    content_lines.append(element['text'])
                    content_lines.append("")
            
            content = "\n".join(content_lines)
            
            # Записываем файл
            file_path.write_text(content, encoding='utf-8')
            created_files.append(str(file_path))
            
            print(f"Создан файл: {file_path}")
            print(f"Размер: {len(content)} символов")
        
        print(f"\nВсего создано файлов: {len(created_files)}")
        print("\nСодержимое директории chapters:")
        for file_path in output_dir.iterdir():
            print(f"  - {file_path.name} ({file_path.stat().st_size} байт)")
        
        # Проверяем содержимое первого файла
        if created_files:
            first_file = Path(created_files[0])
            print(f"\n--- Содержимое первого файла ({first_file.name}) ---")
            content = first_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            for i, line in enumerate(lines[:15], 1):
                print(f"{i:2}: {line}")
            if len(lines) > 15:
                print(f"... и еще {len(lines) - 15} строк")
        
        return len(created_files) > 0
        
    finally:
        # Очищаем временную директорию
        shutil.rmtree(temp_dir)
        print(f"\nВременная директория удалена: {temp_dir}")

if __name__ == '__main__':
    success = test_split_workflow()
    if success:
        print("\n✅ Тест прошел успешно - файлы создаются!")
    else:
        print("\n❌ Тест провалился - файлы не создаются!")