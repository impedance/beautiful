#!/usr/bin/env python3
"""Отладка проблем с dev-portal-user.docx файлом."""

import sys
sys.path.append('./src')

from doc2md.preprocess import convert_docx_to_html
from doc2md.splitter import extract_main_chapters_from_docx_with_position
from bs4 import BeautifulSoup
import re

def debug_user_docx():
    docx_path = "input/dev-portal-user.docx"
    
    print("ОТЛАДКА dev-portal-user.docx")
    print("="*50)
    
    # Получаем главы из DOCX
    main_chapters = extract_main_chapters_from_docx_with_position(docx_path, limit=4)
    print(f"Найдено {len(main_chapters)} глав в DOCX:")
    for chapter in main_chapters:
        print(f"  - {chapter['title']} (стиль: {chapter['style']}, позиция: {chapter['position']})")
    
    # Конвертируем в HTML
    html_content = convert_docx_to_html(docx_path, "src/doc2md/mammoth_style_map.map")
    soup = BeautifulSoup(html_content, "lxml")
    
    print(f"\nHTML длина: {len(html_content)} символов")
    
    # Найдём все заголовочные элементы
    print("\nВСЕ H1-H6 ТЕГИ:")
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        elements = soup.find_all(tag)
        print(f"  {tag.upper()}: {len(elements)} элементов")
        for i, elem in enumerate(elements[:5]):  # показываем первые 5
            text = elem.get_text(strip=True)[:80]
            print(f"    {i+1}. {text}")
    
    # Ищем возможные заголовки в P тегах
    print(f"\nВСЕ P ТЕГИ с коротким текстом (возможные заголовки):")
    p_elements = soup.find_all('p')
    print(f"Всего P тегов: {len(p_elements)}")
    
    short_p_elements = []
    for i, p in enumerate(p_elements):
        text = p.get_text(strip=True)
        # Короткие p теги могут быть заголовками
        if text and len(text.split()) <= 10 and not re.search(r'\d+\s*$', text):
            short_p_elements.append((i, p, text))
    
    print(f"Коротких P тегов (возможные заголовки): {len(short_p_elements)}")
    for i, (idx, p, text) in enumerate(short_p_elements[:20]):  # первые 20
        print(f"  {i+1:2d}. [{idx:3d}] {text}")
    
    # Поищем наши специфичные заголовки
    print(f"\nПОИСК СПЕЦИФИЧНЫХ ЗАГОЛОВКОВ:")
    titles_to_find = ['Общие сведения', 'Начало работы с порталом', 'Компоненты пользовательского интерфейса']
    
    for title in titles_to_find:
        print(f"\nИщем: '{title}'")
        
        # Поиск в тексте
        found_elements = []
        for string in soup.find_all(string=re.compile(re.escape(title), re.IGNORECASE)):
            parent = string.find_parent(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if parent:
                found_elements.append(parent)
        
        print(f"  Найдено {len(found_elements)} элементов:")
        for i, elem in enumerate(found_elements):
            text = elem.get_text(strip=True)[:100]
            print(f"    {i+1}. <{elem.name}> {text}")
    
    # Сохраняем первую часть HTML для анализа
    with open('debug_user_html_start.html', 'w', encoding='utf-8') as f:
        f.write(html_content[:50000])  # первые 50k символов
    print(f"\nПервая часть HTML сохранена в debug_user_html_start.html")

if __name__ == "__main__":
    debug_user_docx()