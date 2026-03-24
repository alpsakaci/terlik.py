import pytest
from terlik import Terlik


@pytest.fixture(scope="module")
def t():
    return Terlik()


def detects(t, text, expected_root=None):
    matches = t.get_matches(text)
    assert len(matches) > 0, f'"{text}" should be detected'
    if expected_root:
        assert any(
            m.root == expected_root for m in matches
        ), f'"{text}" should match root "{expected_root}"'


def clean(t, text):
    assert not t.contains_profanity(text), f'"{text}" should be clean'


class TestProfanity:
    def test_root_sik(self, t):
        cases = [
            "sik",
            "siktir git",
            "sikerim seni",
            "sikicem",
            "siktim",
            "sikeyim",
            "sikis",
            "sikik herif",
            "sikim",
            "SİKTİR",
            "$1kt1r",
            "s.i.k",
            "siiiiiktir",
            "hadi siktir git burdan",
            "siktiler",
            "siktirler",
        ]
        for case in cases:
            detects(t, case, "sik")
        clean(t, "sikke")
        clean(t, "siklet")

    def test_root_amk(self, t):
        cases = [
            "amk",
            "amina koyarim",
            "aminakoyim",
            "aminakoydugum",
            "amq",
            "bu ne amk",
            "AMK",
        ]
        for case in cases:
            detects(t, case, "amk")

    def test_root_orospu(self, t):
        cases = [
            "orospu",
            "orospucocugu",
            "orspu",
            "oruspu",
            "orosbu",
            "kes lan orospu cocugu",
            "orospuluk yapma",
            "orospular",
            "o.r.o.s.p.u",
        ]
        for case in cases:
            detects(t, case, "orospu")

    def test_root_pic(self, t):
        cases = ["piç kurusu", "pic", "piclik yapma", "bu adam pic", "picler"]
        for case in cases:
            detects(t, case, "piç")
        clean(t, "piknik")
        clean(t, "pikachu")

    def test_root_yarrak(self, t):
        cases = [
            "yarrak",
            "yarak",
            "yarakli",
            "dalyarak",
            "dalyarrak",
            "bu ne yarrak gibi is",
            "yarraklar",
        ]
        for case in cases:
            detects(t, case, "yarrak")
        clean(t, "yarasa")

    def test_root_got(self, t):
        cases = [
            "göt",
            "got",
            "gotunu",
            "gotlek",
            "gotveren",
            "gotverenler",
            "senin got",
            "6öt",
            "gotune",
            "gotler",
        ]
        for case in cases:
            detects(t, case, "göt")
        clean(t, "gotik")
        clean(t, "gotham")

    def test_root_am(self, t):
        cases = ["amcik", "amcuk", "amcik herif", "ami"]
        for case in cases:
            detects(t, case, "am")
        safe = [
            "ama",
            "amen",
            "amir",
            "ambalaj",
            "ambulans",
            "ameliyat",
            "amerika",
            "amino",
            "amonyak",
            "ampul",
        ]
        for s in safe:
            clean(t, s)

    def test_root_tasak(self, t):
        cases = ["taşak", "tasak", "tassak", "tassakli", "tasak gecme", "tasaklar"]
        for case in cases:
            detects(t, case, "taşak")

    def test_root_meme(self, t):
        cases = ["meme", "meme gosterdi", "MEME"]
        for case in cases:
            detects(t, case, "meme")
        for s in ["memento", "memleket", "memur", "memorial"]:
            clean(t, s)

    def test_root_ibne(self, t):
        cases = ["ibne", "ibneler", "lan ibne", "i8ne", "ibnelik", "ibneler geldi"]
        for case in cases:
            detects(t, case, "ibne")

    def test_root_gavat(self, t):
        cases = ["gavat", "gavatlik", "bu adam gavat", "gavatlar", "GAVAT"]
        for case in cases:
            detects(t, case, "gavat")

    def test_root_pezevenk(self, t):
        cases = [
            "pezevenk",
            "pezo herif",
            "bu pezevenk kim",
            "pezevenkler",
            "pezevenklik",
        ]
        for case in cases:
            detects(t, case, "pezevenk")

    def test_root_bok(self, t):
        cases = ["bok", "boktan", "ne boktan bir gun", "8ok", "boklar", "boklu"]
        for case in cases:
            detects(t, case, "bok")
        clean(t, "bokser")
        clean(t, "boksör")

    def test_root_haysiyetsiz(self, t):
        cases = ["haysiyetsiz", "bu adam haysiyetsiz", "HAYSIYETSIZ"]
        for case in cases:
            detects(t, case, "haysiyetsiz")

    def test_root_salak(self, t):
        cases = [
            "salak",
            "salaklik",
            "salak misin sen",
            "SALAK",
            "salaksin",
            "salaklar",
        ]
        for case in cases:
            detects(t, case, "salak")

    def test_root_aptal(self, t):
        cases = [
            "aptal",
            "aptallik",
            "aptalca",
            "bu adam aptal herif",
            "@pt@l",
            "aptallar",
            "aptallarin isi",
        ]
        for case in cases:
            detects(t, case, "aptal")

    def test_root_gerizekali(self, t):
        cases = ["gerizekalı", "gerizekali", "bu gerizekali kim", "gerizekaliler"]
        for case in cases:
            detects(t, case, "gerizekalı")

    def test_root_mal(self, t):
        cases = ["mal herif", "bu adam mal", "MAL"]
        for case in cases:
            detects(t, case, "mal")
        safe = [
            "malzeme",
            "maliyet",
            "malik",
            "malikane",
            "maliye",
            "malta",
            "malt",
            "mallorca",
        ]
        for s in safe:
            clean(t, s)

    def test_root_dangalak(self, t):
        cases = ["dangalak", "bu dangalak ne yapiyor", "dangalaklar", "DANGALAK"]
        for case in cases:
            detects(t, case, "dangalak")

    def test_root_ezik(self, t):
        cases = ["ezik", "ezik herif", "ezikler", "eziklik", "EZIK"]
        for case in cases:
            detects(t, case, "ezik")

    def test_root_pust(self, t):
        cases = ["puşt", "pust", "pustt", "lan pust", "pu$t", "pustlar", "pustluk"]
        for case in cases:
            detects(t, case, "puşt")

    def test_root_serefsiz(self, t):
        cases = [
            "şerefsiz",
            "serefsiz",
            "serefsizler",
            "bu serefsiz adam",
            "serefsizlik",
            "SEREFSIZ",
        ]
        for case in cases:
            detects(t, case, "şerefsiz")

    def test_root_yavsak(self, t):
        cases = [
            "yavşak",
            "yavsak",
            "bu yavsak kim",
            "yavsaklik",
            "yavsaklar",
            "YAVSAK",
        ]
        for case in cases:
            detects(t, case, "yavşak")

    def test_root_dol(self, t):
        cases = ["döl", "dol", "dolunu", "dol israfı", "dolcu"]
        for case in cases:
            detects(t, case, "döl")
        for s in ["dolunay", "dolum", "doluluk", "dolmen"]:
            clean(t, s)

    def test_root_kahpe(self, t):
        cases = ["kahpe", "kahpelik", "kahpe kari", "kahpeler", "kahpelikler", "KAHPE"]
        for case in cases:
            detects(t, case, "kahpe")

    def test_root_surtuk(self, t):
        cases = [
            "sürtük",
            "surtuk",
            "bu kadin surtuk",
            "surtukler",
            "surtukluk",
            "SÜRTÜK",
        ]
        for case in cases:
            detects(t, case, "sürtük")

    def test_root_kaltak(self, t):
        cases = ["kaltak", "bu kaltak kim", "kaltaklar", "kaltaklik", "KALTAK"]
        for case in cases:
            detects(t, case, "kaltak")

    def test_root_fahise(self, t):
        cases = [
            "fahişe",
            "fahise",
            "bu fahise kadin",
            "fahiseler",
            "fahiselik",
            "FAHISE",
        ]
        for case in cases:
            detects(t, case, "fahişe")

    def test_root_kevase(self, t):
        cases = ["kevaşe", "kevase", "bu kevase kim", "kevaseler", "KEVASE"]
        for case in cases:
            detects(t, case, "kevaşe")

    def test_root_oglanci(self, t):
        cases = [
            "oğlancı",
            "oglanci",
            "bu adam oglanci",
            "oglancilar",
            "oglancilik",
            "OGLANCI",
        ]
        for case in cases:
            detects(t, case, "oğlancı")

    def test_root_dingil(self, t):
        cases = ["dingil", "bu dingil ne yapiyor", "dingiller", "dingillik", "DINGIL"]
        for case in cases:
            detects(t, case, "dingil")

    def test_root_avanak(self, t):
        cases = ["avanak", "bu avanak herif", "avanaklar", "avanaklik", "AVANAK"]
        for case in cases:
            detects(t, case, "avanak")

    def test_root_manyak(self, t):
        cases = ["manyak", "bu adam manyak", "manyaklar", "manyaklik", "MANYAK"]
        for case in cases:
            detects(t, case, "manyak")

    def test_root_hoduk(self, t):
        cases = ["hödük", "hoduk", "bu hoduk herif", "hodukler", "hodukluk", "HODUK"]
        for case in cases:
            detects(t, case, "hödük")

    def test_root_kepaze(self, t):
        cases = ["kepaze", "bu adam kepaze", "kepazeler", "kepazelik", "KEPAZE"]
        for case in cases:
            detects(t, case, "kepaze")

    def test_root_rezil(self, t):
        cases = ["rezil", "rezil oldu", "reziller", "rezillik", "REZIL"]
        for case in cases:
            detects(t, case, "rezil")

    def test_root_kalles(self, t):
        cases = [
            "kalleş",
            "kalles",
            "bu kalles herif",
            "kallesler",
            "kalleslik",
            "KALLES",
        ]
        for case in cases:
            detects(t, case, "kalleş")

    def test_root_namussuz(self, t):
        cases = [
            "namussuz",
            "bu namussuz adam",
            "namussuzlar",
            "namussuzluk",
            "NAMUSSUZ",
        ]
        for case in cases:
            detects(t, case, "namussuz")
        clean(t, "namus")
        clean(t, "namuslu")

    def test_root_ahlaksiz(self, t):
        cases = [
            "ahlaksız",
            "ahlaksiz",
            "bu ahlaksiz adam",
            "ahlaksizlar",
            "ahlaksizlik",
            "AHLAKSIZ",
        ]
        for case in cases:
            detects(t, case, "ahlaksız")
        clean(t, "ahlak")
        clean(t, "ahlaki")
