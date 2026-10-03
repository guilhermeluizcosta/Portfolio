import html
import re

from linkify_urls import linkify_urls

BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*")
BULLET_PREFIX = "- "
URL_PATTERN = re.compile(r"https?://")


def _needs_formatting(text: str) -> bool:
    return bool(
        BOLD_PATTERN.search(text)
        or re.search(r"^- ", text, re.MULTILINE)
        or "\n\n" in text
        or URL_PATTERN.search(text)
        or "<" in text
        or ">" in text
    )


def format_inline(text: str) -> str:
    """Escape text, apply bold markers, and linkify URLs without double-escaping."""
    escaped = html.escape(text)
    with_bold = BOLD_PATTERN.sub(r"<strong>\1</strong>", escaped)
    return linkify_urls(with_bold, escape=False)


def format_assistant_message(text: str) -> str:
    """Render assistant markdown subset (bold, bullets, paragraphs, URLs) as safe HTML."""
    if not text:
        return text

    if not _needs_formatting(text):
        return text

    blocks = re.split(r"\n\n+", text.strip())
    rendered = []

    for block in blocks:
        lines = block.split("\n")
        non_empty = [line for line in lines if line.strip()]

        if non_empty and all(line.startswith(BULLET_PREFIX) for line in non_empty):
            items = "".join(
                f"<li>{format_inline(line[len(BULLET_PREFIX) :])}</li>"
                for line in non_empty
            )
            rendered.append(f"<ul>{items}</ul>")
            continue

        inline_text = block.replace("\n", " ")
        rendered.append(f"<p>{format_inline(inline_text)}</p>")

    return "".join(rendered)