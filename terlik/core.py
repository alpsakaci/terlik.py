import threading
import time
from typing import Dict, List, Optional
from .types import (
    TerlikOptions,
    DetectOptions,
    CleanOptions,
    MatchResult,
    Mode,
    MaskStyle,
    Severity,
    Category,
)
from .lang.types import LanguageConfig
from .dictionary.core import Dictionary
from .dictionary.schema import validate_dictionary, merge_dictionaries
from .detector import Detector
from .cleaner import clean_text
from .utils import validate_input, MAX_INPUT_LENGTH
from .normalizer import create_normalizer


class TerlikCore:
    def __init__(
        self, lang_config: LanguageConfig, options: Optional[TerlikOptions] = None
    ):
        opts = options or TerlikOptions()

        self.language = lang_config.locale
        self.mode = opts.mode
        self.mask_style = opts.mask_style
        self.enable_fuzzy = opts.enable_fuzzy

        if opts.fuzzy_threshold < 0 or opts.fuzzy_threshold > 1:
            raise ValueError(
                f"fuzzy_threshold must be between 0 and 1, got {opts.fuzzy_threshold}"
            )
        self.fuzzy_threshold = opts.fuzzy_threshold

        self.fuzzy_algorithm = opts.fuzzy_algorithm

        if opts.max_length < 1:
            raise ValueError(f"max_length must be at least 1, got {opts.max_length}")
        self.max_length = opts.max_length

        self.replace_mask = opts.replace_mask
        self.disable_leet_decode = opts.disable_leet_decode
        self.disable_compound = opts.disable_compound
        self.min_severity = opts.min_severity
        self.exclude_categories = opts.exclude_categories

        normalize_fn = create_normalizer(
            locale=lang_config.locale,
            char_map=lang_config.char_map,
            leet_map=lang_config.leet_map,
            number_expansions=lang_config.number_expansions,
        )
        safe_normalize_fn = create_normalizer(
            locale=lang_config.locale,
            char_map=lang_config.char_map,
            leet_map={},
            number_expansions=[],
        )

        dict_data = lang_config.dictionary
        if opts.extend_dictionary:
            validated_ext = validate_dictionary(opts.extend_dictionary)
            dict_data = merge_dictionaries(dict_data, validated_ext)

        self.dictionary = Dictionary(
            data=dict_data,
            custom_words=opts.custom_list,
            custom_whitelist=opts.whitelist,
        )

        has_custom_dict = bool(
            opts.custom_list or opts.whitelist or opts.extend_dictionary
        )

        self.detector = Detector(
            dictionary=self.dictionary,
            normalize_fn=normalize_fn,
            safe_normalize_fn=safe_normalize_fn,
            locale=lang_config.locale,
            char_classes=lang_config.char_classes,
            cache_key=None if has_custom_dict else lang_config.locale,
        )

        if opts.background_warmup:

            def warmup():
                self.detector.compile()
                self.contains_profanity("warmup")

            threading.Thread(target=warmup, daemon=True).start()

    def contains_profanity(
        self, text: str, options: Optional[DetectOptions] = None
    ) -> bool:
        input_text = validate_input(text, self.max_length)
        if not input_text:
            return False
        matches = self.detector.detect(input_text, self._merge_detect_options(options))
        return len(matches) > 0

    def get_matches(
        self, text: str, options: Optional[DetectOptions] = None
    ) -> List[MatchResult]:
        input_text = validate_input(text, self.max_length)
        if not input_text:
            return []
        return self.detector.detect(input_text, self._merge_detect_options(options))

    def clean(self, text: str, options: Optional[CleanOptions] = None) -> str:
        input_text = validate_input(text, self.max_length)
        if not input_text:
            return input_text

        merged_opts = self._merge_detect_options(options)
        matches = self.detector.detect(input_text, merged_opts)

        style = (
            options.mask_style if options and options.mask_style else self.mask_style
        )
        replace_mask = (
            options.replace_mask
            if options and options.replace_mask
            else self.replace_mask
        )

        return clean_text(input_text, matches, style, replace_mask)

    def add_words(self, words: List[str]) -> None:
        self.dictionary.add_words(words)
        self.detector.recompile()

    def remove_words(self, words: List[str]) -> None:
        self.dictionary.remove_words(words)
        self.detector.recompile()

    def get_patterns(self):
        return self.detector.get_patterns()

    def _merge_detect_options(self, options: Optional[DetectOptions]) -> DetectOptions:
        opts = options or DetectOptions()
        return DetectOptions(
            mode=opts.mode if opts.mode is not None else self.mode,
            enable_fuzzy=(
                opts.enable_fuzzy
                if opts.enable_fuzzy is not None
                else self.enable_fuzzy
            ),
            fuzzy_threshold=(
                opts.fuzzy_threshold
                if opts.fuzzy_threshold is not None
                else self.fuzzy_threshold
            ),
            fuzzy_algorithm=(
                opts.fuzzy_algorithm
                if opts.fuzzy_algorithm is not None
                else self.fuzzy_algorithm
            ),
            disable_leet_decode=(
                opts.disable_leet_decode
                if opts.disable_leet_decode is not None
                else self.disable_leet_decode
            ),
            disable_compound=(
                opts.disable_compound
                if opts.disable_compound is not None
                else self.disable_compound
            ),
            min_severity=(
                opts.min_severity
                if opts.min_severity is not None
                else self.min_severity
            ),
            exclude_categories=(
                opts.exclude_categories
                if opts.exclude_categories is not None
                else self.exclude_categories
            ),
        )
