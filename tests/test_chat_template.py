from pathlib import Path

HOME_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "home.html"


def test_home_template_contains_cold_start_hint_i18n():
    content = HOME_TEMPLATE.read_text(encoding="utf-8")
    assert 'data-i18n="chat.cold_start_hint"' in content