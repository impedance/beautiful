"""Tests for preprocess module."""

import pytest
from doc2md.preprocess import remove_table_of_contents


def test_remove_table_of_contents_basic():
    """Test basic TOC removal functionality."""
    html = '''<p>Some intro text</p>
    <p>СОДЕРЖАНИЕ<a href="#__RefHeading___1">1 Section One 5</a>
    <a href="#__RefHeading___2">2 Section Two 10</a></p>
    <p><a href="#__RefHeading___3">3 Section Three 15</a></p>
    <p>Regular content continues here</p>'''
    
    result = remove_table_of_contents(html)
    
    # Should remove "СОДЕРЖАНИЕ" and all TOC links
    assert "СОДЕРЖАНИЕ" not in result
    assert "href=\"#__RefHeading___1\"" not in result
    assert "href=\"#__RefHeading___2\"" not in result
    assert "href=\"#__RefHeading___3\"" not in result
    assert "Regular content continues here" in result


def test_remove_table_of_contents_no_toc():
    """Test that HTML without TOC is unchanged."""
    html = '<p>Just regular content</p><p>More content</p>'
    
    result = remove_table_of_contents(html)
    
    assert result == '<html><body><p>Just regular content</p><p>More content</p></body></html>'


def test_remove_table_of_contents_preserves_other_links():
    """Test that non-TOC links are preserved."""
    html = '''<p>СОДЕРЖАНИЕ<a href="#__RefHeading___1">1 Section 5</a></p>
    <p><a href="https://example.com">External link</a> should remain</p>
    <p><a href="#other_anchor">Internal link</a> should remain</p>'''
    
    result = remove_table_of_contents(html)
    
    assert "СОДЕРЖАНИЕ" not in result
    assert "href=\"#__RefHeading___1\"" not in result
    assert "href=\"https://example.com\"" in result
    assert "href=\"#other_anchor\"" in result