import pytest
from terlik import Terlik
from terlik.lang.tr import config as tr_config
from terlik.lang import get_language_config, get_supported_languages


class TestEntryPoints:
    def test_turkish_entry(self):
        from terlik.types import TerlikOptions

        t = Terlik(TerlikOptions(language="tr"))
        assert t.contains_profanity("siktir")
        assert not t.contains_profanity("merhaba")
        assert t.clean("siktir git") != "siktir git"
        assert t.language == "tr"

    def test_tr_config(self):
        assert tr_config is not None
        assert tr_config.locale == "tr"
        assert tr_config.dictionary is not None

    def test_get_supported_languages(self):
        langs = get_supported_languages()
        assert "tr" in langs

    def test_get_language_config(self):
        cfg = get_language_config("tr")
        assert cfg.locale == "tr"

    def test_unsupported_language(self):
        with pytest.raises(Exception):
            get_language_config("xx")

    def test_warmup(self):
        cache = Terlik.warmup(["tr"])
        assert len(cache) == 1
        assert cache["tr"].contains_profanity("siktir")
