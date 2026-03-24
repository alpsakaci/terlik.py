from typing import Dict, List, Optional, Set
from ..types import DictionaryData, WordEntry

class Dictionary:
    """
    Manages the profanity word list, whitelist, and suffixes for a language.
    """
    def __init__(self, data: DictionaryData, custom_words: Optional[List[str]] = None, custom_whitelist: Optional[List[str]] = None):
        self._entries: Dict[str, WordEntry] = {}
        self._whitelist: Set[str] = {w.lower() for w in data.whitelist}
        self._all_words: List[str] = []
        self._suffixes: List[str] = data.suffixes

        if custom_whitelist:
            for w in custom_whitelist:
                self._whitelist.add(w.lower())
                
        for entry in data.entries:
            self._add_entry(entry)
            
        if custom_words:
            for word in custom_words:
                self._add_entry(WordEntry(
                    root=word.lower(),
                    variants=[],
                    severity="medium",
                    category=None,
                    suffixable=False
                ))

    def _add_entry(self, entry: WordEntry) -> None:
        normalized_root = entry.root.lower()
        self._entries[normalized_root] = entry
        self._all_words.append(normalized_root)
        for v in entry.variants:
            self._all_words.append(v.lower())

    def get_entries(self) -> Dict[str, WordEntry]:
        """Returns all dictionary entries keyed by root word."""
        return self._entries
        
    def get_all_words(self) -> List[str]:
        """Returns all words (roots + variants) as a flat array."""
        return self._all_words
        
    def get_whitelist(self) -> Set[str]:
        """Returns the whitelist as a set of lowercase strings."""
        return self._whitelist
        
    def get_suffixes(self) -> List[str]:
        """Returns available grammatical suffixes for the language."""
        return self._suffixes

    def add_words(self, words: List[str]) -> None:
        """Adds words to the dictionary at runtime."""
        for word in words:
            lower = word.lower().strip()
            if not lower: continue
            if lower not in self._entries:
                self._add_entry(WordEntry(
                    root=lower,
                    variants=[],
                    severity="medium",
                    category=None,
                    suffixable=False
                ))

    def remove_words(self, words: List[str]) -> None:
        """Removes words from the dictionary at runtime."""
        for word in words:
            key = word.lower()
            entry = self._entries.get(key)
            if entry:
                del self._entries[key]
                variants_lower = {v.lower() for v in entry.variants}
                self._all_words = [w for w in self._all_words if w != key and w not in variants_lower]
                
    def find_root_for_word(self, word: str) -> Optional[WordEntry]:
        """Finds the dictionary entry for a given word (checks root and variants)."""
        lower = word.lower()
        direct = self._entries.get(lower)
        if direct:
            return direct
            
        for entry in self._entries.values():
            if any(v.lower() == lower for v in entry.variants):
                return entry
                
        return None
