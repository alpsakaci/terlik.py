from ...dictionary.schema import validate_dictionary
import json
import os
from ..types import LanguageConfig

_dict_path = os.path.join(os.path.dirname(__file__), "dictionary.json")
with open(_dict_path, "r", encoding="utf-8") as f:
    _raw_dict = json.load(f)

validated_data = validate_dictionary(_raw_dict)

config = LanguageConfig(
    locale="en",
    char_map={},
    leet_map={
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "6": "g",
        "7": "t",
        "8": "b",
        "@": "a",
        "$": "s",
        "!": "i",
        "#": "h",
    },
    char_classes={
        "a": "[a4]",
        "b": "[b8]",
        "c": "[c]",
        "d": "[d]",
        "e": "[e3]",
        "f": "[fph]",
        "g": "[g96]",
        "h": "[h#]",
        "i": "[i1]",
        "j": "[j]",
        "k": "[k]",
        "l": "[l1]",
        "m": "[m]",
        "n": "[n]",
        "o": "[o0]",
        "p": "[p]",
        "q": "[q]",
        "r": "[r]",
        "s": "[s5]",
        "t": "[t7]",
        "u": "[uv]",
        "v": "[vu]",
        "w": "[w]",
        "x": "[x]",
        "y": "[y]",
        "z": "[z]",
    },
    dictionary=validated_data,
    number_expansions=[],
)
