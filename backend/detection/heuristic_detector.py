import re
from typing import List, Set
from backend.detection.base import CodeMixDetector
from backend.detection.models import DetectionResult, LanguageSpan


# ---------------------------------------------------------------------------
# Romanized Tamil/Hindi keyword lexicons
# These are high-signal words that are clearly NOT English, covering common
# verbs, pronouns, question words, and suffixes used in Tanglish / Hinglish.
# ---------------------------------------------------------------------------

ROMANIZED_TAMIL_WORDS: Set[str] = {
    # Pronouns / possessives
    "ennoda", "enakku", "naan", "neenga", "avan", "aval", "avanga", "namma",
    # Question words
    "eppadi", "eppo", "enna", "enga", "ethu", "yaarku",
    # Common verbs / suffixes (Romanized Tamil verb endings)
    "panrathu", "panrom", "pannu", "sollu", "sollunga", "paarunga", "theriyuma",
    "iruku", "irukkum", "varum", "poiduchu", "aagum", "seiyalam",
    # Conjunctions / connectors
    "aana", "illa", "illama", "aachu",
    # Common postpositional / locative markers
    "kita", "kku", "oda", "la", "ku",
    # Other common colloquial words
    "panna", "evlo", "kudukanum", "venuma",
}

ROMANIZED_HINDI_WORDS: Set[str] = {
    # Pronouns
    "mere", "mera", "meri", "mujhe", "humara", "aap", "tum", "unka", "unke",
    # Question words
    "kaise", "kab", "kahan", "kyun", "kya", "kaisa",
    # Common verbs / auxiliaries
    "karu", "karna", "karein", "karo", "kar", "hain", "hai", "tha", "thi",
    "chahiye", "milega", "milegi", "sakta", "sakti", "chahta",
    # Connectors / postpositions
    "par", "mein", "se", "ko", "ka", "ki", "ke", "liye", "bhi", "aur",
}


def _tokenize_lower(text: str) -> Set[str]:
    """Extract lowercased alphabetic tokens from text."""
    return set(re.findall(r'[a-z]+', text.lower()))


class HeuristicRegexDetector(CodeMixDetector):
    """
    A practical heuristic detector for code-mix detection supporting:
    1. Unicode-script detection: Devanagari (Hindi) and Tamil native script.
    2. Romanized lexicon detection: Tanglish and Hinglish written in Latin script.

    Strategy:
    - First check for native-script Unicode blocks (high precision).
    - Then check for Romanized regional-language keywords (catches Tanglish/Hinglish).
    - Fall back to treating remaining Latin tokens as English.
    """

    def __init__(self):
        self.devanagari_re = re.compile(r'[\u0900-\u097F]+')
        self.tamil_re = re.compile(r'[\u0B80-\u0BFF]+')
        self.latin_re = re.compile(r'[a-zA-Z]+')

    def _detect_word_lang(self, word: str) -> str:
        """Assign a language to a single word based on Unicode block."""
        if self.devanagari_re.search(word):
            return "Hindi"
        elif self.tamil_re.search(word):
            return "Tamil"
        elif self.latin_re.search(word):
            return "English"
        return "Unknown"

    def _check_romanized(self, query: str):
        """
        Check query tokens against Romanized Tamil/Hindi lexicons.
        Returns (is_romanized_tamil, is_romanized_hindi).
        """
        tokens = _tokenize_lower(query)
        has_tamil = bool(tokens & ROMANIZED_TAMIL_WORDS)
        has_hindi = bool(tokens & ROMANIZED_HINDI_WORDS)
        return has_tamil, has_hindi

    def detect(self, query: str) -> DetectionResult:
        if not query.strip():
            return DetectionResult(
                is_code_mixed=False,
                languages=["Unknown"],
                language_spans=[],
                confidence=1.0
            )

        # --- Pass 1: Romanized lexicon check (catches Tanglish / Hinglish) ---
        is_romanized_tamil, is_romanized_hindi = self._check_romanized(query)

        # If any Romanized regional language is detected alongside Latin text,
        # the query is code-mixed. We don't do span-level analysis for Romanized
        # queries because every token is in Latin script.
        if is_romanized_tamil or is_romanized_hindi:
            langs = ["English"]  # Base language is English (mixed in)
            if is_romanized_tamil:
                langs.append("Tamil")
            if is_romanized_hindi:
                langs.append("Hindi")
            return DetectionResult(
                is_code_mixed=True,
                languages=langs,
                language_spans=[],  # Span attribution not possible for Romanized
                confidence=0.85,
            )

        # --- Pass 2: Unicode script analysis (native script mixing) ---
        spans: List[LanguageSpan] = []
        for match in re.finditer(r'\w+', query):
            word = match.group()
            start, end = match.span()
            lang = self._detect_word_lang(word)

            if spans and spans[-1].language == lang:
                spans[-1].end = end
                spans[-1].text = query[spans[-1].start:end]
            else:
                spans.append(LanguageSpan(
                    start=start,
                    end=end,
                    language=lang,
                    text=query[start:end]
                ))

        detected_langs = list(set(s.language for s in spans if s.language != "Unknown"))
        if not detected_langs:
            detected_langs = ["Unknown"]

        is_mixed = len(detected_langs) > 1
        confidence = 0.95 if is_mixed else 0.70

        return DetectionResult(
            is_code_mixed=is_mixed,
            languages=detected_langs,
            language_spans=spans,
            confidence=confidence
        )
