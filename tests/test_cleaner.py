import pytest
from terlik.cleaner import apply_mask, clean_text
from terlik.types import MatchResult


class TestCleaner:
    def test_apply_mask_stars(self):
        assert apply_mask("siktir", "stars", "[***]") == "******"

    def test_apply_mask_partial(self):
        assert apply_mask("siktir", "partial", "[***]") == "s****r"

    def test_apply_mask_partial_short(self):
        assert apply_mask("am", "partial", "[***]") == "**"
        assert apply_mask("a", "partial", "[***]") == "*"

    def test_apply_mask_replace(self):
        assert apply_mask("siktir", "replace", "[***]") == "[***]"
        assert apply_mask("siktir", "replace", "***") == "***"

    @pytest.fixture
    def match_list(self):
        return [
            MatchResult(
                word="siktir",
                root="sik",
                index=7,
                severity="high",
                category="insult",
                method="pattern",
            )
        ]

    def test_clean_text_stars(self, match_list):
        result = clean_text("haydi, siktir git!", match_list, "stars", "[***]")
        assert result == "haydi, ****** git!"

    def test_clean_text_partial(self, match_list):
        result = clean_text("haydi, siktir git!", match_list, "partial", "[***]")
        assert result == "haydi, s****r git!"

    def test_clean_text_replace(self, match_list):
        result = clean_text("haydi, siktir git!", match_list, "replace", "[küfür]")
        assert result == "haydi, [küfür] git!"

    def test_clean_text_multiple(self):
        multi_matches = [
            MatchResult(
                word="siktir",
                root="sik",
                index=0,
                severity="high",
                category="insult",
                method="pattern",
            ),
            MatchResult(
                word="aptal",
                root="aptal",
                index=11,
                severity="low",
                category="insult",
                method="pattern",
            ),
        ]
        result = clean_text("siktir lan aptal", multi_matches, "stars", "[***]")
        assert result == "****** lan *****"

    def test_clean_text_no_matches(self):
        assert clean_text("merhaba dunya", [], "stars", "[***]") == "merhaba dunya"
