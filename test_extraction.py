#!/usr/bin/env python3
"""Тестирование извлечения глав из DOCX файлов."""

import sys
sys.path.append('./src')

from doc2md.splitter import extract_main_chapters_from_docx, extract_headings_from_docx

def test_chapter_extraction(docx_path: str):
    print(f"\n{'='*60}")
    print(f"ТЕСТИРОВАНИЕ ИЗВЛЕЧЕНИЯ ГЛАВ: {docx_path}")
    print(f"{'='*60}")
    
    # Извлекаем все заголовки
    print("\n1. ВСЕ ЗАГОЛОВКИ:")
    all_headings = extract_headings_from_docx(docx_path)
    for i, heading in enumerate(all_headings[:20]):  # показываем первые 20
        print(f"  {i+1:2d}. [{heading['style']:12s}] Lvl={heading['level']} IsMain={heading['is_main_chapter']} | {heading['text'][:80]}")
    
    if len(all_headings) > 20:
        print(f"     ... и ещё {len(all_headings) - 20} заголовков")
    
    # Извлекаем основные главы
    print(f"\n2. ОСНОВНЫЕ ГЛАВЫ (по текущему алгоритму):")
    main_chapters = extract_main_chapters_from_docx(docx_path)
    for i, chapter in enumerate(main_chapters):
        print(f"  {i+1}. {chapter}")
    
    print(f"\nВСЕГО ОСНОВНЫХ ГЛАВ: {len(main_chapters)}")
    
    # Показываем заголовки первого уровня с is_main_chapter=True
    print(f"\n3. ДЕТАЛИЗАЦИЯ ОСНОВНЫХ ГЛАВ:")
    for heading in all_headings:
        if heading['is_main_chapter'] and heading['level'] == 1:
            print(f"  ✓ [{heading['style']}] {heading['text']}")
    
    return main_chapters

def main():
    files_to_test = [
        "input/dev-portal-admin.docx",
        "input/dev-portal-user.docx"
    ]
    
    for file_path in files_to_test:
        try:
            main_chapters = test_chapter_extraction(file_path)
        except Exception as e:
            print(f"ОШИБКА при обработке {file_path}: {e}")

if __name__ == "__main__":
    main()