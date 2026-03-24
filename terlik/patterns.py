import re
from typing import Dict, List, Optional
from .types import CompiledPattern, WordEntry, Category

# Explicit Latin + Turkish + European letter/digit range.
# À = U+00C0, ɏ = U+024F
WORD_CHAR = r"a-zA-Z0-9À-ɏ"
SEPARATOR = r"[^" + WORD_CHAR + r"]{0,3}"
WORD_BOUNDARY_BEHIND = r"(?<![" + WORD_CHAR + r"])"
WORD_BOUNDARY_AHEAD = r"(?!=[" + WORD_CHAR + r"])"  # Wait, ahead should be (?![...])
WORD_BOUNDARY_AHEAD = r"(?![" + WORD_CHAR + r"])"

MAX_PATTERN_LENGTH = 20000
MAX_SUFFIX_CHAIN = 2
REGEX_TIMEOUT_MS = 250


def char_to_pattern(ch: str, char_classes: Dict[str, str]) -> str:
    cls = char_classes.get(ch.lower())
    if cls:
        return f"{cls}+"
    return re.escape(ch) + "+"


def word_to_pattern(word: str, char_classes: Dict[str, str], normalize_fn) -> str:
    normalized = normalize_fn(word)
    parts = [char_to_pattern(ch, char_classes) for ch in normalized]
    return SEPARATOR.join(parts)


def char_to_literal_pattern(ch: str) -> str:
    return re.escape(ch) + "+"


def build_suffix_group(suffixes: List[str], char_classes: Dict[str, str]) -> str:
    if not suffixes:
        return ""

    suffix_patterns = []
    for suffix in suffixes:
        parts = [char_to_literal_pattern(ch) for ch in suffix]
        suffix_patterns.append(SEPARATOR.join(parts))

    suffix_patterns.sort(key=len, reverse=True)
    return f"(?:{SEPARATOR}(?:{'|'.join(suffix_patterns)}))"


def compile_patterns(
    entries: Dict[str, WordEntry],
    suffixes: Optional[List[str]],
    char_classes: Dict[str, str],
    normalize_fn,
) -> List[CompiledPattern]:
    patterns: List[CompiledPattern] = []

    suffix_group = build_suffix_group(suffixes, char_classes) if suffixes else ""

    for entry in entries.values():
        all_forms = [entry.root] + entry.variants

        # Sort by length descending, remove duplicates, filter empty
        sorted_forms = []
        seen = set()
        for w in all_forms:
            n = normalize_fn(w)
            if len(n) > 0 and n not in seen:
                seen.add(n)
                sorted_forms.append(n)

        sorted_forms.sort(key=len, reverse=True)

        use_suffix = entry.suffixable and bool(suffix_group)
        pattern_str = ""

        if use_suffix:
            form_patterns = [
                word_to_pattern(w, char_classes, normalize_fn) for w in sorted_forms
            ]
            combined = "|".join(form_patterns)
            pattern_str = f"{WORD_BOUNDARY_BEHIND}(?:{combined}){suffix_group}{{0,{MAX_SUFFIX_CHAIN}}}{WORD_BOUNDARY_AHEAD}"
        elif suffix_group:
            MIN_VARIANT_SUFFIX_LEN = 4
            strict_forms = []
            suffixable_forms = []
            for w in sorted_forms:
                if len(w) >= MIN_VARIANT_SUFFIX_LEN:
                    suffixable_forms.append(
                        word_to_pattern(w, char_classes, normalize_fn)
                    )
                else:
                    strict_forms.append(word_to_pattern(w, char_classes, normalize_fn))

            parts = []
            if suffixable_forms:
                parts.append(
                    f"(?:{'|'.join(suffixable_forms)}){suffix_group}{{0,{MAX_SUFFIX_CHAIN}}}"
                )
            if strict_forms:
                parts.append(f"(?:{'|'.join(strict_forms)})")

            pattern_str = (
                f"{WORD_BOUNDARY_BEHIND}(?:{'|'.join(parts)}){WORD_BOUNDARY_AHEAD}"
            )
        else:
            form_patterns = [
                word_to_pattern(w, char_classes, normalize_fn) for w in sorted_forms
            ]
            combined = "|".join(form_patterns)
            pattern_str = f"{WORD_BOUNDARY_BEHIND}(?:{combined}){WORD_BOUNDARY_AHEAD}"

        if len(pattern_str) > MAX_PATTERN_LENGTH:
            form_patterns = [
                word_to_pattern(w, char_classes, normalize_fn) for w in sorted_forms
            ]
            combined = "|".join(form_patterns)
            pattern_str = f"{WORD_BOUNDARY_BEHIND}(?:{combined}){WORD_BOUNDARY_AHEAD}"

        try:
            regex = re.compile(pattern_str, re.IGNORECASE)
            patterns.append(
                CompiledPattern(
                    root=entry.root,
                    severity=entry.severity,
                    category=entry.category,
                    regex=regex,
                    variants=entry.variants,
                )
            )
        except Exception as e:
            if use_suffix:
                try:
                    fallback_forms = "|".join(
                        [
                            word_to_pattern(w, char_classes, normalize_fn)
                            for w in sorted_forms
                        ]
                    )
                    fallback_pattern = f"{WORD_BOUNDARY_BEHIND}(?:{fallback_forms}){WORD_BOUNDARY_AHEAD}"
                    regex = re.compile(fallback_pattern, re.IGNORECASE)
                    patterns.append(
                        CompiledPattern(
                            root=entry.root,
                            severity=entry.severity,
                            category=entry.category,
                            regex=regex,
                            variants=entry.variants,
                        )
                    )
                except Exception:
                    pass
            else:
                pass

    return patterns
