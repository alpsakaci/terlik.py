import pytest
from terlik.detector import Detector
from terlik.dictionary.core import Dictionary
from terlik.lang.tr.config import config as trConfig
from terlik.normalizer import create_normalizer
from terlik.types import DetectOptions


@pytest.fixture
def detector():
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


class TestDetector:
    def test_pattern_mode(self, detector):
        opts = DetectOptions(mode="balanced")

        results = detector.detect("bu adam siktir olsun", opts)
        assert len(results) > 0
        assert results[0].root == "sik"

        assert len(detector.detect("$1kt1r lan", opts)) > 0
        assert len(detector.detect("s.i.k.t.i.r", opts)) > 0
        assert len(detector.detect("siiiktir", opts)) > 0

        # Whitelist
        res_sikke = detector.detect("osmanlı sikke koleksiyonu", opts)
        assert not any(r.word.lower() == "sikke" for r in res_sikke)

        res_orospu = detector.detect("orospu cocugu", opts)
        assert len(res_orospu) > 0
        assert any(r.root == "orospu" for r in res_orospu)

        assert len(detector.detect("merhaba dunya nasilsin", opts)) == 0

    def test_strict_mode(self, detector):
        opts = DetectOptions(mode="strict")
        assert len(detector.detect("siktir git", opts)) > 0
        assert len(detector.detect("s i k t i r", opts)) == 0

    def test_loose_mode(self, detector):
        opts = DetectOptions(mode="loose", enable_fuzzy=True, fuzzy_threshold=0.7)
        assert len(detector.detect("siktiir", opts)) > 0

    def test_get_patterns(self, detector):
        patterns = detector.get_patterns()
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
        assert "sik" in patterns
