import pytest
from terlik.dictionary.schema import merge_dictionaries, DictionaryData
from terlik.types import WordEntry, TerlikOptions
from terlik.terlik import Terlik

base_dict = DictionaryData(
    version=1,
    suffixes=["ler", "lar"],
    entries=[
        WordEntry(
            root="kötü", variants=[], severity="low", category="insult", suffixable=True
        )
    ],
    whitelist=["safeword"],
)

ext_dict = DictionaryData(
    version=1,
    suffixes=["ler", "ci"],
    entries=[
        WordEntry(
            root="badword",
            variants=["b4dword"],
            severity="high",
            category="general",
            suffixable=False,
        )
    ],
    whitelist=["safeword", "anothersafe"],
)


class TestExtendDictionary:
    def test_merge_dictionaries(self):
        merged = merge_dictionaries(base_dict, ext_dict)
        roots = [e.root for e in merged.entries]
        assert "kötü" in roots
        assert "badword" in roots

        assert "ler" in merged.suffixes
        assert "lar" in merged.suffixes
        assert "ci" in merged.suffixes
        assert merged.suffixes.count("ler") == 1

        assert "safeword" in merged.whitelist
        assert "anothersafe" in merged.whitelist
        assert merged.whitelist.count("safeword") == 1

        assert merged.version == base_dict.version

    def test_extend_dictionary_option(self):
        opts = TerlikOptions(
            extend_dictionary=DictionaryData(
                version=1,
                suffixes=[],
                whitelist=[],
                entries=[
                    WordEntry(
                        root="customcurse",
                        variants=[],
                        severity="high",
                        category="general",
                        suffixable=False,
                    )
                ],
            )
        )
        t = Terlik(opts)
        assert t.contains_profanity("customcurse")
        assert t.contains_profanity("siktir")

    def test_merges_whitelist_from_extension(self):
        opts = TerlikOptions(
            extend_dictionary=DictionaryData(
                version=1, suffixes=[], whitelist=["siklet"], entries=[]
            )
        )
        t = Terlik(opts)
        assert not t.contains_profanity("siklet")

    def test_works_with_custom_list(self):
        opts = TerlikOptions(
            custom_list=["extraword"],
            extend_dictionary=DictionaryData(
                version=1,
                suffixes=[],
                whitelist=[],
                entries=[
                    WordEntry(
                        root="extcurse",
                        variants=[],
                        severity="high",
                        category="general",
                        suffixable=False,
                    )
                ],
            ),
        )
        t = Terlik(opts)
        assert t.contains_profanity("extraword")
        assert t.contains_profanity("extcurse")
        assert t.contains_profanity("siktir")

    def test_detects_variants_from_ext(self):
        opts = TerlikOptions(
            extend_dictionary=DictionaryData(
                version=1,
                suffixes=[],
                whitelist=[],
                entries=[
                    WordEntry(
                        root="testroot",
                        variants=["t3str00t"],
                        severity="high",
                        category="general",
                        suffixable=False,
                    )
                ],
            )
        )
        t = Terlik(opts)
        assert t.contains_profanity("testroot")

    def test_extended_suffixes(self):
        opts = TerlikOptions(
            extend_dictionary=DictionaryData(
                version=1,
                suffixes=["ler", "lar"],
                whitelist=[],
                entries=[
                    WordEntry(
                        root="extword",
                        variants=[],
                        severity="high",
                        category="general",
                        suffixable=True,
                    )
                ],
            )
        )
        t = Terlik(opts)
        assert t.contains_profanity("extword")
        assert t.contains_profanity("extwordler")
