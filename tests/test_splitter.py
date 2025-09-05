from doc2md.splitter import split_html_by_h1


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
