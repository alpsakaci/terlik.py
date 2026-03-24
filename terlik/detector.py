import time
import re
from typing import Dict, List, Set, Optional, Callable
from .types import (
    CompiledPattern,
    DetectOptions,
    MatchResult,
    Category,
    Mode,
    SEVERITY_ORDER,
)
from .dictionary.core import Dictionary
from .patterns import compile_patterns, REGEX_TIMEOUT_MS
from .fuzzy import get_fuzzy_matcher


class Detector:
    # Static cache for compiled patterns
    _pattern_cache: Dict[str, List[CompiledPattern]] = {}

    def __init__(
        self,
        dictionary: Dictionary,
        normalize_fn: Callable[[str], str],
        safe_normalize_fn: Callable[[str], str],
        locale: str,
        char_classes: Dict[str, str],
        cache_key: Optional[str] = None,
    ):
        self.dictionary = dictionary
        self.normalize_fn = normalize_fn
        self.safe_normalize_fn = safe_normalize_fn
        self.locale = locale
        self.char_classes = char_classes
        self.cache_key = cache_key
        self._patterns: Optional[List[CompiledPattern]] = None
        self.normalized_word_set: Set[str] = set()
        self.normalized_word_to_root: Dict[str, str] = {}
        self._build_normalized_lookup()

    def _ensure_compiled(self) -> List[CompiledPattern]:
        if self._patterns is None:
            if self.cache_key:
                cached = Detector._pattern_cache.get(self.cache_key)
                if cached is not None:
                    self._patterns = cached
                    return self._patterns

            self._patterns = compile_patterns(
                self.dictionary.get_entries(),
                self.dictionary.get_suffixes(),
                self.char_classes,
                self.normalize_fn,
            )

            if self.cache_key:
                Detector._pattern_cache[self.cache_key] = self._patterns

        return self._patterns

    def compile(self) -> None:
        self._ensure_compiled()

    def recompile(self) -> None:
        self.cache_key = None
        self._patterns = compile_patterns(
            self.dictionary.get_entries(),
            self.dictionary.get_suffixes(),
            self.char_classes,
            self.normalize_fn,
        )
        self._build_normalized_lookup()

    def _build_normalized_lookup(self) -> None:
        self.normalized_word_set.clear()
        self.normalized_word_to_root.clear()
        for word in self.dictionary.get_all_words():
            n = self.normalize_fn(word)
            self.normalized_word_set.add(n)
            self.normalized_word_to_root[n] = word

    def get_patterns(self) -> Dict[str, re.Pattern]:
        return {p.root: p.regex for p in self._ensure_compiled()}

    def detect(
        self, text: str, options: Optional[DetectOptions] = None
    ) -> List[MatchResult]:
        opts = options or DetectOptions()
        mode: Mode = opts.mode or "balanced"
        results: List[MatchResult] = []
        whitelist = self.dictionary.get_whitelist()

        if mode == "strict":
            self._detect_strict(text, whitelist, results)
        else:
            self._detect_pattern(text, whitelist, results, opts)

        if mode == "loose" or opts.enable_fuzzy:
            threshold = (
                opts.fuzzy_threshold if opts.fuzzy_threshold is not None else 0.8
            )
            algorithm = (
                opts.fuzzy_algorithm
                if opts.fuzzy_algorithm is not None
                else "levenshtein"
            )
            self._detect_fuzzy(text, whitelist, results, threshold, algorithm)

        filtered = self._apply_strictness_filters(results, opts)
        return self._deduplicate_results(filtered)

    def _apply_strictness_filters(
        self, results: List[MatchResult], options: DetectOptions
    ) -> List[MatchResult]:
        min_sev = options.min_severity
        ex_cats = options.exclude_categories

        if not min_sev and not ex_cats:
            return results

        filtered = []
        for r in results:
            if min_sev and SEVERITY_ORDER[r.severity] < SEVERITY_ORDER[min_sev]:
                continue
            if ex_cats and r.category and r.category in ex_cats:
                continue
            filtered.append(r)
        return filtered

    def _detect_strict(
        self, text: str, whitelist: Set[str], results: List[MatchResult]
    ) -> None:
        normalized = self.normalize_fn(text)
        words = re.split(r"\s+", normalized)
        original_words = re.split(r"\s+", text)

        char_index = 0
        for wi, orig_word in enumerate(original_words):
            norm_word = words[wi] if wi < len(words) else ""

            if not norm_word:
                char_index += len(orig_word) + 1
                continue

            if norm_word in whitelist:
                char_index += len(orig_word) + 1
                continue

            if norm_word in self.normalized_word_set:
                dict_word = self.normalized_word_to_root[norm_word]
                entry = self.dictionary.find_root_for_word(dict_word)
                if entry:
                    results.append(
                        MatchResult(
                            word=orig_word,
                            root=entry.root,
                            index=char_index,
                            severity=entry.severity,
                            category=entry.category,
                            method="exact",
                        )
                    )

            char_index += len(orig_word) + 1

    def _detect_pattern(
        self,
        text: str,
        whitelist: Set[str],
        results: List[MatchResult],
        options: DetectOptions,
    ) -> None:
        active_norm_fn = (
            self.safe_normalize_fn if options.disable_leet_decode else self.normalize_fn
        )

        lower_text = (
            text.lower()
        )  # JS does locale-lower, Python lower is sufficient or we handle custom
        if self.locale == "tr":
            lower_text = text.replace("I", "ı").replace("İ", "i").lower()

        self._run_patterns(
            lower_text, text, whitelist, results, lower_text != text, options
        )

        normalized_text = active_norm_fn(text)
        if normalized_text != lower_text and len(normalized_text) > 0:
            self._run_patterns(normalized_text, text, whitelist, results, True, options)

        if not options.disable_compound:
            decompound = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
            decompound = re.sub(r"([A-Z]{2,})([a-z])", r"\1 \2", decompound)
            if decompound != text:
                decompound_norm = active_norm_fn(decompound)
                if decompound_norm != normalized_text and decompound_norm != lower_text:
                    self._run_patterns(
                        decompound_norm, text, whitelist, results, True, options
                    )

    def _run_patterns(
        self,
        search_text: str,
        original_text: str,
        whitelist: Set[str],
        results: List[MatchResult],
        is_normalized: bool,
        options: DetectOptions,
    ) -> None:
        existing_indices = {r.index for r in results}
        patterns = self._ensure_compiled()
        min_sev = options.min_severity
        ex_cats = options.exclude_categories

        for pattern in patterns:
            if min_sev and SEVERITY_ORDER[pattern.severity] < SEVERITY_ORDER[min_sev]:
                continue
            if ex_cats and pattern.category and pattern.category in ex_cats:
                continue

            pattern_start = time.time()

            for match in pattern.regex.finditer(search_text):
                matched_text = match.group(0)
                match_index = match.start()

                # Whitelist checks
                if matched_text in whitelist:
                    continue
                normalized_match = self.normalize_fn(matched_text)
                if normalized_match in whitelist:
                    continue

                surrounding = self._get_surrounding_word(
                    search_text, match_index, len(matched_text)
                )
                if surrounding in whitelist:
                    continue
                normalized_surrounding = self.normalize_fn(surrounding)
                if normalized_surrounding in whitelist:
                    continue

                if is_normalized:
                    mapped = self._map_normalized_to_original(
                        original_text, match_index, matched_text
                    )
                    if mapped:
                        mapped_word, mapped_index = mapped
                        if mapped_word.lower() in whitelist:
                            continue
                        if re.search(r"\d+$", mapped_word) and re.match(
                            r"^[^\d]+\d+$", mapped_word
                        ):
                            continue
                        if mapped_index not in existing_indices:
                            results.append(
                                MatchResult(
                                    word=mapped_word,
                                    root=pattern.root,
                                    index=mapped_index,
                                    severity=pattern.severity,
                                    category=pattern.category,
                                    method="pattern",
                                )
                            )
                            existing_indices.add(mapped_index)
                else:
                    if match_index not in existing_indices:
                        results.append(
                            MatchResult(
                                word=matched_text,
                                root=pattern.root,
                                index=match_index,
                                severity=pattern.severity,
                                category=pattern.category,
                                method="pattern",
                            )
                        )
                        existing_indices.add(match_index)

                if (time.time() - pattern_start) * 1000 > REGEX_TIMEOUT_MS:
                    break

    def _map_normalized_to_original(
        self, original_text: str, norm_index: int, norm_match: str
    ):
        orig_words = re.split(r"(\s+)", original_text)
        norm_offset = 0
        orig_offset = 0

        for segment in orig_words:
            if re.match(r"^\s+$", segment):
                norm_offset += 1
                orig_offset += len(segment)
                continue

            norm_word = self.normalize_fn(segment)
            norm_end = norm_offset + len(norm_word)

            if norm_index >= norm_offset and norm_index < norm_end:
                return (segment, orig_offset)

            norm_offset = norm_end
            orig_offset += len(segment)

        return None

    def _detect_fuzzy(
        self,
        text: str,
        whitelist: Set[str],
        existing_results: List[MatchResult],
        threshold: float,
        algorithm: str,
    ) -> None:
        normalized = self.normalize_fn(text)
        norm_words = re.split(r"\s+", normalized)
        orig_words = re.split(r"\s+", text)
        matcher = get_fuzzy_matcher(algorithm)
        existing_indices = {r.index for r in existing_results}
        start_time = time.time()

        char_index = 0
        for wi, orig_word in enumerate(orig_words):
            if (time.time() - start_time) * 1000 > REGEX_TIMEOUT_MS:
                break

            word = norm_words[wi] if wi < len(norm_words) else ""

            if len(word) < 3 or word in whitelist:
                char_index += len(orig_word) + 1
                continue

            for norm_dict in self.normalized_word_set:
                if len(norm_dict) < 3:
                    continue

                similarity = matcher(word, norm_dict)
                if similarity >= threshold:
                    if char_index not in existing_indices:
                        dict_word = self.normalized_word_to_root[norm_dict]
                        entry = self.dictionary.find_root_for_word(dict_word)
                        if entry:
                            existing_results.append(
                                MatchResult(
                                    word=orig_word,
                                    root=entry.root,
                                    index=char_index,
                                    severity=entry.severity,
                                    category=entry.category,
                                    method="fuzzy",
                                )
                            )
                            existing_indices.add(char_index)
                    break

            char_index += len(orig_word) + 1

    def _get_surrounding_word(self, text: str, index: int, length: int) -> str:
        start = index
        end = index + length

        while start > 0 and re.match(r"[a-zA-ZÀ-ɏ]", text[start - 1]):
            start -= 1
        while end < len(text) and re.match(r"[a-zA-ZÀ-ɏ]", text[end]):
            end += 1

        return text[start:end]

    def _deduplicate_results(self, results: List[MatchResult]) -> List[MatchResult]:
        seen: Dict[int, MatchResult] = {}
        for r in results:
            existing = seen.get(r.index)
            if not existing or len(r.word) > len(existing.word):
                seen[r.index] = r

        return sorted(seen.values(), key=lambda x: x.index)
