from ...dictionary.schema import validate_dictionary
import json
import os
from ..types import LanguageConfig

_dict_path = os.path.join(os.path.dirname(__file__), "dictionary.json")
with open(_dict_path, "r", encoding="utf-8") as f:
    _raw_dict = json.load(f)

validated_data = validate_dictionary(_raw_dict)

config = LanguageConfig(
    locale="es",
    char_map={
        "ñ": "n",
        "Ñ": "n",
        "á": "a",
        "Á": "a",
        "é": "e",
        "É": "e",
        "í": "i",
        "Í": "i",
        "ó": "o",
        "Ó": "o",
        "ú": "u",
        "Ú": "u",
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
        "a": "[a4áÁ]",
        "b": "[b8]",
        "c": "[c]",
        "d": "[d]",
        "e": "[e3éÉ]",
        "f": "[f]",
        "g": "[g9]",
        "h": "[h]",
        "i": "[i1íÍ]",
        "j": "[j]",
        "k": "[k]",
        "l": "[l1]",
        "m": "[m]",
        "n": "[nñÑ]",
        "o": "[o0óÓ]",
        "p": "[p]",
        "q": "[q]",
        "r": "[r]",
        "s": "[s5]",
        "t": "[t7]",
        "u": "[uvúÚ]",
        "v": "[vu]",
        "w": "[w]",
        "x": "[x]",
        "y": "[y]",
        "z": "[z]",
    },
    dictionary=validated_data,
    number_expansions=[],
)
