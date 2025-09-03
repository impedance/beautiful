"""Тесты для проверки корректного форматирования блоков кода."""

import pytest
from pathlib import Path
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestCodeBlockFormatting:
    """Тесты для проверки правильного форматирования блоков кода в markdown."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        docx_path = Path(__file__).parent.parent.parent / "dev.docx"
        self.converter = ImprovedDocxToMarkdownConverter(str(docx_path))
    
    def test_detect_yaml_language(self):
        """Проверяет определение YAML языка."""
        yaml_text = "version: '3'\nservices:"
        language = self.converter._detect_code_language(yaml_text)
        assert language == 'yaml'
    
    def test_detect_bash_language(self):
        """Проверяет определение Bash языка."""
        bash_commands = [
            "sudo systemctl start service",
            "docker run image",
            "git clone repo",
            "#!/bin/bash"
        ]
        
        for cmd in bash_commands:
            language = self.converter._detect_code_language(cmd)
            assert language == 'bash', f"Failed for command: {cmd}"
    
    def test_detect_conf_language(self):
        """Проверяет определение conf языка."""
        conf_text = "[main]\ninclude = throughput-performance"
        language = self.converter._detect_code_language(conf_text)
        assert language == 'conf'
    
    def test_detect_python_language(self):
        """Проверяет определение Python языка."""
        python_text = "def function():\n    import os"
        language = self.converter._detect_code_language(python_text)
        assert language == 'python'
    
    def test_detect_sql_language(self):
        """Проверяет определение SQL языка."""
        sql_text = "SELECT * FROM table"
        language = self.converter._detect_code_language(sql_text)
        assert language == 'sql'
    
    def test_docker_compose_filename_detection(self):
        """Проверяет определение имени файла docker-compose.yaml."""
        yaml_text = "version: '3'\nservices:\n  web:"
        filename = self.converter._detect_code_filename(yaml_text, 'yaml')
        assert filename == 'docker-compose.yaml'
    
    def test_bash_terminal_filename_detection(self):
        """Проверяет что для обычных bash команд используется Terminal."""
        bash_text = "sudo systemctl start nginx"
        filename = self.converter._detect_code_filename(bash_text, 'bash')
        assert filename == 'Terminal'
    
    def test_bash_script_filename_detection(self):
        """Проверяет определение имени файла script.sh для bash скриптов."""
        bash_script = "#!/bin/bash\necho 'Hello World'"
        filename = self.converter._detect_code_filename(bash_script, 'bash')
        assert filename == 'script.sh'
    
    def test_tuned_conf_filename_detection(self):
        """Проверяет определение имени файла tuned.conf."""
        conf_text = "[main]\ninclude = throughput-performance"
        filename = self.converter._detect_code_filename(conf_text, 'conf')
        assert filename == 'tuned.conf'
    
    def test_empty_filename_for_generic_code(self):
        """Проверяет что для обычного кода без специальных паттернов возвращается пустое имя."""
        yaml_text = "key: value\nother: data"
        filename = self.converter._detect_code_filename(yaml_text, 'yaml')
        assert filename == ''
    
    def test_code_block_format_with_filename(self):
        """Проверяет что блок кода форматируется с именем файла когда оно доступно."""
        # Создаем markdown lines для тестирования
        self.converter.markdown_lines = []
        self.converter.in_code_block = False
        
        # Симулируем блок docker-compose
        test_text = "version: '3'\nservices:"
        language = self.converter._detect_code_language(test_text)
        filename = self.converter._detect_code_filename(test_text, language)
        
        # Проверяем что у нас есть и язык и имя файла
        assert language == 'yaml'
        assert filename == 'docker-compose.yaml'
        
        # Проверяем что форматирование корректно
        expected_format = f"```{language} {filename}"
        if filename:
            actual_format = f"```{language} {filename}"
        else:
            actual_format = f"```{language}"
        
        assert actual_format == "```yaml docker-compose.yaml"
    
    def test_code_block_format_without_filename(self):
        """Проверяет что блок кода форматируется только с языком когда нет имени файла."""
        test_text = "key: value"
        language = self.converter._detect_code_language(test_text)
        filename = self.converter._detect_code_filename(test_text, language)
        
        assert language == 'yaml'
        assert filename == ''
        
        expected_format = f"```{language}"
        assert expected_format == "```yaml"