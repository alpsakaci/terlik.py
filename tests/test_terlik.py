import pytest
from terlik import Terlik
from terlik.types import TerlikOptions

class TestTerlikIntegration:
    class TestContainsProfanity:
        def test_returns_true_for_profane_text(self):
            terlik = Terlik()
            assert terlik.contains_profanity("siktir git") is True

        def test_returns_false_for_clean_text(self):
            terlik = Terlik()
            assert terlik.contains_profanity("merhaba dunya") is False

        def test_returns_false_for_empty_input(self):
            terlik = Terlik()
            assert terlik.contains_profanity("") is False

        def test_returns_false_for_null_ish_input(self):
            terlik = Terlik()
            assert terlik.contains_profanity(None) is False

    class TestGetMatches:
        def test_returns_match_details(self):
            terlik = Terlik()
            matches = terlik.get_matches("siktir git")
            assert len(matches) > 0
            assert hasattr(matches[0], "word")
            assert hasattr(matches[0], "root")
            assert hasattr(matches[0], "index")
            assert hasattr(matches[0], "severity")
            assert hasattr(matches[0], "method")

        def test_returns_empty_array_for_clean_text(self):
            terlik = Terlik()
            assert terlik.get_matches("merhaba") == []

    class TestClean:
        def test_masks_profanity_with_stars_by_default(self):
            terlik = Terlik()
            result = terlik.clean("siktir git")
            assert "siktir" not in result
            assert "*" in result

        def test_supports_partial_mask(self):
            terlik_partial = Terlik(TerlikOptions(mask_style="partial"))
            result = terlik_partial.clean("siktir git")
            assert result != "siktir git"

        def test_supports_replace_mask(self):
            terlik_replace = Terlik(TerlikOptions(mask_style="replace", replace_mask="[küfür]"))
            result = terlik_replace.clean("siktir git")
            assert "[küfür]" in result

        def test_returns_clean_text_unchanged(self):
            terlik = Terlik()
            assert terlik.clean("merhaba dunya") == "merhaba dunya"

    class TestAddRemoveWords:
        def test_adds_custom_words(self):
            terlik = Terlik()
            assert terlik.contains_profanity("kodumun") is False
            terlik.add_words(["kodumun"])
            assert terlik.contains_profanity("kodumun") is True

        def test_removes_words_from_dictionary(self):
            terlik = Terlik()
            assert terlik.contains_profanity("salak") is True
            terlik.remove_words(["salak"])
            assert terlik.contains_profanity("salak") is False

    class TestModes:
        def test_strict_mode_does_not_catch_separated_chars(self):
            terlik = Terlik(TerlikOptions(mode="strict"))
            assert terlik.contains_profanity("s i k t i r") is False

        def test_balanced_mode_catches_separated_chars(self):
            terlik = Terlik(TerlikOptions(mode="balanced"))
            assert terlik.contains_profanity("s.i.k.t.i.r") is True

        def test_loose_mode_enables_fuzzy(self):
            terlik = Terlik(TerlikOptions(mode="loose"))
            matches = terlik.get_matches("siktiir git")
            assert len(matches) > 0

    class TestCustomOptions:
        def test_respects_custom_whitelist(self):
            terlik = Terlik(TerlikOptions(whitelist=["testword"]))
            # whitelist is additive, built-in ones still work
            assert terlik.contains_profanity("sikke") is False

        def test_respects_custom_word_list(self):
            terlik = Terlik(TerlikOptions(custom_list=["hiyar"]))
            assert terlik.contains_profanity("bu adam hiyar") is True

        def test_respects_max_length(self):
            terlik = Terlik(TerlikOptions(max_length=5))
            # Input gets truncated to 5 chars - profanity beyond limit not detected
            assert terlik.contains_profanity("abcde siktir git") is False

    class TestGetPatterns:
        def test_returns_patterns_map(self):
            terlik = Terlik()
            patterns = terlik.get_patterns()
            assert isinstance(patterns, dict)
            assert len(patterns) > 0
