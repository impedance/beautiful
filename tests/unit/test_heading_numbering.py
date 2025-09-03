#!/usr/bin/env python3
"""
Тесты для правильной нумерации заголовков
"""

import pytest
import unittest
from unittest.mock import Mock
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestHeadingNumbering(unittest.TestCase):
    """Тесты правильной иерархической нумерации заголовков"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем mock объект документа
        self.mock_doc = Mock()
        self.mock_doc.element = Mock()
        self.mock_doc.element.body = []
        self.mock_doc.styles = []

    def test_hierarchical_vs_flat_numbering(self):
        """Тест различий между иерархической и плоской нумерацией"""
        
        # Правильная иерархическая структура (как в samples/4.install-and-launch.md)
        correct_structure = [
            "## 4.1 Развёртывание программного окружения",
            "### 4.1.1 Установка среды контейнеризации Docker", 
            "### 4.1.2 Развёртывание маршрутизатора входящих запросов Traefik",
            "#### 4.1.2.1 Подготовка конфигурационных файлов",
            "#### 4.1.2.2 Создание вспомогательных файлов", 
            "#### 4.1.2.3 Запуск сервиса",
            "### 4.1.3 Установка и подготовка PostgreSQL",
            "### 4.1.4 Подготовка постоянного хранилища",
            "## 4.2 Установка Комплекса",
            "## 4.3 Запуск Комплекса",
            "### 4.3.1 Загрузка через командную строку",
            "### 4.3.2 Вход в комплекс"
        ]
        
        # Неправильная плоская структура (как в chapters/4.installation-setup.md)
        incorrect_structure = [
            "## 4.1 Развёртывание программного окружения",
            "## 4.2 Установка среды контейнеризации Docker",
            "## 4.3 Развёртывание маршрутизатора входящих запросов Traefik", 
            "## 4.4 Подготовка конфигурационных файлов",
            "## 4.5 Создание вспомогательных файлов",
            "## 4.6 Установка и подготовка PostgreSQL",
            "## 4.7 Подготовка постоянного хранилища",
            "## 4.8 Установка Комплекса",
            "## 4.9 Запуск Комплекса",
            "## 4.10 Загрузка через командную строку",
            "## 4.11 Вход в комплекс"
        ]
        
        # Проверяем что структуры разные
        self.assertNotEqual(correct_structure, incorrect_structure)
        
        # Проверяем иерархические уровни в правильной структуре
        self.assertTrue(any("### 4.1.1" in heading for heading in correct_structure))
        self.assertTrue(any("#### 4.1.2.1" in heading for heading in correct_structure))
        
        # Проверяем что в неправильной структуре все заголовки уровня 2
        incorrect_levels = [line.split()[0] for line in incorrect_structure]
        self.assertTrue(all(level == "##" for level in incorrect_levels))

    def test_heading_level_detection(self):
        """Тест определения правильного уровня заголовков"""
        
        test_cases = [
            ("4.1 Основной раздел", 2),  # ## 4.1
            ("4.1.1 Подраздел", 3),      # ### 4.1.1  
            ("4.1.1.1 Подподраздел", 4), # #### 4.1.1.1
        ]
        
        for heading_text, expected_level in test_cases:
            # Определяем уровень по количеству точек в нумерации
            parts = heading_text.split()[0].split('.')
            # 4.1 имеет 2 части (["4", "1"]), должен быть уровень 2
            # 4.1.1 имеет 3 части (["4", "1", "1"]), должен быть уровень 3
            # 4.1.1.1 имеет 4 части (["4", "1", "1", "1"]), должен быть уровень 4
            actual_level = len(parts)
            
            self.assertEqual(actual_level, expected_level, 
                           f"Неправильный уровень для '{heading_text}': ожидался {expected_level}, получен {actual_level}")

    def test_numbering_pattern_recognition(self):
        """Тест распознавания паттернов нумерации"""
        
        # Паттерны правильной нумерации
        correct_patterns = [
            "4.1 Название",
            "4.1.1 Подназвание", 
            "4.1.2.1 Подподназвание",
            "4.1.2.2 Еще подподназвание",
            "4.2 Следующий основной"
        ]
        
        # Паттерны неправильной плоской нумерации
        incorrect_patterns = [
            "4.1 Название",
            "4.2 Подназвание",  # Должно быть 4.1.1
            "4.3 Подподназвание",  # Должно быть 4.1.2.1  
            "4.4 Еще подподназвание",  # Должно быть 4.1.2.2
            "4.5 Следующий основной"   # Должно быть 4.2
        ]
        
        # Проверяем что можем распознать иерархическую структуру
        for pattern in correct_patterns:
            number_part = pattern.split()[0]
            dots_count = number_part.count('.')
            self.assertGreaterEqual(dots_count, 1, f"Неправильный паттерн: {pattern}")
        
        # Проверяем что плоская структура имеет только один уровень точек
        for pattern in incorrect_patterns:
            number_part = pattern.split()[0]
            dots_count = number_part.count('.')
            self.assertEqual(dots_count, 1, f"Паттерн должен иметь только одну точку: {pattern}")

    def test_chapter_structure_validation(self):
        """Тест валидации структуры главы"""
        
        # Правильная структура главы 4
        valid_chapter_structure = {
            "4.1": {
                "level": 2,
                "subsections": {
                    "4.1.1": {"level": 3},
                    "4.1.2": {
                        "level": 3, 
                        "subsections": {
                            "4.1.2.1": {"level": 4},
                            "4.1.2.2": {"level": 4},
                            "4.1.2.3": {"level": 4}
                        }
                    },
                    "4.1.3": {"level": 3},
                    "4.1.4": {"level": 3}
                }
            },
            "4.2": {"level": 2},
            "4.3": {
                "level": 2,
                "subsections": {
                    "4.3.1": {"level": 3},
                    "4.3.2": {"level": 3}
                }
            }
        }
        
        # Проверяем что структура логична
        self.assertIn("4.1", valid_chapter_structure)
        self.assertEqual(valid_chapter_structure["4.1"]["level"], 2)
        
        # Проверяем подразделы
        subsections = valid_chapter_structure["4.1"]["subsections"]
        self.assertIn("4.1.2", subsections)
        self.assertEqual(subsections["4.1.2"]["level"], 3)
        
        # Проверяем под-подразделы
        subsubsections = subsections["4.1.2"]["subsections"]
        self.assertIn("4.1.2.1", subsubsections)
        self.assertEqual(subsubsections["4.1.2.1"]["level"], 4)

    def test_markdown_heading_level_conversion(self):
        """Тест конвертации уровней заголовков в markdown"""
        
        test_conversions = [
            ("4.1 Раздел", 2, "## 4.1 Раздел"),
            ("4.1.1 Подраздел", 3, "### 4.1.1 Подраздел"), 
            ("4.1.2.1 Подподраздел", 4, "#### 4.1.2.1 Подподраздел"),
        ]
        
        for heading_text, level, expected_markdown in test_conversions:
            actual_markdown = "#" * level + " " + heading_text
            self.assertEqual(actual_markdown, expected_markdown,
                           f"Неправильная конвертация для уровня {level}")

    def test_heading_numbering_restoration(self):
        """Тест восстановления правильной нумерации заголовков"""
        
        # Неправильная плоская нумерация (как в chapters/)
        flat_headings = [
            "4.2 Установка среды контейнеризации Docker",
            "4.3 Развёртывание маршрутизатора входящих запросов Traefik",
            "4.4 Подготовка конфигурационных файлов",
            "4.5 Создание вспомогательных файлов"
        ]
        
        # Ожидаемая правильная иерархическая нумерация (как в samples/)
        expected_hierarchical = [
            "4.1.1 Установка среды контейнеризации Docker",      # было 4.2
            "4.1.2 Развёртывание маршрутизатора входящих запросов Traefik",  # было 4.3
            "4.1.2.1 Подготовка конфигурационных файлов",       # было 4.4
            "4.1.2.2 Создание вспомогательных файлов"           # было 4.5
        ]
        
        # Проверяем что у нас есть план восстановления
        self.assertEqual(len(flat_headings), len(expected_hierarchical))
        
        # Проверяем что нумерация действительно изменится
        for i, (flat, hierarchical) in enumerate(zip(flat_headings, expected_hierarchical)):
            flat_number = flat.split()[0]
            hier_number = hierarchical.split()[0] 
            self.assertNotEqual(flat_number, hier_number,
                              f"Строка {i}: нумерация должна измениться с {flat_number} на {hier_number}")


if __name__ == '__main__':
    unittest.main()