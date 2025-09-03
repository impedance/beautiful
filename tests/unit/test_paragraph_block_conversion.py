#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тестирование преобразования последовательных абзацев в список"""

from formatting_fixes import MarkdownFormatter


def test_paragraph_block_converted_to_list():
    formatter = MarkdownFormatter()
    input_text = "Первый пункт;\nВторой пункт;\nТретий пункт.\n\nДальше текст."
    expected = "- Первый пункт;\n- Второй пункт;\n- Третий пункт.\n\nДальше текст."
    result = formatter.transform_document(input_text)
    assert result == expected

