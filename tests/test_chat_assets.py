import re
from pathlib import Path

CHAT_JS = Path(__file__).resolve().parent.parent / "static" / "chat.js"


def test_chat_js_references_welcome_and_suggestion_i18n_keys():
    content = CHAT_JS.read_text(encoding="utf-8")
    for key in (
        "chat.welcome",
        "chat.suggestion_1",
        "chat.suggestion_2",
        "chat.suggestion_3",
    ):
        assert re.search(rf"I18n\.t\(['\"]{re.escape(key)}['\"]", content)


def test_chat_js_references_format_assistant_message():
    content = CHAT_JS.read_text(encoding="utf-8")
    assert "function formatAssistantMessage" in content
    assert "formatAssistantMessage(text)" in content