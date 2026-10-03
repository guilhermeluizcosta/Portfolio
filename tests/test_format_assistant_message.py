import pytest

from format_assistant_message import format_assistant_message


@pytest.mark.parametrize(
    ("text", "expected_fragment"),
    [
        ("**Banco Inter** – dev", "<strong>Banco Inter</strong>"),
        ("- **A**\n- **B**", "<ul>"),
        ("Parágrafo 1\n\nParágrafo 2", "<p>"),
        (
            "Veja https://github.com/foo",
            '<a href="https://github.com/foo" target="_blank" rel="noopener noreferrer">',
        ),
    ],
)
def test_format_assistant_message(text, expected_fragment):
    result = format_assistant_message(text)
    assert expected_fragment in result


def test_format_assistant_message_list_has_two_items():
    result = format_assistant_message("- **A**\n- **B**")
    assert result.count("<li>") == 2


def test_format_assistant_message_two_paragraphs():
    result = format_assistant_message("Parágrafo 1\n\nParágrafo 2")
    assert result.count("<p>") == 2


def test_format_assistant_message_escapes_script():
    result = format_assistant_message("<script>alert(1)</script>")
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_format_assistant_message_plain_text():
    result = format_assistant_message("Sem markdown")
    assert result == "Sem markdown"
    assert "<" not in result