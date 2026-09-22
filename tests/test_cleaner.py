import pytest
from backend.retrieval.cleaner import clean_text


def test_clean_text_basic_whitespace():
    raw = "  This   is    a   test sentence.   \n\n\n\nAnother line.  "
    cleaned = clean_text(raw)
    assert cleaned == "This is a test sentence.\n\nAnother line."


def test_clean_text_carriage_returns():
    raw = "Line 1\r\nLine 2\rLine 3\nLine 4"
    cleaned = clean_text(raw)
    assert "Line 1\nLine 2\nLine 3\nLine 4" == cleaned


def test_clean_text_zero_width_and_dividers():
    raw = (
        "Heading\n"
        "------------------------------------\n"
        "Content with zero\u200bwidth character.\n"
        "====================================\n"
        "End of section."
    )
    cleaned = clean_text(raw)
    assert "\u200b" not in cleaned
    assert "----------------" not in cleaned
    assert "================" not in cleaned
    assert "Heading" in cleaned
    assert "Content with zerowidth character." in cleaned
    assert "End of section." in cleaned


def test_clean_text_multilingual_preservation():
    raw = "Admission eligibility: न्यूनतम CGPA 3.0 hona chahiye (75% aggregate)!"
    cleaned = clean_text(raw)
    # Ensure Devanagari characters, English, punctuation, and casing are preserved
    assert cleaned == raw


def test_clean_text_empty():
    assert clean_text("") == ""
    assert clean_text("   \n\n   \t  ") == ""
