import unittest
import tempfile
import shutil
import os
import re
from pathlib import Path

from improved_docx_converter import ImprovedDocxToMarkdownConverter


class TestChapter2Formatting(unittest.TestCase):
    """Интеграционный тест проверки второй главы"""

    def test_chapter_two_numbering_and_lists(self):
        docx_path = Path("dev.docx")
        if not docx_path.exists():
            self.skipTest("Тестовый DOCX файл dev.docx не найден")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            shutil.copy(docx_path, tmpdir_path / "dev.docx")
            old_cwd = os.getcwd()
            os.chdir(tmpdir_path)
            try:
                converter = ImprovedDocxToMarkdownConverter(str(tmpdir_path / "dev.docx"), split_chapters=True)
                converter.convert_to_chapters()
                chapter_file = tmpdir_path / "chapters" / "2.architecture.md"
                self.assertTrue(chapter_file.exists(), "Файл второй главы должен существовать")
                content = chapter_file.read_text(encoding="utf-8")
                self.assertRegex(content, re.compile(r"^## 2\.\d+ ", re.MULTILINE))
                self.assertRegex(content, re.compile(r"^- ", re.MULTILINE))
            finally:
                os.chdir(old_cwd)
