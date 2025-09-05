import doc2md.heading_numbering as hn


def test_add_numbering_anchor_followed_by_text(monkeypatch):
    html = '<a id="__RefHeading___3"></a>ФункцииКомплекс реализует функции'

    def fake_structure(_):
        return [(2, "1.2", "Функции")]

    monkeypatch.setattr(hn, "extract_heading_structure_from_toc", fake_structure)

    result = hn.add_numbering_to_html(html, "dummy.docx")
    assert result.startswith("<h2>1.2 Функции</h2>Комплекс")
