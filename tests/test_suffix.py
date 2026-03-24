import pytest
from terlik.terlik import Terlik


class TestSuffix:
    @pytest.fixture
    def t(self):
        return Terlik()

    def test_suffixable_roots(self, t):
        assert t.contains_profanity("siktiler hepsini")
        assert t.contains_profanity("sikerim seni")
        assert t.contains_profanity("orospuluk yapma")
        assert t.contains_profanity("gotune sokayim")
        assert t.contains_profanity("boktan bir gun")
        assert t.contains_profanity("ibnelik yapma")
        assert t.contains_profanity("gavatlar geldi")
        assert t.contains_profanity("salaksin sen")
        assert t.contains_profanity("aptallarin isi")
        assert t.contains_profanity("kahpeler burada")
        assert t.contains_profanity("pezevenkler toplandi")
        assert t.contains_profanity("yavsaklik etme")
        assert t.contains_profanity("serefsizler")
        assert t.contains_profanity("pustlar geldi")

    def test_suffix_chaining(self, t):
        assert t.contains_profanity("siktirler hep")
        assert t.contains_profanity("orospuluklar")

    def test_evasion_suffix(self, t):
        assert t.contains_profanity("s.i.k.t.i.r.l.e.r")
        assert t.contains_profanity("$1kt1rler")

    def test_non_suffixable(self, t):
        assert not t.contains_profanity("ama neden")
        assert t.contains_profanity("ami bozuk")

    def test_false_positive_prevention(self, t):
        assert not t.contains_profanity("ama ben istemiyorum")
        assert t.contains_profanity("ami problemi var")
        assert not t.contains_profanity("amen dedi")
        assert not t.contains_profanity("osmanlı sikke")
        assert not t.contains_profanity("amsterdam")
        assert not t.contains_profanity("bokser kopek cinsi")
        assert not t.contains_profanity("dolmen yapisi")
        assert not t.contains_profanity("dolunay vardi")
        assert not t.contains_profanity("sıkma limon")
        assert not t.contains_profanity("sıkıntı var")
        assert not t.contains_profanity("sıkıştı araba")
        assert not t.contains_profanity("sıkı çalış")
        assert not t.contains_profanity("amir geldi")
