"""
Terlik
Multi-language profanity detection and filtering engine.
"""

from .terlik import Terlik
from .core import TerlikCore
from .normalizer import normalize
from .fuzzy import levenshtein_distance, levenshtein_similarity, dice_similarity

__all__ = [
    "Terlik",
    "TerlikCore",
    "normalize",
    "levenshtein_distance",
    "levenshtein_similarity",
    "dice_similarity",
]
