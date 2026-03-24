from ...dictionary.schema import validate_dictionary
import json
import os
from ..types import LanguageConfig

_dict_path = os.path.join(os.path.dirname(__file__), "dictionary.json")
with open(_dict_path, "r", encoding="utf-8") as f:
    _raw_dict = json.load(f)

validated_data = validate_dictionary(_raw_dict)

config = LanguageConfig(
    locale="de",
    char_map={
        "ä": "a",
        "Ä": "a",
        "ö": "o",
        "Ö": "o",
        "ü": "u",
        "Ü": "u",
        "ß": "ss",
    },
    leet_map={
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
        "!": "i",
    },
    char_classes={
        "a": "[a4äÄ]",
        "b": "[b8]",
        "c": "[c]",
        "d": "[d]",
        "e": "[e3]",
        "f": "[f]",
        "g": "[g9]",
        "h": "[h]",
        "i": "[i1]",
        "j": "[j]",
        "k": "[k]",
        "l": "[l1]",
        "m": "[m]",
        "n": "[n]",
        "o": "[o0öÖ]",
        "p": "[p]",
        "q": "[q]",
        "r": "[r]",
        "s": "[s5ß]",
        "t": "[t7]",
        "u": "[uvüÜ]",
        "v": "[vu]",
        "w": "[w]",
        "x": "[x]",
        "y": "[y]",
        "z": "[z]",
    },
    dictionary=validated_data,
    number_expansions=[],
)
