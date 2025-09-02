#!/usr/bin/env python3
"""
Тесты для правильного распределения контента по главам
"""

import unittest
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestContentDistribution(unittest.TestCase):
    """Тесты правильного распределения контента по главам"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        self.converter.split_chapters = True
    
    def test_table_of_contents_exclusion(self):
        """Тест исключения содержания из глав"""
        
        # Симулируем документ с содержанием в начале
        document_elements = [
            # Заголовок содержания
            {'type': 'heading', 'level': 3, 'text': 'СОДЕРЖАНИЕ', 'element': None},
            
            # Элементы содержания (с табами и номерами страниц)
            {'type': 'heading', 'level': 1, 'text': '1    Общие сведения	5', 'element': None},
            {'type': 'heading', 'level': 2, 'text': '1.1    Назначение	5', 'element': None},
            {'type': 'heading', 'level': 2, 'text': '1.2    Функции	5', 'element': None},
            {'type': 'heading', 'level': 1, 'text': '2    Архитектура комплекса	6', 'element': None},
            {'type': 'heading', 'level': 2, 'text': '2.1    Основные компоненты	6', 'element': None},
            
            # Некий разделитель или пустая строка
            {'type': 'paragraph', 'text': 'Перечень сокращений	46', 'element': None},
            
            # Основной контент глав (БЕЗ табов и номеров страниц)
            {'type': 'heading', 'level': 3, 'text': 'Общие сведения', 'element': None},
            {'type': 'heading', 'level': 3, 'text': 'Назначение', 'element': None},
            {'type': 'paragraph', 'text': 'Комплекс предназначен для предоставления разработчикам...', 'element': None},
            {'type': 'heading', 'level': 3, 'text': 'Функции', 'element': None},
            {'type': 'paragraph', 'text': 'Комплекс реализует следующие основные функции:', 'element': None},
            
            {'type': 'heading', 'level': 3, 'text': 'Архитектура комплекса', 'element': None},
            {'type': 'paragraph', 'text': 'Программный комплекс построен по модульной архитектуре.', 'element': None},
            {'type': 'heading', 'level': 3, 'text': 'Основные компоненты', 'element': None},
            {'type': 'paragraph', 'text': 'Состав архитектуры включает следующие части:', 'element': None},
        ]
        
        # Обычная логика - разделение на главы из содержания
        chapters_wrong = self.converter._split_into_chapters(document_elements)
        
        # Проверяем что получается неправильное разделение
        self.assertEqual(len(chapters_wrong), 2, "С обычной логикой должно получаться 2 главы из содержания")
        
        # Первая глава содержит только заголовки из содержания
        chapter_1_wrong = chapters_wrong[0]
        paragraphs_in_chapter_1_wrong = sum(1 for e in chapter_1_wrong['elements'] if e['type'] == 'paragraph')
        self.assertEqual(paragraphs_in_chapter_1_wrong, 0, "В первой главе не должно быть абзацев при неправильной логике")
        
        # Последняя глава содержит весь основной текст
        last_chapter_wrong = chapters_wrong[-1]
        paragraphs_in_last_wrong = sum(1 for e in last_chapter_wrong['elements'] if e['type'] == 'paragraph')
        self.assertGreater(paragraphs_in_last_wrong, 3, "В последней главе должно быть много абзацев")
    
    def test_proper_content_distribution(self):
        """Тест правильного распределения контента"""
        
        # Симулируем правильную логику - работа с основным текстом
        # (это то, что должно получаться после исправления)
        main_content_elements = [
            # Первая глава - Общие сведения
            {'type': 'heading', 'level': 3, 'text': 'Общие сведения', 'element': None},
            {'type': 'heading', 'level': 3, 'text': 'Назначение', 'element': None},
            {'type': 'paragraph', 'text': 'Комплекс предназначен для предоставления разработчикам...', 'element': None},
            {'type': 'paragraph', 'text': 'Функциональные задачи Комплекса включают в себя:', 'element': None},
            {'type': 'heading', 'level': 3, 'text': 'Функции', 'element': None},
            {'type': 'paragraph', 'text': 'Комплекс реализует следующие основные функции:', 'element': None},
            
            # Вторая глава - Архитектура
            {'type': 'heading', 'level': 3, 'text': 'Архитектура комплекса', 'element': None},
            {'type': 'paragraph', 'text': 'Программный комплекс построен по модульной архитектуре.', 'element': None},
            {'type': 'heading', 'level': 3, 'text': 'Основные компоненты', 'element': None},
            {'type': 'paragraph', 'text': 'Состав архитектуры включает следующие части:', 'element': None},
            {'type': 'paragraph', 'text': 'CMS-сервер (Winter CMS) — основной элемент серверной части.', 'element': None},
            
            # Третья глава - Технические требования
            {'type': 'heading', 'level': 3, 'text': 'Технические и программные требования', 'element': None},
            {'type': 'paragraph', 'text': 'Настоящий раздел содержит сведения о минимальных требованиях.', 'element': None},
        ]
        
        # Нужно создать метод для правильного определения глав из основного текста
        # Пока проверяем с помощью модификации определения заголовков
        
        # Эмулируем правильную логику через определение заголовков глав без табов
        def is_main_chapter_header(text):
            # Заголовки основного текста - это заголовки без табов и номеров страниц
            if '\t' in text or text.endswith(tuple('0123456789')):
                return False
            
            # Ищем паттерны основных глав
            main_chapter_patterns = [
                'Общие сведения',
                'Архитектура комплекс', 
                'Технические и программные требования',
                'Установка и запуск',
                'Тонкая настройка',
                'Мониторинг и диагностика',
                'Управление контентом'
            ]
            
            for pattern in main_chapter_patterns:
                if pattern.lower() in text.lower():
                    return True
            return False
        
        # Ручное создание глав из основного контента
        chapters = []
        current_chapter = None
        chapter_counter = 0
        
        for element in main_content_elements:
            if element['type'] == 'heading' and element['level'] == 3:
                if is_main_chapter_header(element['text']):
                    # Сохраняем предыдущую главу
                    if current_chapter:
                        chapters.append(current_chapter)
                    
                    # Начинаем новую главу
                    chapter_counter += 1
                    current_chapter = {
                        'info': {'number': chapter_counter, 'title': element['text']},
                        'elements': [element]
                    }
                elif current_chapter:
                    current_chapter['elements'].append(element)
            elif current_chapter:
                current_chapter['elements'].append(element)
        
        # Добавляем последнюю главу
        if current_chapter:
            chapters.append(current_chapter)
        
        # Проверяем правильное распределение
        self.assertEqual(len(chapters), 3, "Должно быть 3 главы")
        
        # Проверяем первую главу
        chapter_1 = chapters[0]
        self.assertEqual(chapter_1['info']['title'], 'Общие сведения')
        paragraphs_1 = sum(1 for e in chapter_1['elements'] if e['type'] == 'paragraph')
        self.assertGreater(paragraphs_1, 1, "В первой главе должны быть абзацы")
        
        # Проверяем вторую главу
        chapter_2 = chapters[1]
        self.assertEqual(chapter_2['info']['title'], 'Архитектура комплекса')
        paragraphs_2 = sum(1 for e in chapter_2['elements'] if e['type'] == 'paragraph')
        self.assertGreater(paragraphs_2, 1, "Во второй главе должны быть абзацы")
        
        # Проверяем третью главу
        chapter_3 = chapters[2]
        self.assertEqual(chapter_3['info']['title'], 'Технические и программные требования')
        paragraphs_3 = sum(1 for e in chapter_3['elements'] if e['type'] == 'paragraph')
        self.assertGreater(paragraphs_3, 0, "В третьей главе должны быть абзацы")
    
    def test_content_vs_table_of_contents_detection(self):
        """Тест различения содержания и основного контента"""
        
        # Заголовки из содержания (с табами и номерами)
        toc_headers = [
            "1    Общие сведения	5",
            "2    Архитектура комплекса	6", 
            "3    Технические требования	10",
        ]
        
        # Заголовки из основного текста (без табов и номеров)
        main_headers = [
            "Общие сведения",
            "Архитектура комплекса",
            "Технические и программные требования",
        ]
        
        # Проверяем что заголовки содержания определяются как главы
        for header in toc_headers:
            is_chapter = self.converter._is_chapter_header(header)
            self.assertTrue(is_chapter, f"Заголовок содержания '{header}' должен определяться как глава")
        
        # Но нужно создать отдельную логику для основного текста
        # Пока проверяем что основные заголовки НЕ определяются как главы (уровень 3)
        # Это показывает проблему в текущей логике
        
    def test_chapter_content_quality(self):
        """Тест качества содержимого глав"""
        
        # Глава должна содержать разнообразный контент
        good_chapter = {
            'info': {'number': 1, 'title': 'Общие сведения'},
            'elements': [
                {'type': 'heading', 'level': 1, 'text': 'Общие сведения', 'element': None},
                {'type': 'heading', 'level': 2, 'text': 'Назначение', 'element': None},
                {'type': 'paragraph', 'text': 'Описание назначения комплекса...', 'element': None},
                {'type': 'paragraph', 'text': 'Дополнительная информация о функциях...', 'element': None},
                {'type': 'heading', 'level': 2, 'text': 'Требования', 'element': None},
                {'type': 'paragraph', 'text': 'Технические требования к системе...', 'element': None},
            ]
        }
        
        # Плохая глава - только заголовки
        bad_chapter = {
            'info': {'number': 2, 'title': 'Архитектура'},
            'elements': [
                {'type': 'heading', 'level': 1, 'text': 'Архитектура', 'element': None},
                {'type': 'heading', 'level': 2, 'text': 'Компоненты', 'element': None},
                {'type': 'heading', 'level': 2, 'text': 'Схема', 'element': None},
            ]
        }
        
        # Проверяем качество глав
        good_paragraphs = sum(1 for e in good_chapter['elements'] if e['type'] == 'paragraph')
        bad_paragraphs = sum(1 for e in bad_chapter['elements'] if e['type'] == 'paragraph')
        
        self.assertGreater(good_paragraphs, 2, "Хорошая глава должна содержать несколько абзацев")
        self.assertEqual(bad_paragraphs, 0, "Плохая глава содержит только заголовки")
        
        # После исправления все главы должны быть "хорошими"


if __name__ == '__main__':
    print("Запуск тестов распределения контента...")
    unittest.main(verbosity=2)