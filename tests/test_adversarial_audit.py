import pytest
import time
from terlik import Terlik


# Load dictionary instances
@pytest.fixture(scope="module")
def en():
    from terlik.types import TerlikOptions

    return Terlik(TerlikOptions(language="en"))


@pytest.fixture(scope="module")
def tr():
    from terlik.types import TerlikOptions

    return Terlik(TerlikOptions(language="tr"))


@pytest.fixture(scope="module")
def es():
    from terlik.types import TerlikOptions

    return Terlik(TerlikOptions(language="es"))


@pytest.fixture(scope="module")
def de():
    from terlik.types import TerlikOptions

    return Terlik(TerlikOptions(language="de"))


class TestAdversarialEN:
    def test_accented(self, en):
        accented = [
            "f\u00fcck",
            "f\u00f9ck",
            "f\u00fbck",
            "sh\u00eet",
            "sh\u00eft",
            "b\u00eetch",
            "c\u00fcnt",
            "d\u00ecck",
            "n\u00efgger",
            "f\u00e0ggot",
            "r\u00e0pe",
            "p\u00f6rn",
        ]
        for word in accented:
            assert en.contains_profanity(word), f"{word} should be detected"
        assert not en.contains_profanity("w\u00f6nk")

    def test_cyrillic(self, en):
        cyrillic = [
            "fu\u0441k",
            "f\u0443ck",
            "\u0430ss",
            "sh\u0456t",
            "b\u0456tch",
            "\u0441unt",
            "di\u0441k",
            "wh\u043ere",
            "r\u0430pe",
            "p\u043ern",
        ]
        for word in cyrillic:
            assert en.contains_profanity(word)

    def test_fullwidth(self, en):
        assert en.contains_profanity("\uff46\uff55\uff43\uff4b")
        assert en.contains_profanity("\uff53\uff48\uff49\uff54")
        assert en.contains_profanity("f\uff55ck")

    def test_normalization(self, en):
        assert en.contains_profanity("fuc\u0327k")
        assert en.contains_profanity("fu\u00e7k")
        assert en.contains_profanity("shi\u0302t")
        assert en.contains_profanity("sh\u00eet")

    def test_zero_width(self, en):
        assert en.contains_profanity("f\u200buck")
        assert en.contains_profanity("f\u200cu\u200cc\u200ck")
        assert en.contains_profanity("f\u00adu\u00adc\u00adk")

    def test_fp_stress(self, en):
        fps = [
            "assumption",
            "cocky",
            "therapists",
            "grapevine",
            "passionate",
            "compassionate",
            "embarrass",
            "harassment",
            "scrapbook",
            "cumulonimbus",
            "cumulative",
            "circumvent",
            "pennant",
            "penalize",
            "peninsula",
            "penetrate",
            "Titanic",
            "constitution",
            "analytical",
            "psychoanalysis",
            "masseuse",
            "cassette",
            "classic",
            "classy",
            "Dickensian",
            "cocktails",
            "peacocking",
            "buttress",
            "butterscotch",
            "rebuttal",
            "sextant",
            "sextet",
            "Sussex",
            "shitake",
            "document",
            "buckle",
            "Hancock",
            "cocktail",
            "shuttlecocks",
        ]
        for word in fps:
            assert not en.contains_profanity(word)

    def test_compound_evasion(self, en):
        compounds = [
            "fuckwad",
            "shitlord",
            "cockwomble",
            "twatwaffle",
            "assmunch",
            "cumguzzler",
            "dickweasel",
        ]
        for word in compounds:
            assert en.contains_profanity(word)

    def test_boundary_cases(self, en):
        assert en.contains_profanity("visit example.com/fuck")
        assert en.contains_profanity("email fuck@email.com")
        assert en.contains_profanity("FuckYou")
        assert en.contains_profanity("mother-fucker")
        assert en.contains_profanity("#fuckyou")


