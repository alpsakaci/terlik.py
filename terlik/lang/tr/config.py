import json
import os
from ..types import LanguageConfig
from ...dictionary.schema import validate_dictionary

_DIR = os.path.dirname(os.path.abspath(__file__))
_DICT_PATH = os.path.join(_DIR, "dictionary.json")

with open(_DICT_PATH, "r", encoding="utf-8") as f:
    _raw_dict = json.load(f)

validated_data = validate_dictionary(_raw_dict)

config = LanguageConfig(
    locale="tr",
    char_map={
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ı": "i",
        "İ": "i",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
    },
    leet_map={
        "0": "o",
        "1": "i",
        "2": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "6": "g",
        "7": "t",
        "8": "b",
        "9": "g",
        "@": "a",
        "$": "s",
        "!": "i",
    },
    char_classes={
        "a": "[a4àáâãäå]",
        "b": "[b8ß]",
        "c": "[cçÇ]",
        "d": "[d]",
        "e": "[e3èéêë]",
        "f": "[f]",
        "g": "[gğĞ69]",
        "h": "[h]",
        "i": "[iıİ12ìíîï]",
        "j": "[j]",
        "k": "[k]",
        "l": "[l1]",
        "m": "[m]",
        "n": "[nñ]",
        "o": "[o0öÖòóôõ]",
        "p": "[p]",
        "q": "[qk]",
        "r": "[r]",
        "s": "[s5şŞß]",
        "t": "[t7]",
        "u": "[uüÜùúûv]",
        "v": "[vu]",
        "w": "[w]",
        "x": "[x]",
        "y": "[y]",
        "z": "[z2]",
    },
    number_expansions=[
        ("100", "yuz"),
        ("50", "elli"),
        ("10", "on"),
        ("2", "iki"),
    ],
    dictionary=validated_data,
)
