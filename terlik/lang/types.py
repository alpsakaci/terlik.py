from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..dictionary.schema import DictionaryData

@dataclass
class LanguageConfig:
    locale: str
    char_map: Dict[str, str]
    leet_map: Dict[str, str]
    char_classes: Dict[str, str]
    dictionary: DictionaryData
    number_expansions: Optional[List[Tuple[str, str]]] = None
