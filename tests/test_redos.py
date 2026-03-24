import pytest
import time
from terlik.detector import Detector
from terlik.dictionary.core import Dictionary
from terlik.lang.tr.config import config as trConfig
from terlik.normalizer import create_normalizer
from terlik.patterns import REGEX_TIMEOUT_MS


def create_detector():
    normalize_fn = create_normalizer(
        locale=trConfig.locale,
        char_map=trConfig.char_map,
        leet_map=trConfig.leet_map,
        number_expansions=trConfig.number_expansions,
    )
    safe_normalize_fn = create_normalizer(
        locale=trConfig.locale,
        char_map=trConfig.char_map,
        leet_map={},
        number_expansions=[],
    )
    dictionary = Dictionary(trConfig.dictionary)
    return Detector(
        dictionary,
        normalize_fn,
        safe_normalize_fn,
        trConfig.locale,
        trConfig.char_classes,
    )


MAX_DETECT_MS = REGEX_TIMEOUT_MS * 120


class TestReDos:
    @pytest.fixture(scope="class")
    def tr_detector(self):
        detector = create_detector()
        # Warmup
        from terlik.types import DetectOptions

        detector.detect("warmup text siktir", DetectOptions())
        return detector

    def test_constants(self):
        assert REGEX_TIMEOUT_MS == 250

    def test_repeated_separators(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "a" + "." * 100 + "b" + "." * 100 + "c"
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_long_overlap(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "@" * 50
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_max_length(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "test" * 2500
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_leet_separator_mixed(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "$" + "..." * 20 + "1" + "..." * 20 + "k"
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_mixed_overlap_sequence(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "@$!|+#€" * 10
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_unicode_flood(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "€¢©®™" * 20
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_near_match_prefix_flood(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "s" * 50 + "xxxxx"
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_deep_suffix_chain_probe(self, tr_detector):
        from terlik.types import DetectOptions

        input_text = "orospu" + "larinin" * 10
        start = time.time()
        tr_detector.detect(input_text, DetectOptions())
        assert (time.time() - start) * 1000 < MAX_DETECT_MS

    def test_regression_detection(self, tr_detector):
        from terlik.types import DetectOptions

        assert len(tr_detector.detect("siktir git", DetectOptions())) > 0
        assert len(tr_detector.detect("$1kt1r", DetectOptions())) > 0
        assert len(tr_detector.detect("s.i.k.t.i.r", DetectOptions())) > 0
        assert len(tr_detector.detect("siiiiiktir", DetectOptions())) > 0
        assert len(tr_detector.detect("s1kt1r git", DetectOptions())) > 0
        assert len(tr_detector.detect("orospuluk yapma", DetectOptions())) > 0


class TestAttackSurface:
    @pytest.fixture(scope="class")
    def tr(self):
        from terlik.terlik import Terlik

        t = Terlik()
        t.contains_profanity("warmup")
        return t

    def test_separator_abuse(self, tr):
        assert tr.contains_profanity("s.i.k")
        assert tr.contains_profanity("s_i-k.t.i.r")
        assert tr.contains_profanity("s...i...k")
        assert tr.contains_profanity("s....i....k")
        assert tr.contains_profanity("s\ti\tk")
        assert tr.contains_profanity("s\u200di\u200dk")

    def test_leet_bypass(self, tr):
        assert tr.contains_profanity("$1kt1r lan")
        assert tr.contains_profanity("s1ktir git")
        assert tr.contains_profanity("@pt@l")
        assert tr.contains_profanity("8ok gibi")
        assert tr.contains_profanity("$...1...k")

    def test_char_repetition(self, tr):
        assert tr.contains_profanity("siiiiik")
        assert tr.contains_profanity("sikkkk")
        assert tr.contains_profanity("s" + "i" * 16 + "k")
        assert tr.contains_profanity("$$$1kt1r")

    def test_unicode_tricks(self, tr):
        assert tr.contains_profanity("SiKTiR")
        assert tr.contains_profanity("SIKTIR")
        assert tr.contains_profanity("sIkTiR")

    def test_whitelist_integrity(self, tr):
        assert not tr.contains_profanity("sikke")
        assert not tr.contains_profanity("amsterdam")
        assert not tr.contains_profanity("s1kke")
        assert not tr.contains_profanity("sikkeleri")

    def test_boundary_attacks(self, tr):
        assert tr.contains_profanity("siktir git")
        assert tr.contains_profanity("hadi siktir")
        assert tr.contains_profanity("siktir")
        assert tr.contains_profanity("(siktir)")
        assert tr.contains_profanity('"siktir" dedi')
        assert not tr.contains_profanity("siktir123")
        assert tr.contains_profanity("😀 siktir 😀")
        assert not tr.contains_profanity("mesiktin")

    def test_multi_match(self, tr):
        assert len(tr.get_matches("siktir git orospu cocugu")) >= 2
        input_text = " ".join(["siktir"] * 20)
        assert len(tr.get_matches(input_text)) >= 1
        assert len(tr.get_matches("sik bok got amk ibne")) >= 3

    def test_input_edge_cases(self, tr):
        assert not tr.contains_profanity("")
        assert not tr.contains_profanity("   \t\n  ")
        assert not tr.contains_profanity("a")
        assert not tr.contains_profanity("12345678901234567890")
        assert not tr.contains_profanity("!@#$%^&*()")
        assert not tr.contains_profanity("bu bir test cumlesdir " * 200)
        assert tr.contains_profanity("s\ni\nk")

    def test_suffix_hardening(self, tr):
        assert tr.contains_profanity("orospuluk")
        assert tr.contains_profanity("orospuluklar")
        assert not tr.contains_profanity("ama neden")
        assert tr.contains_profanity("s.i.k.t.i.r.l.e.r")
        assert tr.contains_profanity("$1kt1rler")
