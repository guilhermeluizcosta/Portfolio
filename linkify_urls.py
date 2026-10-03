import html
import re

URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")


def linkify_urls(text: str, escape: bool = True) -> str:
    if not text:
        return text

    def _maybe_escape(value: str) -> str:
        return html.escape(value) if escape else value

    parts = []
    last_end = 0
    for match in URL_PATTERN.finditer(text):
        parts.append(_maybe_escape(text[last_end : match.start()]))
        url = match.group(0)
        escaped_url = html.escape(url)
        parts.append(
            f'<a href="{escaped_url}" target="_blank" rel="noopener noreferrer">{escaped_url}</a>'
        )
        last_end = match.end()
    parts.append(_maybe_escape(text[last_end:]))
    return "".join(parts)