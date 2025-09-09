from doc2md.splitter import split_html_by_h1, split_html_using_docx_structure


def test_split_html_by_h1_splits_content() -> None:
    html = "<h1>One</h1><p>A</p><h1>Two</h1><p>B</p>"
    chapters = split_html_by_h1(html)
    assert len(chapters) == 2
    assert chapters[0].startswith("<h1>One")
    assert chapters[1].startswith("<h1>Two")


def test_split_html_by_h1_no_h1_tags_returns_empty_list() -> None:
    """Test that HTML without H1 tags returns empty list."""
    html = "<p>Some content</p><h2>Subheading</h2><p>More content</p>"
    chapters = split_html_by_h1(html)
    assert len(chapters) == 0


def test_split_html_by_h1_empty_html_returns_empty_list() -> None:
    """Test that empty HTML returns empty list."""
    chapters = split_html_by_h1("")
    assert len(chapters) == 0


def test_document_with_styled_headings_not_detected() -> None:
    """Test that styled headings without TOC anchors are not detected as chapters."""
    html_content = """
    <html>
    <body>
        <p><strong>ПЛАТФОРМА УПРАВЛЕНИЯ ГИБРИДНОЙ ИНФРАСТРУКТУРОЙ</strong></p>
        <p>Some heading text</p>
        <p>Content here</p>
        <p>Another heading</p>
        <p>More content</p>
    </body>
    </html>
    """

    chapters = split_html_by_h1(html_content)

    # Should return empty list since there are no TOC anchors
    assert len(chapters) == 0


def test_split_by_numbered_toc_anchors() -> None:
    """Test splitting HTML by numbered TOC anchors."""
    html_content = """
    <html>
    <body>
        <p>Introduction text</p>
        <p><a id="_Toc193363120"></a>1 Общие сведения</p>
        <p>Content of chapter 1</p>
        <p>More content for chapter 1</p>
        <p><a id="_Toc193363121"></a>2 Установка и настройка</p>
        <p>Content of chapter 2</p>
        <h2>Subsection in chapter 2</h2>
        <p><a id="_Toc193363122"></a>3 Веб-интерфейс</p>
        <p>Content of chapter 3</p>
    </body>
    </html>
    """

    chapters = split_html_by_h1(html_content)

    # Should return 3 chapters
    assert len(chapters) == 3

    # First chapter should contain anchor and content until next chapter
    assert "_Toc193363120" in chapters[0]
    assert "Общие сведения" in chapters[0]
    assert "Content of chapter 1" in chapters[0]
    assert "More content for chapter 1" in chapters[0]
    assert "2 Установка" not in chapters[0]

    # Second chapter should contain its anchor and content
    assert "_Toc193363121" in chapters[1]
    assert "2 Установка и настройка" in chapters[1]
    assert "Content of chapter 2" in chapters[1]
    assert "Subsection in chapter 2" in chapters[1]
    assert "3 Веб-интерфейс" not in chapters[1]

    # Third chapter should contain its content
    assert "_Toc193363122" in chapters[2]
    assert "3 Веб-интерфейс" in chapters[2]
    assert "Content of chapter 3" in chapters[2]


def test_split_by_major_section_toc_anchors() -> None:
    """Test splitting HTML by major section TOC anchors (like in real ROSA document)."""
    html_content = """
    <html>
    <body>
        <p>Table of contents and intro</p>
        <p><a id="_Toc193363120"></a>Общие сведения</p>
        <p>Content about general information</p>
        <p>More details</p>
        <p><a id="_Toc193363126"></a>Установка и настройка</p>
        <p>Installation content</p>
        <h2>Configuration subsection</h2>
        <p><a id="_Toc193363127"></a>Веб-интерфейс</p>
        <p>Web interface description</p>
        <p><a id="_Toc193363128"></a>API</p>
        <p>API documentation</p>
    </body>
    </html>
    """

    chapters = split_html_by_h1(html_content)

    # Should return 4 chapters
    assert len(chapters) == 4

    # First chapter - General information
    assert "_Toc193363120" in chapters[0]
    assert "Общие сведения" in chapters[0]
    assert "Content about general information" in chapters[0]
    assert "More details" in chapters[0]
    assert "Установка и настройка" not in chapters[0]

    # Second chapter - Installation
    assert "_Toc193363126" in chapters[1]
    assert "Установка и настройка" in chapters[1]
    assert "Installation content" in chapters[1]
    assert "Configuration subsection" in chapters[1]
    assert "Веб-интерфейс" not in chapters[1]

    # Third chapter - Web interface
    assert "_Toc193363127" in chapters[2]
    assert "Веб-интерфейс" in chapters[2]
    assert "Web interface description" in chapters[2]
    assert "API" not in chapters[2]

    # Fourth chapter - API
    assert "_Toc193363128" in chapters[3]
    assert "API" in chapters[3]
    assert "API documentation" in chapters[3]


