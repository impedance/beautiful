from doc2md.postprocess import PostProcessor


def test_postprocessor_normalizes_headings() -> None:
    md = "## Intro\n### Detail\n#### Deep\n### Next\n## Second\n"
    processor = PostProcessor(md, chapter_number=1, doc_slug="slug")
    lines = processor.run().splitlines()
    assert lines[0] == "## 1.1 Intro"
    assert lines[1] == "### 1.1.1 Detail"
    assert lines[2] == "#### 1.1.1.1 Deep"
    assert lines[3] == "### 1.1.2 Next"
    assert lines[4] == "## 1.2 Second"


def test_postprocessor_rewrites_image_paths() -> None:
    md = "Here\n![Alt](image.png)\n"
    processor = PostProcessor(md, chapter_number=2, doc_slug="guide")
    result = processor.run()
    assert "![Alt](/images/developer/administrator/guide/image.png)" in result
