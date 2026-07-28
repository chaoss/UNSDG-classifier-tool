from markdowncleaner import MarkdownCleaner, CleanerOptions
from markdowncleaner.config.loader import CleaningPatterns
from pathlib import Path

options = CleanerOptions()
options.remove_short_lines = False      # CRITICAL — don't strip short lines
options.remove_sections = False         # default sections don't match READMEs
options.remove_references_heuristically = False  # no references in READMEs
options.remove_footnotes_in_text = False         # no footnotes in READMEs
options.contract_empty_lines = True     # keep this
options.fix_encoding_mojibake = True    # keep this — helps with multilingual READMEs
options.normalize_quotation_symbols = True  # keep this

cleaner = MarkdownCleaner(options=options)

def clean_readme(raw_readme: str) -> str:
    cleaned = cleaner.clean_markdown_string(raw_readme)
    return cleaned

import re

def clean_github_readme(raw_readme: str) -> str:
    # markdowncleaner first
    cleaned = cleaner.clean_markdown_string(raw_readme)
    
    # Then GitHub-specific patterns markdowncleaner misses
    cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)   # code blocks
    cleaned = re.sub(r'`[^`]*`', '', cleaned)           # inline code
    cleaned = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned)   # images/badges
    cleaned = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', cleaned)  # links→text
    cleaned = re.sub(r'<[^>]+>', '', cleaned)           # HTML tags
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    return cleaned.strip()