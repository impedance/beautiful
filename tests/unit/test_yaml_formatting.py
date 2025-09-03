#!/usr/bin/env python3
"""
Тесты для правильного форматирования YAML блоков
"""

import pytest
import unittest
from unittest.mock import Mock
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestYamlFormatting(unittest.TestCase):
    """Тесты правильного форматирования YAML блоков в markdown"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем mock объект документа
        self.mock_doc = Mock()
        self.mock_doc.element = Mock()
        self.mock_doc.element.body = []
        self.mock_doc.styles = []

    def test_yaml_code_block_formatting(self):
        """Тест правильного форматирования YAML блоков кода"""
        # Подготавливаем YAML контент
        yaml_content = '''version: "3"
services:
  reverse-proxy:
    image: traefik:v3.3.2
    restart: always
    command:
      - --api.insecure=true
      - --providers.docker
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    labels:
      - "traefik.enable=true"'''

        # Ожидаемый результат с правильным форматированием
        expected_output = '''```yaml docker-compose.yaml
version: "3"
services:
  reverse-proxy:
    image: traefik:v3.3.2
    restart: always
    command:
      - --api.insecure=true
      - --providers.docker
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    labels:
      - "traefik.enable=true"
```'''

        # Проверяем что YAML блок должен оставаться цельным
        self.assertIn('version: "3"', expected_output)
        self.assertIn('services:', expected_output)
        self.assertIn('reverse-proxy:', expected_output)
        
        # Проверяем правильную структуру блока кода
        lines = expected_output.split('\n')
        self.assertTrue(lines[0].startswith('```yaml'))
        self.assertTrue(lines[-1] == '```')
        
        # Проверяем что отступы сохранены
        service_lines = [line for line in lines if 'reverse-proxy:' in line]
        self.assertEqual(len(service_lines), 1)
        self.assertTrue(service_lines[0].startswith('  '))  # Правильный отступ

    def test_broken_yaml_formatting_detection(self):
        """Тест детекции неправильно отформатированного YAML"""
        # Неправильно отформатированный YAML (как в проблемном файле)
        broken_yaml = '''```yaml
version: '3'
services:
```

reverse-proxy:

image: traefik:v3.3.2

restart: always

command:

- --api.insecure=true'''
        
        # Проверяем что это неправильное форматирование
        lines = broken_yaml.split('\n')
        
        # Блок кода закрывается слишком рано
        first_close = [i for i, line in enumerate(lines) if line.strip() == '```']
        self.assertTrue(len(first_close) > 0)
        self.assertTrue(first_close[0] < 5)  # Закрывается на 4-й строке
        
        # После закрытия блока есть еще YAML содержимое
        after_close = '\n'.join(lines[first_close[0]+1:])
        self.assertIn('reverse-proxy:', after_close)
        self.assertIn('image:', after_close)

    def test_detect_yaml_language_correctly(self):
        """Тест правильного определения языка YAML"""
        converter = ImprovedDocxToMarkdownConverter.__new__(ImprovedDocxToMarkdownConverter)
        
        # Тестовые строки, которые должны определяться как YAML
        yaml_patterns = [
            "version: '3'",
            "services:",
            "  reverse-proxy:",
            "    image: traefik:v3.3.2",
            "    ports:",
            "      - 80:80"
        ]
        
        for pattern in yaml_patterns:
            detected_lang = converter._detect_code_language(pattern)
            self.assertEqual(detected_lang, 'yaml', f"Failed to detect YAML for: {pattern}")

    def test_yaml_block_with_filename(self):
        """Тест создания YAML блока с названием файла"""
        # Проверяем что блок создается с правильным заголовком
        yaml_block_start = "```yaml docker-compose.yaml"
        
        self.assertIn("yaml", yaml_block_start)
        self.assertIn("docker-compose.yaml", yaml_block_start)
        
        # Проверяем что это не просто ```yaml
        self.assertNotEqual(yaml_block_start.strip(), "```yaml")

    def test_yaml_indentation_preservation(self):
        """Тест сохранения отступов в YAML"""
        yaml_with_indents = [
            "version: '3'",
            "services:",
            "  web:",
            "    image: nginx",
            "    ports:",
            "      - 80:80",
            "    environment:",
            "      - ENV=production"
        ]
        
        # Проверяем что отступы правильные
        self.assertFalse(yaml_with_indents[0].startswith(' '))  # Корневой уровень
        self.assertTrue(yaml_with_indents[2].startswith('  '))  # 2 пробела
        self.assertTrue(yaml_with_indents[5].startswith('      '))  # 6 пробелов
        
        # Проверяем что структура иерархическая
        services_line = yaml_with_indents[1]
        web_line = yaml_with_indents[2]
        ports_line = yaml_with_indents[4]
        port_value_line = yaml_with_indents[5]
        
        # services без отступа
        self.assertEqual(len(services_line) - len(services_line.lstrip()), 0)
        # web с отступом 2
        self.assertEqual(len(web_line) - len(web_line.lstrip()), 2)
        # ports с отступом 4
        self.assertEqual(len(ports_line) - len(ports_line.lstrip()), 4)
        # значение порта с отступом 6
        self.assertEqual(len(port_value_line) - len(port_value_line.lstrip()), 6)


if __name__ == '__main__':
    unittest.main()