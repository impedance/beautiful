import pytest
from pathlib import Path
from improved_docx_converter import ImprovedDocxToMarkdownConverter


class FakeFont:
    def __init__(self, name=None):
        self.name = name


class FakeRun:
    def __init__(self, text):
        self.text = text
        self.bold = False
        self.italic = False
        self.font = FakeFont()


class FakeParagraph:
    def __init__(self, text):
        self.text = text
        self.runs = [FakeRun(text)]


def test_service_and_filename_wrapped_with_backticks():
    docx_path = Path(__file__).parent.parent.parent / "dev.docx"
    converter = ImprovedDocxToMarkdownConverter(str(docx_path))
    para = FakeParagraph(
        "Для установки сервиса Traefik необходимо подготовить файл docker-compose.yaml со следующим содержанием:"
    )
    formatted = converter._format_inline_text(para)
    assert (
        formatted
        == "Для установки сервиса `Traefik` необходимо подготовить файл `docker-compose.yaml` со следующим содержанием:"
    )
