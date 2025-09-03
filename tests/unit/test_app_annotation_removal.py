"""Тесты для проверки удаления AppAnnotation из конвертера."""

import pytest
from pathlib import Path
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestAppAnnotationRemoval:
    """Тесты для проверки что AppAnnotation больше не используется."""
    
    def test_format_app_annotation_returns_plain_text(self):
        """Проверяет что _format_app_annotation возвращает обычный текст без оберток."""
        docx_path = Path(__file__).parent.parent.parent / "dev.docx"
        converter = ImprovedDocxToMarkdownConverter(str(docx_path))
        
        test_text = "Это тестовый текст для аннотации"
        result = converter._format_app_annotation(test_text)
        
        # Проверяем что результат - это просто исходный текст
        assert result == test_text
        assert "::AppAnnotation" not in result
        assert "::" not in result
    
    def test_converted_document_has_no_app_annotation(self):
        """Проверяет что в конвертированном документе нет AppAnnotation."""
        docx_path = Path(__file__).parent.parent.parent / "dev.docx"
        converter = ImprovedDocxToMarkdownConverter(str(docx_path))
        
        # Тестируем различные типы текста
        test_texts = [
            "Обычный текст",
            "Текст с форматированием",
            "Многострочный\nтекст\nс переносами"
        ]
        
        for text in test_texts:
            result = converter._format_app_annotation(text)
            
            # Убеждаемся что нет ни одного упоминания AppAnnotation
            assert "::AppAnnotation" not in result
            assert result == text
    
    def test_empty_text_handling(self):
        """Проверяет обработку пустого текста."""
        docx_path = Path(__file__).parent.parent.parent / "dev.docx"
        converter = ImprovedDocxToMarkdownConverter(str(docx_path))
        
        result = converter._format_app_annotation("")
        assert result == ""
        assert "::AppAnnotation" not in result
    
    def test_remove_app_annotation_markers(self):
        """Проверяет удаление маркеров ::AppAnnotation из текста."""
        docx_path = Path(__file__).parent.parent.parent / "dev.docx"
        converter = ImprovedDocxToMarkdownConverter(str(docx_path))
        
        test_cases = [
            ("::AppAnnotation\nТекст\n::", "Текст"),
            ("::AppAnnotation\nНесколько строк текста\nс переносами\n::", "Несколько строк текста\nс переносами"),
            ("Обычный текст без маркеров", "Обычный текст без маркеров"),
            ("::AppAnnotation\n::", ""),
            (":: только одинарные маркеры ::", "только одинарные маркеры"),
        ]
        
        for input_text, expected_output in test_cases:
            result = converter._remove_app_annotation_markers(input_text)
            assert result == expected_output, f"Failed for input: {input_text}"