import pytest

from linkify_urls import linkify_urls


@pytest.mark.parametrize(
    ("text", "expected_fragment"),
    [
        (
            "Veja https://github.com/foo",
            '<a href="https://github.com/foo" target="_blank" rel="noopener noreferrer">',
        ),
        ("Sem link aqui", "Sem link aqui"),
        (
            "http://a.com e https://b.com",
            '<a href="http://a.com" target="_blank" rel="noopener noreferrer">',
        ),
    ],
)
def test_linkify_urls(text, expected_fragment):
    result = linkify_urls(text)
    assert expected_fragment in result
    if "Sem link aqui" in text:
        assert "<a" not in result


def test_linkify_urls_two_distinct_links():
    result = linkify_urls("http://a.com e https://b.com")
    assert result.count('rel="noopener noreferrer"') == 2
    assert 'href="http://a.com"' in result
    assert 'href="https://b.com"' in result