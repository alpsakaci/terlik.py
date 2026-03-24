import pytest
from terlik import Terlik


class TestEdgeCases:
    @pytest.fixture
    def terlik_inst(self):
        return Terlik()

    def test_false_positive_prevention(self, terlik_inst):
        assert not terlik_inst.contains_profanity("osmanlı sikke koleksiyonu")
        assert not terlik_inst.contains_profanity("amsterdam güzel şehir")
        assert not terlik_inst.contains_profanity("ambulans geldi")
        assert not terlik_inst.contains_profanity("ameliyat olacak")
        assert not terlik_inst.contains_profanity("malzeme listesi")
        assert not terlik_inst.contains_profanity("devlet memuru")
        assert not terlik_inst.contains_profanity("bokser köpek cinsi")
        assert not terlik_inst.contains_profanity("ama yapamam")
        assert terlik_inst.contains_profanity("ami sorunu")
        assert not terlik_inst.contains_profanity("amen dedi papaz")
        assert not terlik_inst.contains_profanity("amir bey geldi")
        assert not terlik_inst.contains_profanity("dolmen antik yapi")
        assert not terlik_inst.contains_profanity("amazon siparis verdim")
        assert not terlik_inst.contains_profanity("ambargo uygulandi")
        assert not terlik_inst.contains_profanity("amblem tasarimi")
        assert not terlik_inst.contains_profanity("amfibi arac")
        assert not terlik_inst.contains_profanity("dolap kapagi")
        assert not terlik_inst.contains_profanity("dolar kuru yukseldi")
        assert not terlik_inst.contains_profanity("dolma yaprak sardim")
        assert not terlik_inst.contains_profanity("dolmus bekliyorum")
        assert not terlik_inst.contains_profanity("malum kisi")
        assert not terlik_inst.contains_profanity("namus meselesi")
        assert not terlik_inst.contains_profanity("namuslu adam")
        assert not terlik_inst.contains_profanity("ahlak dersi")
        assert not terlik_inst.contains_profanity("ahlaki degerler")

    def test_emoji_handling(self, terlik_inst):
        assert terlik_inst.contains_profanity("😡 siktir 😡")
        assert not terlik_inst.contains_profanity("😀😁😂🤣")

    def test_long_input(self, terlik_inst):
        long_clean = "merhaba " * 2000
        assert not terlik_inst.contains_profanity(long_clean)

        t_trunc = Terlik(
            options=type(
                "Opts",
                (),
                {
                    "language": "tr",
                    "max_length": 20,
                    "mode": "balanced",
                    "mask_style": "stars",
                    "enable_fuzzy": False,
                    "fuzzy_threshold": 0.8,
                    "fuzzy_algorithm": "levenshtein",
                    "replace_mask": "[***]",
                    "disable_leet_decode": False,
                    "disable_compound": False,
                    "min_severity": None,
                    "exclude_categories": None,
                    "custom_list": None,
                    "whitelist": None,
                    "extend_dictionary": None,
                    "background_warmup": False,
                },
            )()
        )
        t_trunc.max_length = 20
        text = "a" * 25 + " siktir"
        assert not t_trunc.contains_profanity(text)

    def test_empty_and_special_inputs(self, terlik_inst):
        assert not terlik_inst.contains_profanity("")
        assert terlik_inst.clean("") == ""
        assert terlik_inst.get_matches("") == []

        assert not terlik_inst.contains_profanity("   ")
        assert not terlik_inst.contains_profanity("123456")
        assert not terlik_inst.contains_profanity("!@#$%^&*()")

    def test_turkish_character_variations(self, terlik_inst):
        assert terlik_inst.contains_profanity("SİKTİR")
        assert terlik_inst.contains_profanity("Sİktİr")

    def test_leet_speak_evasion(self, terlik_inst):
        assert terlik_inst.contains_profanity("$1kt1r lan")
        assert terlik_inst.contains_profanity("@pt@l herif")
        assert terlik_inst.contains_profanity("8ok herif")
        assert terlik_inst.contains_profanity("senin 6öt")
        assert terlik_inst.contains_profanity("s2kt2r")

    def test_character_repetition(self, terlik_inst):
        assert terlik_inst.contains_profanity("siiiiiktir")
        assert terlik_inst.contains_profanity("orrrospu")

    def test_separator_evasion(self, terlik_inst):
        assert terlik_inst.contains_profanity("s.i.k.t.i.r")
        assert terlik_inst.contains_profanity("s-i-k-t-i-r")
        assert terlik_inst.contains_profanity("s_i_k_t_i_r")

    def test_new_variant_detection(self, terlik_inst):
        assert terlik_inst.contains_profanity("aminakoyayim")
        assert terlik_inst.contains_profanity("aminakoydum")
        assert terlik_inst.contains_profanity("aminakoydugumun")
        assert terlik_inst.contains_profanity("bu ne aq")
        assert terlik_inst.contains_profanity("orospucocuklari")
        assert terlik_inst.contains_profanity("gotos herif")
        assert terlik_inst.contains_profanity("yarrani ye")
        assert terlik_inst.contains_profanity("yarragimi")
        assert terlik_inst.contains_profanity("yarragini")
        assert terlik_inst.contains_profanity("sktr lan")

    def test_turkish_number_evasion(self, terlik_inst):
        assert terlik_inst.contains_profanity("s2k herif")
        assert terlik_inst.contains_profanity("s2mle ugras")
        assert not terlik_inst.contains_profanity("2023 yilinda")
        assert not terlik_inst.contains_profanity("skor 2-1 oldu")
        assert not terlik_inst.contains_profanity("100 kisi geldi")
