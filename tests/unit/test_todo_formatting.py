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


class FakeStyle:
    def __init__(self, name):
        self.name = name


class FakeIndent:
    def __init__(self, pt):
        self.pt = pt


class FakeParagraphFormat:
    def __init__(self, left_indent=None):
        self.left_indent = FakeIndent(left_indent) if left_indent is not None else None


class FakeParagraph:
    def __init__(self, text, style_name="Normal", left_indent=None):
        self.text = text
        self.runs = [FakeRun(text)]
        self.style = FakeStyle(style_name)
        self.paragraph_format = FakeParagraphFormat(left_indent)


docx_path = Path(__file__).parent.parent.parent / "dev.docx"


def test_placeholder_and_link_formatting():
    converter = ImprovedDocxToMarkdownConverter(str(docx_path))
    para = FakeParagraph(
        "<HASHED PASS> — хеш пароля (формирование описано в официальной документации: https://doc.traefik.io/traefik/middlewares/http/basicauth/)."
    )
    formatted = converter._format_inline_text(para)
    assert (
        formatted
        == "`<HASHED PASS>` — хеш пароля ([формирование описано в официальной документации](https://doc.traefik.io/traefik/middlewares/http/basicauth/))."
    )


def test_letter_enumerated_list_item():
    converter = ImprovedDocxToMarkdownConverter(str(docx_path))
    para = FakeParagraph(
        "б) Создать структуру директорий /opt/devstg.rosa.ru/traefik/ssl/ и разместить в ней TLS-сертификат и закрытый ключ.",
        style_name="List Number"
    )
    converter._process_list_item(para)
    assert (
        converter.markdown_lines[-1]
        == "b. Создать структуру директорий `/opt/devstg.rosa.ru/traefik/ssl/` и разместить в ней TLS-сертификат и закрытый ключ."
    )


def test_plain_text_link_conversion():
    converter = ImprovedDocxToMarkdownConverter(str(docx_path))
    para = FakeParagraph(
        "Подробности о работе с TLS-сертификатами приведены в официальной документации разработчиков сервиса: https://doc.traefik.io/traefik/https/tls/"
    )
    formatted = converter._format_inline_text(para)
    assert (
        formatted
        == "Подробности о работе с TLS-сертификатами приведены в [официальной документации разработчиков сервиса](https://doc.traefik.io/traefik/https/tls/)"
    )
