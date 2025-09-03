import re
import sys
import os
from pathlib import Path

# Ensure root path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from formatting_fixes import MarkdownFormatter


def test_transform_document_numbering_and_lists():
    formatter = MarkdownFormatter()
    markdown = (
        "### Архитектура\n\n"
        "### Основные компоненты\n\n"
        "предоставление разработчикам доступа к документации;\n\n"
        "размещение готовых примеров фрагментов исходного кода;\n\n"
        "обеспечение условий для ускоренной разработки программного обеспечения.\n\n"
        "### Состав плагинов\n\n"
        "Local – модуль расширения ядра CMS;\n\n"
        "Local.OAuth – реализация авторизации через сервис ROSA ID;\n\n"
        "Local.Snippets – внедрение переиспользуемых блоков контента.\n"
    )
    result = formatter.transform_document(markdown, chapter_number=2)

    assert "## 2.1 Основные компоненты" in result
    assert "## 2.2 Состав плагинов" in result
    assert re.search(r"^- .*доступа к документации;", result, re.MULTILINE)
    assert re.search(r"^- Local", result, re.MULTILINE)
