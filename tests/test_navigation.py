from pathlib import Path

import frontmatter

from doc2md.navigation import inject_navigation_and_create_toc


def create_md(path: Path, title: str) -> None:
    content = f"---\ntitle: {title}\n---\n\n# {title}\n"
    path.write_text(content, encoding="utf-8")


def test_inject_navigation_and_create_toc(tmp_path: Path) -> None:
    files = [("a.md", "First"), ("b.md", "Second"), ("c.md", "Third")]
    for name, title in files:
        create_md(tmp_path / name, title)

    inject_navigation_and_create_toc(str(tmp_path))

    a = frontmatter.load(tmp_path / "a.md")
    b = frontmatter.load(tmp_path / "b.md")
    c = frontmatter.load(tmp_path / "c.md")

    assert "readPrev" not in a
    assert a["readNext"]["to"] == "/b"

    assert b["readPrev"]["label"] == "First"
    assert b["readNext"]["label"] == "Third"

    assert c["readPrev"]["to"] == "/b"
    assert "readNext" not in c

    toc_path = tmp_path / "toc.json"
    assert toc_path.exists()
    content = toc_path.read_text(encoding="utf-8")
    assert "First" in content and "Third" in content