class TestAdversarialTR:
    def test_locale_edge_cases(self, tr):
        assert tr.contains_profanity("SİKTİR")

    def test_accented(self, tr):
        accented = ["s\u00ecktir", "s\u00eektir", "or\u00f2spu"]
        for word in accented:
            assert tr.contains_profanity(word)

    def test_cyrillic(self, tr):
        assert tr.contains_profanity("s\u0456kt\u0456r")
        assert tr.contains_profanity("\u043er\u043espu")

    def test_fp_stress(self, tr):
        safe = [
            "sıkıntı",
            "sıkıştı",
            "sıkma",
            "sıkı",
            "sıkıcı",
            "ambalaj",
            "ameliyat",
            "ambulans",
            "amazon",
            "bokser",
            "boksör",
            "malzeme",
            "maliyet",
            "memur",
            "memorial",
            "memleket",
            "memento",
            "piknik",
            "kasım",
            "namuslu",
            "ahlaki",
            "dolunay",
            "dolap",
            "dolar",
            "dolma",
            "sikke",
            "siklet",
            "gotan",
            "gotik",
            "gotham",
            "yarasa",
            "tasselled",
            "sıkmak",
            "sıkılmak",
            "masikler",
            "sikilasma",
        ]
        for word in safe:
            assert not tr.contains_profanity(word)

    def test_number_expansion(self, tr):
        assert tr.contains_profanity("s2k")
        assert not tr.contains_profanity("s100")

    def test_suffix_boundary(self, tr):
        assert tr.contains_profanity("orospular")


class TestAdversarialES:
    def test_accented(self, es):
        accented = [
            "m\u00ecerda",
            "p\u00fbta",
            "c\u00f2ño",
            "h\u00ecjoputa",
            "p\u00e8ndejo",
        ]
        for word in accented:
            assert es.contains_profanity(word)

    def test_cyrillic(self, es):
        assert es.contains_profanity("put\u0430")

    def test_fp_stress(self, es):
        safe = [
            "computadora",
            "disputar",
            "reputacion",
            "imputar",
            "pollo",
            "pollito",
            "polluelo",
            "folleto",
            "follaje",
            "particular",
            "articulo",
            "vehicular",
            "calcular",
            "maricopa",
            "putamen",
            "disputar",
            "polleria",
        ]
        for word in safe:
            assert not es.contains_profanity(word)


class TestAdversarialDE:
    def test_ss_beta(self, de):
        assert de.contains_profanity("Scheisse")
        assert de.contains_profanity("SCHEISSE")
        assert de.contains_profanity("SCHEIßE")

    def test_accented(self, de):
        accented = [
            "f\u00ecck",
            "f\u00eeck",
            "H\u00f9re",
            "F\u00f2tze",
            "Schl\u00e0mpe",
            "W\u00ecchser",
        ]
        for word in accented:
            assert de.contains_profanity(word)

    def test_cyrillic(self, de):
        assert de.contains_profanity("F\u0456ck")
        assert de.contains_profanity("\u0410rsch")

    def test_fp_stress(self, de):
        safe = [
            "schwanger",
            "schwangerschaft",
            "geschichte",
            "ficktion",
            "arschen",
            "schwanzen",
            "Gesellschaft",
            "Wirtschaft",
            "Wissenschaft",
            "Druckerei",
            "Druckfehler",
            "Spastik",
            "Spastiker",
        ]
        for word in safe:
            assert not de.contains_profanity(word)


class TestCrossCuttingAndIsolation:
    def test_redos_en_separator(self, en):
        start = time.time()
        en.contains_profanity("." * 1000 + "fuck")
        assert (time.time() - start) * 1000 < 1000

    def test_redos_en_alternating(self, en):
        import string

        letters = string.ascii_lowercase
        txt = ".".join(letters[i % 26] for i in range(500))
        start = time.time()
        en.contains_profanity(txt)
        assert (time.time() - start) * 1000 < 2000

    def test_redos_en_nearmatch(self, en):
        txt = "fuc " * 2500
        start = time.time()
        en.contains_profanity(txt[:10000])
        assert (time.time() - start) * 1000 < 5000

    def test_redos_tr_suffix(self, tr):
        txt = "sik" + "tirlerinesinin" * 700
        start = time.time()
        tr.contains_profanity(txt[:10000])
        assert (time.time() - start) * 1000 < 5000

    def test_isolation(self, en, tr, es, de):
        assert not en.contains_profanity("siktir git")
        assert not en.contains_profanity("du Arschloch")
        assert not tr.contains_profanity("what the fuck")
        assert not de.contains_profanity("hijo de puta")
        assert not es.contains_profanity("orospu çocuğu")
