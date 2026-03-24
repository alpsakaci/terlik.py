from typing import List
from .types import MaskStyle, MatchResult


def mask_stars(word: str) -> str:
    return "*" * len(word)


def mask_partial(word: str) -> str:
    if len(word) <= 2:
        return "*" * len(word)
    return word[0] + "*" * (len(word) - 2) + word[-1]


def mask_replace(replace_mask: str) -> str:
    return replace_mask


def apply_mask(word: str, style: MaskStyle, replace_mask: str) -> str:
    """
    Applies a mask to a single word using the specified style.
    """
    if style == "stars":
        return mask_stars(word)
    elif style == "partial":
        return mask_partial(word)
    elif style == "replace":
        return mask_replace(replace_mask)
    return word


def clean_text(
    text: str, matches: List[MatchResult], style: MaskStyle, replace_mask: str
) -> str:
    """
    Replaces all matched profanity in the text with masked versions.
    Processes matches from end to start to preserve character indices.
    """
    if not matches:
        return text

    # Sort by index descending so we can replace from end to start
    sorted_matches = sorted(matches, key=lambda m: m.index, reverse=True)

    result = text
    for match in sorted_matches:
        masked = apply_mask(match.word, style, replace_mask)
        # Slicing safely to replace exactly the match.word
        start = match.index
        end = match.index + len(match.word)
        result = result[:start] + masked + result[end:]

    return result
