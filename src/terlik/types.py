import re
from typing import List, Optional, Union, Dict, Literal
from dataclasses import dataclass

# Profanity severity level
Severity = Literal["high", "medium", "low"]

# Content category for profanity entries
Category = Literal["sexual", "insult", "slur", "general"]

# Numeric ordering for severity comparison
SEVERITY_ORDER: Dict[Severity, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
}

# Detection mode controlling the balance between precision and recall
Mode = Literal["strict", "balanced", "loose"]

# Masking style used when cleaning text
MaskStyle = Literal["stars", "partial", "replace"]

# Fuzzy matching algorithm
FuzzyAlgorithm = Literal["levenshtein", "dice"]

# How a match was detected
MatchMethod = Literal["exact", "pattern", "fuzzy"]


@dataclass
# A single entry in the profanity dictionary
class WordEntry:
    root: str
    variants: List[str]
    severity: Severity
    category: Optional[str] = None
    suffixable: bool = False


@dataclass
class DictionaryData:
    version: int
    suffixes: List[str]
    entries: List[WordEntry]
    whitelist: List[str]


@dataclass
# Configuration options for creating a Terlik instance
class TerlikOptions:
    language: str = "tr"
    mode: Mode = "balanced"
    mask_style: MaskStyle = "stars"
    custom_list: Optional[List[str]] = None
    whitelist: Optional[List[str]] = None
    enable_fuzzy: bool = False
    fuzzy_threshold: float = 0.8
    fuzzy_algorithm: FuzzyAlgorithm = "levenshtein"
    max_length: int = 10000
    replace_mask: str = "[***]"
    background_warmup: bool = False
    extend_dictionary: Optional[DictionaryData] = None
    disable_leet_decode: bool = False
    disable_compound: bool = False
    min_severity: Optional[Severity] = None
    exclude_categories: Optional[List[Category]] = None


@dataclass
# Per-call detection options that override instance defaults
class DetectOptions:
    mode: Optional[Mode] = None
    enable_fuzzy: Optional[bool] = None
    fuzzy_threshold: Optional[float] = None
    fuzzy_algorithm: Optional[FuzzyAlgorithm] = None
    disable_leet_decode: Optional[bool] = None
    disable_compound: Optional[bool] = None
    min_severity: Optional[Severity] = None
    exclude_categories: Optional[List[Category]] = None


@dataclass
# Per-call clean options that override instance defaults
class CleanOptions(DetectOptions):
    mask_style: Optional[MaskStyle] = None
    replace_mask: Optional[str] = None


@dataclass
# A single profanity match found in the input text
class MatchResult:
    word: str
    root: str
    index: int
    severity: Severity
    category: Optional[Category]
    method: MatchMethod


@dataclass
# A compiled regex pattern for a dictionary entry
class CompiledPattern:
    root: str
    severity: Severity
    category: Optional[Category]
    regex: re.Pattern
    variants: List[str]
