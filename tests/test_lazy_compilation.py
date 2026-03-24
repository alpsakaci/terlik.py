import pytest
import time
from terlik.terlik import Terlik
from terlik.types import TerlikOptions


class TestLazyCompilation:
    def test_construction_performance(self):
        start = time.time()
        Terlik()
        elapsed = (time.time() - start) * 1000
        # Should build without regex compilation, very fast
        assert elapsed < 100

    def test_transparent_lazy_compilation(self):
        t = Terlik()
        assert t.contains_profanity("siktir git")
        assert not t.contains_profanity("merhaba dunya")

        t2 = Terlik()
        matches = t2.get_matches("siktir git")
        assert len(matches) > 0
        assert matches[0].method == "pattern"

        t3 = Terlik()
        cleaned = t3.clean("siktir git")
        assert "siktir" not in cleaned

    def test_strict_mode_no_pattern_compilation(self):
        t1 = Terlik(TerlikOptions(mode="strict"))
        start_construct = time.time()
        t2 = Terlik(TerlikOptions(mode="strict"))
        construct_time = (time.time() - start_construct) * 1000

        start_detect = time.time()
        t2.contains_profanity("siktir")
        detect_time = (time.time() - start_detect) * 1000

        assert construct_time < 100
        assert detect_time < 100

        assert t1.contains_profanity("siktir")
        assert not t1.contains_profanity("merhaba")

    def test_get_patterns_triggers_compilation(self):
        t = Terlik()
        patterns = t.get_patterns()
        assert len(patterns) > 0

    def test_recompile(self):
        t = Terlik()
        assert not t.contains_profanity("xyztest123")
        t.add_words(["xyztest123"])
        assert t.contains_profanity("xyztest123")

        t2 = Terlik(TerlikOptions(custom_list=["xyztest456"]))
        assert t2.contains_profanity("xyztest456")
        t2.remove_words(["xyztest456"])
        assert not t2.contains_profanity("xyztest456")

    def test_background_warmup(self):
        t = Terlik(TerlikOptions(background_warmup=True))
        time.sleep(0.1)  # Let background thread warmup
        assert t.contains_profanity("siktir git")

    def test_warmup_static(self):
        cache = Terlik.warmup(["tr"])
        tr = cache["tr"]
        assert tr.contains_profanity("siktir")
