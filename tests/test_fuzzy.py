import pytest
import math
from terlik.fuzzy import (
    levenshtein_distance,
    levenshtein_similarity,
    dice_similarity,
    get_fuzzy_matcher,
)


class TestFuzzy:
    def test_lev_distance(self):
        assert levenshtein_distance("abc", "abc") == 0
        assert levenshtein_distance("abc", "ab") == 1
        assert levenshtein_distance("abc", "axc") == 1
        assert levenshtein_distance("abc", "abcd") == 1
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "") == 3
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("kitten", "sitting") == 3

    def test_lev_similarity(self):
        assert levenshtein_similarity("abc", "abc") == 1.0
        assert math.isclose(levenshtein_similarity("abc", "xyz"), 0.0)

        sim = levenshtein_similarity("siktir", "siktr")
        assert 0.5 < sim < 1.0

        assert levenshtein_similarity("", "") == 1.0

    def test_dice_similarity(self):
        assert dice_similarity("abc", "abc") == 1.0
        assert dice_similarity("a", "a") == 1.0
        assert dice_similarity("a", "b") == 0.0

        sim = dice_similarity("night", "nacht")
        assert 0 < sim < 1.0

        assert dice_similarity("ab", "cd") == 0.0

    def test_get_matcher(self):
        matcher_lev = get_fuzzy_matcher("levenshtein")
        assert matcher_lev("abc", "abc") == 1.0

        matcher_dice = get_fuzzy_matcher("dice")
        assert matcher_dice("abc", "abc") == 1.0
