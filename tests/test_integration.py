import pytest
from terlik.terlik import Terlik
from terlik.types import TerlikOptions


class TestIntegration:
    def test_contains_profanity(self):
        t = Terlik()
        assert t.contains_profanity("siktir git")
        assert not t.contains_profanity("merhaba dunya")
        assert not t.contains_profanity("")
        assert not t.contains_profanity(None)

    def test_get_matches(self):
        t = Terlik()
        matches = t.get_matches("siktir git")
        assert len(matches) > 0
        assert hasattr(matches[0], "word")
        assert hasattr(matches[0], "root")
        assert hasattr(matches[0], "index")
        assert hasattr(matches[0], "severity")
        assert hasattr(matches[0], "method")

        assert t.get_matches("merhaba") == []

    def test_clean(self):
        t = Terlik()
        result = t.clean("siktir git")
        assert "siktir" not in result
        assert "*" in result

        t_partial = Terlik(TerlikOptions(mask_style="partial"))
        assert t_partial.clean("siktir git") != "siktir git"

        t_replace = Terlik(TerlikOptions(mask_style="replace", replace_mask="[küfür]"))
        assert "[küfür]" in t_replace.clean("siktir git")

    def test_add_remove_words(self):
        t = Terlik()
        assert not t.contains_profanity("kodumun")
        t.add_words(["kodumun"])
        assert t.contains_profanity("kodumun")

        assert t.contains_profanity("salak")
        t.remove_words(["salak"])
        assert not t.contains_profanity("salak")

    def test_modes(self):
        t1 = Terlik(TerlikOptions(mode="strict"))
        assert not t1.contains_profanity("s i k t i r")

        t2 = Terlik(TerlikOptions(mode="balanced"))
        assert t2.contains_profanity("s.i.k.t.i.r")

        t3 = Terlik(TerlikOptions(mode="loose"))
        matches = t3.get_matches("siktiir git")
        assert len(matches) > 0

    def test_custom_options(self):
        t1 = Terlik(TerlikOptions(whitelist=["testword"]))
        assert not t1.contains_profanity("sikke")

        t2 = Terlik(TerlikOptions(custom_list=["hiyar"]))
        assert t2.contains_profanity("bu adam hiyar")

        t3 = Terlik(TerlikOptions(max_length=5))
        assert not t3.contains_profanity("abcde siktir git")

    def test_get_patterns(self):
        t = Terlik()
        patterns = t.get_patterns()
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
