import pytest
import string
from terlik.dictionary.schema import validate_dictionary
from terlik.lang.tr.config import _raw_dict as trData


class TestDictionary:
    def test_validates_actual_tr_json(self):
        try:
            validate_dictionary(trData)
        except Exception as e:
            pytest.fail(f"validate_dictionary raised Exception: {e}")

    def test_valid_version(self):
        assert trData["version"] >= 1

    def test_has_entries(self):
        assert isinstance(trData["entries"], list)
        assert len(trData["entries"]) > 0

    def test_has_whitelist(self):
        assert isinstance(trData["whitelist"], list)
        assert len(trData["whitelist"]) > 0

    def test_has_suffixes(self):
        assert isinstance(trData["suffixes"], list)

    def test_entries_validity(self):
        for entry in trData["entries"]:
            assert len(entry["root"]) > 0

        roots = [e["root"].lower() for e in trData["entries"]]
        unique_roots = set(roots)
        assert len(roots) == len(unique_roots)

        valid_severities = {"high", "medium", "low"}
        for entry in trData["entries"]:
            assert entry["severity"] in valid_severities

        valid_categories = {"sexual", "insult", "slur", "general"}
        for entry in trData["entries"]:
            if entry.get("category"):
                assert entry["category"] in valid_categories

        for entry in trData["entries"]:
            assert isinstance(entry["suffixable"], bool)
            assert isinstance(entry["variants"], list)

    def test_whitelist_integrity(self):
        wl = {w.lower() for w in trData["whitelist"]}
        assert "amsterdam" in wl
        assert "sikke" in wl
        assert "bokser" in wl
        assert "malzeme" in wl
        assert "memur" in wl


class TestDictionaryRejection:
    def test_reject_null(self):
        with pytest.raises(ValueError):
            validate_dictionary(None)

    def test_reject_missing_version(self):
        with pytest.raises(ValueError, match="version"):
            validate_dictionary({"suffixes": [], "entries": [], "whitelist": []})

    def test_reject_duplicate_roots(self):
        with pytest.raises(ValueError, match="duplicate root"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": [],
                    "whitelist": [],
                    "entries": [
                        {
                            "root": "test",
                            "variants": [],
                            "severity": "high",
                            "category": "general",
                            "suffixable": False,
                        },
                        {
                            "root": "test",
                            "variants": [],
                            "severity": "low",
                            "category": "insult",
                            "suffixable": False,
                        },
                    ],
                }
            )

    def test_reject_invalid_severity(self):
        with pytest.raises(ValueError, match="severity"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": [],
                    "whitelist": [],
                    "entries": [
                        {
                            "root": "test",
                            "variants": [],
                            "severity": "extreme",
                            "category": "general",
                            "suffixable": False,
                        }
                    ],
                }
            )

    def test_reject_invalid_category(self):
        with pytest.raises(ValueError, match="category"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": [],
                    "whitelist": [],
                    "entries": [
                        {
                            "root": "test",
                            "variants": [],
                            "severity": "high",
                            "category": "unknown",
                            "suffixable": False,
                        }
                    ],
                }
            )

    def test_reject_empty_root(self):
        with pytest.raises(ValueError, match="root"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": [],
                    "whitelist": [],
                    "entries": [
                        {
                            "root": "",
                            "variants": [],
                            "severity": "high",
                            "category": "general",
                            "suffixable": False,
                        }
                    ],
                }
            )

    def test_reject_invalid_suffix_format(self):
        with pytest.raises(ValueError, match="(?i)suffix"):
            validate_dictionary(
                {"version": 1, "suffixes": ["ABC"], "entries": [], "whitelist": []}
            )

    def test_reject_long_suffix(self):
        with pytest.raises(ValueError, match="(?i)suffix"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": ["abcdefghijk"],
                    "entries": [],
                    "whitelist": [],
                }
            )

    def test_reject_too_many_suffixes(self):
        # generate > 150 suffixes
        suffixes = [f"suf{i}" for i in range(151)]
        with pytest.raises(ValueError, match="maximum"):
            validate_dictionary(
                {"version": 1, "suffixes": suffixes, "entries": [], "whitelist": []}
            )

    def test_reject_empty_whitelist_entry(self):
        with pytest.raises(ValueError, match="(?i)(empty|must not be empty)"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": [],
                    "entries": [],
                    "whitelist": ["valid", ""],
                }
            )

    def test_reject_duplicate_whitelist(self):
        with pytest.raises(ValueError, match="duplicate"):
            validate_dictionary(
                {
                    "version": 1,
                    "suffixes": [],
                    "entries": [],
                    "whitelist": ["word", "word"],
                }
            )