def test_split_html_using_docx_structure_sequential(monkeypatch, tmp_path) -> None:
    """Ensure sequential search prevents earlier references affecting splitting."""

    html = (
        "<p>См. раздел 'Вторая глава' ниже</p>"
        "<p>Введение</p>"
        "<p>Еще текст</p>"
        "<h1>Первая глава</h1><p>A</p>"
        "<h1>Вторая глава</h1><p>B</p>"
        "<h1>Третья глава</h1><p>C</p>"
    )

    monkeypatch.setattr(
        "doc2md.splitter.extract_main_chapters_from_docx",
        lambda _path: ["Первая глава", "Вторая глава", "Третья глава"],
    )

    dummy = tmp_path / "dummy.docx"
    dummy.write_text("temp")
    chapters = split_html_using_docx_structure(html, str(dummy))

    assert len(chapters) == 3
    assert chapters[0].startswith("<h1>1 Первая глава</h1>")
    assert chapters[1].startswith("<h1>2 Вторая глава</h1>")
    assert "A" not in chapters[1]
    assert chapters[2].startswith("<h1>3 Третья глава</h1>")


def test_missing_intermediate_heading(monkeypatch, tmp_path) -> None:
    """If a chapter title isn't found, previous chapter should end at next available heading."""

    html = "<h1>Intro</h1><p>A</p><h1>Conclusion</h1><p>B</p>"

    monkeypatch.setattr(
        "doc2md.splitter.extract_main_chapters_from_docx",
        lambda _path: ["Intro", "Middle", "Conclusion"],
    )

    dummy = tmp_path / "dummy.docx"
    dummy.write_text("temp")

    chapters = split_html_using_docx_structure(html, str(dummy))

    assert len(chapters) == 2
    assert chapters[0].startswith("<h1>1 Intro</h1>")
    assert "Conclusion" not in chapters[0]
    assert chapters[1].startswith("<h1>2 Conclusion</h1>")


def test_global_content_filtering(monkeypatch, tmp_path) -> None:
    """Global content like copyright and support info should be filtered from last chapter."""

    html = """<h1>Chapter 1</h1><p>Content 1</p>
    <h1>Chapter 2</h1><p>Content 2</p>
    <p>Техническая поддержка: support@example.com</p>
    <p>© 2024 Все права защищены</p>"""

    monkeypatch.setattr(
        "doc2md.splitter.extract_main_chapters_from_docx",
        lambda _path: ["Chapter 1", "Chapter 2"],
    )

    dummy = tmp_path / "dummy.docx"
    dummy.write_text("temp")

    chapters = split_html_using_docx_structure(html, str(dummy))

    assert len(chapters) == 2
    
    # Chapter 1 should have its content
    assert "Content 1" in chapters[0]
    assert "техническая поддержка" not in chapters[0].lower()
    assert "все права защищены" not in chapters[0].lower()
    
    # Chapter 2 should have its content but NOT the global footer
    assert "Content 2" in chapters[1]
    assert "техническая поддержка" not in chapters[1].lower()
    assert "все права защищены" not in chapters[1].lower()


def test_toc_global_content_filtering() -> None:
    """Global content should also be filtered when using TOC anchor splitting."""
    html_content = """
    <html>
    <body>
        <p><a id="_Toc123"></a>1 Первая глава</p>
        <p>Content of chapter 1</p>
        <p><a id="_Toc124"></a>2 Вторая глава</p>
        <p>Content of chapter 2</p>
        <p>Техническая поддержка: support@example.com</p>
        <p>© 2024 Все права защищены</p>
    </body>
    </html>
    """

    chapters = split_html_by_h1(html_content)

    assert len(chapters) == 2

    # Chapter 1 should have its content
    assert "Content of chapter 1" in chapters[0]
    assert "техническая поддержка" not in chapters[0].lower()
    assert "все права защищены" not in chapters[0].lower()
    
    # Chapter 2 should have its content but NOT the global footer
    assert "Content of chapter 2" in chapters[1]
    assert "техническая поддержка" not in chapters[1].lower()
    assert "все права защищены" not in chapters[1].lower()
