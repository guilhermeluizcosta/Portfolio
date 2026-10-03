import json
import re
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "static" / "locales"
HOME_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "home.html"
SUPPORTED_LOCALES = ("en", "pt-BR")
CHAT_UI_KEYS = (
    "chat.welcome",
    "chat.cold_start_hint",
    "chat.suggestion_1",
    "chat.suggestion_2",
    "chat.suggestion_3",
)
SERVER_MESSAGE_KEYS = (
    "fill_fields",
    "email_success",
    "email_error",
    "chat_empty_question",
    "chat_limit_reached",
    "chat_unavailable",
    "chat_timeout",
)


def _load_locale(locale: str) -> dict:
    path = LOCALES_DIR / f"{locale}.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _template_i18n_keys() -> set[str]:
    content = HOME_TEMPLATE.read_text(encoding="utf-8")
    keys = set(re.findall(r'data-i18n="([^"]+)"', content))
    keys.update(re.findall(r'data-i18n-placeholder="([^"]+)"', content))
    return keys


def test_locale_files_exist_for_each_supported_language():
    for locale in SUPPORTED_LOCALES:
        assert (LOCALES_DIR / f"{locale}.json").is_file()


def test_locale_files_share_the_same_ui_keys():
    english = _load_locale("en")
    portuguese = _load_locale("pt-BR")

    assert set(english["ui"].keys()) == set(portuguese["ui"].keys())


def test_home_template_keys_exist_in_english_locale():
    english = _load_locale("en")
    template_keys = _template_i18n_keys()

    missing = template_keys - set(english["ui"].keys())
    assert missing == set()


def test_chat_ui_keys_exist_in_each_locale():
    for locale in SUPPORTED_LOCALES:
        data = _load_locale(locale)
        missing = set(CHAT_UI_KEYS) - set(data["ui"].keys())
        assert missing == set()


def test_server_messages_exist_in_each_locale():
    for locale in SUPPORTED_LOCALES:
        data = _load_locale(locale)
        assert set(data["server"].keys()) == set(SERVER_MESSAGE_KEYS)