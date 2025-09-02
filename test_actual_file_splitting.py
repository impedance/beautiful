#!/usr/bin/env python3
"""
Тест для проверки фактического создания файлов при разделении на главы
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestActualFileSplitting(unittest.TestCase):
    """Тест фактического создания файлов при разделении на главы"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_docx = self.temp_dir / "test.docx"
        
        # Создаем фиктивный DOCX файл
        self.test_docx.write_text("fake docx", encoding='utf-8')
        
    def tearDown(self):
        """Очистка после тестов"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_converter_creates_chapter_files(self):
        """Тест что конвертер фактически создает файлы глав"""
        # Импортируем конвертер
        from improved_docx_converter import ImprovedDocxToMarkdownConverter
        
        # Создаем мок-документ со структурой как в образцах
        mock_doc = Mock()
        mock_body = Mock()
        mock_doc.element.body = []
        
        # Создаем моки для параграфов с заголовками глав
        chapter_data = [
            ("1. Общие сведения", 1),
            ("1.1 Функциональное назначение", 2), 
            ("1.2 Требования к программной среде", 2),
            ("2. Архитектура комплекса", 1),
            ("2.1 Основные компоненты", 2),
            ("3. Технические требования", 1),
            ("3.1 Требования к ПО", 2)
        ]
        
        # Создаем моки элементов документа
        mock_elements = []
        for text, level in chapter_data:
            mock_element = Mock()
            mock_element.tag = "http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
            mock_para = Mock()
            mock_para.text = text
            
            # Мокаем определение уровня заголовка
            def mock_is_heading(para):
                if para.text == "1. Общие сведения":
                    return 1
                elif para.text == "2. Архитектура комплекса":
                    return 1  
                elif para.text == "3. Технические требования":
                    return 1
                elif para.text.startswith(("1.1", "1.2", "2.1", "3.1")):
                    return 2
                return None
                
            mock_elements.append((mock_element, mock_para))
        
        mock_doc.element.body = [elem[0] for elem in mock_elements]
        
        with patch('improved_docx_converter.Document') as mock_document_class, \
             patch('improved_docx_converter.Paragraph') as mock_paragraph_class:
            
            # Настраиваем мок Document
            mock_document_class.return_value = mock_doc
            
            # Настраиваем мок Paragraph
            def mock_paragraph_factory(element, doc):
                # Находим соответствующий мок-параграф для этого элемента
                for mock_element, mock_para in mock_elements:
                    if mock_element == element:
                        return mock_para
                return Mock(text="")
                
            mock_paragraph_class.side_effect = mock_paragraph_factory
            
            # Создаем конвертер с split_chapters=True
            converter = ImprovedDocxToMarkdownConverter(
                str(self.test_docx), 
                add_frontmatter=True,
                split_chapters=True
            )
            
            # Мокаем _is_heading для правильного определения заголовков
            def mock_is_heading_method(para):
                if para.text == "1. Общие сведения":
                    return 1
                elif para.text == "2. Архитектура комплекс":
                    return 1  
                elif para.text == "3. Технические требования":
                    return 1
                elif para.text.startswith(("1.1", "1.2", "2.1", "3.1")):
                    return 2
                return None
                
            converter._is_heading = mock_is_heading_method
            
            # Определяем директорию вывода
            output_dir = self.temp_dir / "chapters"
            
            # Вызываем convert_to_chapters
            try:
                created_files = converter.convert_to_chapters(str(output_dir))
                
                # Проверяем что файлы были созданы
                self.assertTrue(output_dir.exists(), "Директория chapters должна быть создана")
                
                # Проверяем что созданы файлы глав
                expected_files = [
                    "1.common.md",
                    "2.architecture.md", 
                    "3.technical-requirements.md"
                ]
                
                created_filenames = [Path(f).name for f in created_files]
                
                for expected_file in expected_files:
                    file_path = output_dir / expected_file
                    self.assertTrue(file_path.exists(), f"Файл {expected_file} должен быть создан")
                    
                    # Проверяем содержимое файла
                    content = file_path.read_text(encoding='utf-8')
                    self.assertTrue(content.startswith('---'), f"Файл {expected_file} должен начинаться с frontmatter")
                    self.assertIn('title:', content, f"Файл {expected_file} должен содержать title")
                    
                print(f"Созданы файлы: {created_filenames}")
                print(f"Содержимое директории: {list(output_dir.iterdir())}")
                
                return True
                
            except Exception as e:
                print(f"Ошибка при создании файлов глав: {e}")
                print(f"Содержимое temp_dir: {list(self.temp_dir.iterdir())}")
                if output_dir.exists():
                    print(f"Содержимое output_dir: {list(output_dir.iterdir())}")
                raise
    
    def test_integration_with_samples_structure(self):
        """Тест интеграции с структурой из samples"""
        samples_dir = Path("samples")
        if not samples_dir.exists():
            self.skipTest("Директория samples не найдена")
        
        # Проверяем что в samples есть ожидаемые файлы
        expected_files = ["1.common.md", "2.architecture.md", "3.technical-requirements.md"]
        
        for expected_file in expected_files:
            file_path = samples_dir / expected_file
            self.assertTrue(file_path.exists(), f"В samples должен быть файл {expected_file}")
            
            # Проверяем структуру файла
            content = file_path.read_text(encoding='utf-8')
            self.assertTrue(content.startswith('---'), f"Файл {expected_file} должен начинаться с frontmatter")
            self.assertIn('title:', content, f"Файл {expected_file} должен содержать title")


if __name__ == '__main__':
    print("Запуск тестов фактического создания файлов...")
    unittest.main(verbosity=2)