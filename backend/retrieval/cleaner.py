import re
import unicodedata

# Regex for common unicode spaces and zero-width artifacts
_ZERO_WIDTH_CHARS = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060]")
_REPEATED_DIVIDERS = re.compile(r"^[ \t]*[-=_*~]{5,}[ \t]*$", re.MULTILINE)
_MULTIPLE_NEWLINES = re.compile(r"\n{3,}")
_HORIZONTAL_SPACES = re.compile(r"[^\S\r\n]+")


def clean_text(text: str) -> str:
    """
    Clean and normalize raw extracted document text without aggressive rewriting.

    Actions performed:
    1. Standardizes carriage returns to unix newlines.
    2. Strips zero-width and invisible control characters.
    3. Normalizes non-breaking and unusual unicode whitespace to standard spaces.
    4. Removes decorative page dividers and form feed artifacts (\x0c).
    5. Strips trailing whitespace per line and collapses excessive blank lines.
    6. Preserves exact casing, multilingual scripts, and punctuation.
    """
    if not text:
        return ""

    # Normalize unicode to standard NFKC representation (decomposes compatibility forms)
    text = unicodedata.normalize("NFKC", text)

    # Remove form feed characters (common in PDF extraction page breaks)
    text = text.replace("\x0c", "\n")

    # Standardize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove zero-width and invisible characters
    text = _ZERO_WIDTH_CHARS.sub("", text)

    # Remove repeated decorative dividers
    text = _REPEATED_DIVIDERS.sub("", text)

    # Remove non-printable control characters except tab and newline
    text = "".join(
        ch for ch in text if ch in ("\t", "\n") or (unicodedata.category(ch)[0] != "C")
    )

    # Process line by line to preserve structure while trimming excess whitespace
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # Collapse multiple horizontal spaces/tabs into a single space
        line = _HORIZONTAL_SPACES.sub(" ", line).strip()
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Collapse 3 or more consecutive newlines into 2 (clean paragraph break)
    text = _MULTIPLE_NEWLINES.sub("\n\n", text)

    return text.strip()
