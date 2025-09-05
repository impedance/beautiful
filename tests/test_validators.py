from doc2md.validators import (
    run_all_validators,
    validate_app_annotations,
    validate_component_list_punctuation,
    validate_table_captions,
)


def test_validate_app_annotations() -> None:
    md_good = "::AppAnnotation\ntext\n::\n"
    md_bad = "::AppAnnotation\ntext\n"
    assert validate_app_annotations(md_good) == []
    assert "Mismatched" in validate_app_annotations(md_bad)[0]


def test_validate_table_captions() -> None:
    md_good = "> Таблица 1 – Описание\n"
    md_bad = "> Таблица X - Описание\n"
    assert validate_table_captions(md_good) == []
    assert validate_table_captions(md_bad)


def test_validate_component_list_punctuation() -> None:
    md_good = "- один;\n- два.\n"
    md_bad = "- один\n- два\n"
    assert validate_component_list_punctuation(md_good) == []
    warnings = validate_component_list_punctuation(md_bad)
    assert any(";" in w for w in warnings)
    assert any("." in w for w in warnings)


def test_run_all_validators_combines() -> None:
    md = "::AppAnnotation\ntext\n\n> Таблица X - Описание\n\n- item\n- last\n"
    warnings = run_all_validators(md)
    assert len(warnings) == 4
