import re
import unicodedata
from typing import Dict, List, Optional, Callable, Tuple

INVISIBLE_CHARS = re.compile(
    r"[\u200B\u200C\u200D\u200E\u200F\uFEFF\u00AD\u034F\u2060\u2061\u2062\u2063\u2064\u180E]"
)

COMBINING_MARKS = re.compile(r"[\u0300-\u036f]")

CYRILLIC_CONFUSABLES: Dict[str, str] = {
    "\u0430": "a",  # Cyrillic а → Latin a
    "\u0441": "c",  # Cyrillic с → Latin c
    "\u0435": "e",  # Cyrillic е → Latin e
    "\u0456": "i",  # Cyrillic і → Latin i
    "\u043e": "o",  # Cyrillic о → Latin o
    "\u0440": "p",  # Cyrillic р → Latin p
    "\u0443": "u",  # Cyrillic у → Latin u
    "\u0445": "x",  # Cyrillic х → Latin x
}


def replace_from_map(text: str, char_map: Dict[str, str]) -> str:
    return "".join(char_map.get(ch, ch) for ch in text)


def build_number_expander(
    expansions: List[Tuple[str, str]],
) -> Optional[Callable[[str], str]]:
    if not expansions:
        return None

    lookup = dict(expansions)
    escaped_keys = [re.escape(k) for k, v in expansions]
    # Word character equivalent in JS implementation is [a-zA-ZÀ-ɏ]
    # We'll use the same positive lookbehind/lookahead.
    pattern = (
        r"(?<=[a-zA-ZÀ-ɏ])" r"(" + "|".join(escaped_keys) + r")" r"(?=[a-zA-ZÀ-ɏ])"
    )
    regex = re.compile(pattern)

    def expand(text: str) -> str:
        return regex.sub(lambda m: lookup.get(m.group(0), m.group(0)), text)

    return expand


def remove_punctuation(text: str) -> str:
    # Remove punctuation enclosed between word characters
    # Replaces /(?<=[a-zA-ZÀ-ɏ])[.\-_*,;:\!\?]+(?=[a-zA-ZÀ-ɏ])/g
    return re.sub(r"(?<=[a-zA-ZÀ-ɏ])[.\-_*,;:!?]+(?=[a-zA-ZÀ-ɏ])", "", text)


def collapse_repeats(text: str) -> str:
    # /(.)\1{2,}/g -> "$1"
    return re.sub(r"(.)\1{2,}", r"\1", text)


def trim_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def create_normalizer(
    locale: str,
    char_map: Dict[str, str],
    leet_map: Dict[str, str],
    number_expansions: Optional[List[Tuple[str, str]]] = None,
) -> Callable[[str], str]:
    expand_numbers = (
        build_number_expander(number_expansions) if number_expansions else None
    )

    # Handle Turkish special cases for lowercasing to avoid I/ı i/İ issues
    is_turkish = locale.lower() == "tr"

    def normalize(text: str) -> str:
        result = text
        result = INVISIBLE_CHARS.sub("", result)

        # NFKD decompose
        result = unicodedata.normalize("NFKD", result)
        result = COMBINING_MARKS.sub("", result)

        if is_turkish:
            result = result.replace("I", "ı").replace("İ", "i")

        result = result.lower()

        result = replace_from_map(result, CYRILLIC_CONFUSABLES)
        result = replace_from_map(result, char_map)

        if expand_numbers:
            result = expand_numbers(result)

        result = replace_from_map(result, leet_map)
        result = remove_punctuation(result)
        result = collapse_repeats(result)
        result = trim_whitespace(result)

        return result

    return normalize


# Turkish defaults for backward compat / pure shortcut
TURKISH_CHAR_MAP = {
    "ç": "c",
    "Ç": "c",
    "ğ": "g",
    "Ğ": "g",
    "ı": "i",
    "İ": "i",
    "ö": "o",
    "Ö": "o",
    "ş": "s",
    "Ş": "s",
    "ü": "u",
    "Ü": "u",
}

LEET_MAP = {
    "0": "o",
    "1": "i",
    "2": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "6": "g",
    "7": "t",
    "8": "b",
    "9": "g",
    "@": "a",
    "$": "s",
    "!": "i",
}

TR_NUMBER_MAP = [
    ("100", "yuz"),
    ("50", "elli"),
    ("10", "on"),
    ("2", "iki"),
]

_turkish_normalize = create_normalizer("tr", TURKISH_CHAR_MAP, LEET_MAP, TR_NUMBER_MAP)


def normalize(text: str) -> str:
    return _turkish_normalize(text)
