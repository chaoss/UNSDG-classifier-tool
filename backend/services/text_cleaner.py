"""
text_cleaner.py
~~~~~~~~~~~~~~~

A dedicated text cleaner that removes images, links, and HTML from raw
README / user-provided description text. This is intended to be the very
first preprocessing step before any LLM or classifier pipeline.

Supported removals:
- Markdown images:   !\[alt\](url)  →  removed entirely
- Markdown links:   \[text\](url)   →  keeps only the text part
- HTML tags:        <...>           →  stripped
- Bare URLs:        http://... or   →  removed
  https://...
- Normalizes whitespace and collapses multiple newlines.
"""

import re


def clean_text(raw: str) -> str:
    """
    Remove images, links, and HTML from raw text.

    This is intentionally a pure function with no side-effects —
    callers can invoke it once at pipeline start or per-chunk as needed.
    """
    text = raw

    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()