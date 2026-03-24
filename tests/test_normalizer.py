import pytest
from terlik.normalizer import (
    normalize,
    create_normalizer,
    TURKISH_CHAR_MAP,
    LEET_MAP,
    TR_NUMBER_MAP,
    remove_punctuation,
    collapse_repeats,
    trim_whitespace,
)


class TestNormalizer:
    def test_create_normalizer_turkish(self):
        norm_fn = create_normalizer("tr", TURKISH_CHAR_MAP, LEET_MAP, TR_NUMBER_MAP)
        assert norm_fn("HELLO") == "hello"
        assert norm_fn("İSTANBUL") == "istanbul"
        assert norm_fn("çğıöşü") == "cgiosu"
        assert norm_fn("ÇĞİÖŞÜ") == "cgiosu"

    def test_replace_leetspeak(self):
        norm_fn = create_normalizer("tr", TURKISH_CHAR_MAP, LEET_MAP, TR_NUMBER_MAP)
        assert norm_fn("h3ll0") == "hello"
        assert norm_fn("$1k") == "sik"
        assert norm_fn("4m1n4") == "amina"

    def test_expand_numbers(self):
        norm_fn = create_normalizer("tr", TURKISH_CHAR_MAP, LEET_MAP, TR_NUMBER_MAP)
        assert norm_fn("s2k") == "sikik"
        assert norm_fn("s2mle") == "sikimle"
        assert norm_fn("a2b") == "aikib"
        # Does not expand standalone numbers using number_expansions (but leet_map still converts them)
        assert norm_fn("2023 yilinda") == "ioie yilinda"
        assert norm_fn("skor 2-1") == "skor ii"
        assert norm_fn("100 kisi") == "ioo kisi"
        assert norm_fn("i8ne") == "ibne"

    def test_remove_punctuation(self):
        assert remove_punctuation("s.i.k") == "sik"
        assert remove_punctuation("s-i-k") == "sik"
        assert remove_punctuation("s_i_k") == "sik"
        assert remove_punctuation("s*i*k") == "sik"
        assert remove_punctuation("hello! world") == "hello! world"
        assert remove_punctuation("test.") == "test."

    def test_collapse_repeats(self):
        assert collapse_repeats("siiik") == "sik"
        assert collapse_repeats("ammmk") == "amk"
        assert collapse_repeats("aaaaaa") == "a"
        assert collapse_repeats("oo") == "oo"

    def test_trim_whitespace(self):
        assert trim_whitespace("  hello   world  ") == "hello world"

    def test_full_pipeline(self):
        assert normalize("S.İ.K.T.İ.R") == "siktir"
        assert normalize("$1k7!r") == "siktir"
        assert normalize("SIIIKTIR") == "siktir"
        assert normalize("  hello   world  ") == "hello world"
        assert normalize("") == ""
        assert normalize("a") == "a"
        # Emojis preserved
        assert "😀" in normalize("hello 😀 world")
