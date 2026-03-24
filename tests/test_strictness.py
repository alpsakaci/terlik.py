import pytest
from terlik.terlik import Terlik
from terlik.types import TerlikOptions, DetectOptions, CleanOptions


class TestStrictness:
    def test_disable_leet_decode(self):
        t1 = Terlik()
        assert t1.contains_profanity("$1kt1r")

        t2 = Terlik(TerlikOptions(disable_leet_decode=True))
        assert not t2.contains_profanity("$1kt1r")

        assert not t1.contains_profanity(
            "$1kt1r", DetectOptions(disable_leet_decode=True)
        )
        assert t1.contains_profanity("$1kt1r")

        # safety layers
        assert t2.contains_profanity("ｓｉｋｔｉｒ")  # NFKD
        assert t2.contains_profanity("sïktïr")  # Diacritics
        assert t2.contains_profanity("оrоspu")  # Cyrillic 'а', 'о'

        assert t2.contains_profanity("siktir")
        assert t2.contains_profanity("amk")

    def test_disable_compound(self):
        t1 = Terlik(TerlikOptions(language="en"))
        assert t1.contains_profanity("ShitPerson")

        t2 = Terlik(TerlikOptions(language="en", disable_compound=True))
        assert not t2.contains_profanity("ShitPerson")

        assert not t1.contains_profanity(
            "ShitPerson", DetectOptions(disable_compound=True)
        )

        assert t2.contains_profanity("motherfucker")
        assert t2.contains_profanity("fuck")

    def test_min_severity(self):
        t1 = Terlik()
        assert t1.contains_profanity("salak")
        assert t1.contains_profanity("bok")
        assert t1.contains_profanity("siktir")

        t2 = Terlik(TerlikOptions(min_severity="medium"))
        assert not t2.contains_profanity("salak")
        assert t2.contains_profanity("bok")

        t3 = Terlik(TerlikOptions(min_severity="high"))
        assert not t3.contains_profanity("salak")
        assert not t3.contains_profanity("bok")
        assert t3.contains_profanity("siktir")

        assert not t1.contains_profanity("salak", DetectOptions(min_severity="medium"))

        t4 = Terlik(TerlikOptions(min_severity="low"))
        assert t4.contains_profanity("salak")

    def test_exclude_categories(self):
        t1 = Terlik()
        assert t1.contains_profanity("siktir")
        assert t1.contains_profanity("orospu")

        t2 = Terlik(TerlikOptions(exclude_categories=["sexual"]))
        assert not t2.contains_profanity("siktir")
        assert t2.contains_profanity("orospu")

        t3 = Terlik(
            TerlikOptions(
                custom_list=["badword"],
                exclude_categories=["sexual", "insult", "slur", "general"],
            )
        )
        assert t3.contains_profanity("badword")

    def test_category_in_match_result(self):
        t = Terlik()
        matches = t.get_matches("siktir")
        assert len(matches) > 0
        assert matches[0].category == "sexual"

    def test_mode_toggle_interaction(self):
        t = Terlik(TerlikOptions(mode="strict", min_severity="high"))
        assert not t.contains_profanity("salak")
        assert t.contains_profanity("siktir")

    def test_clean_respects_toggles(self):
        t = Terlik(TerlikOptions(min_severity="high"))
        assert t.clean("salak") == "salak"
        assert t.clean("siktir") != "siktir"

        t2 = Terlik()
        cleaned = t2.clean("salak siktir", CleanOptions(min_severity="high"))
        assert "salak" in cleaned
        assert "siktir" not in cleaned
