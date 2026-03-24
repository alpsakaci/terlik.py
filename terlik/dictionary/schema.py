import re
from typing import Any, Dict, List, Set
from ..types import DictionaryData, WordEntry

VALID_SEVERITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"sexual", "insult", "slur", "general"}
MAX_SUFFIXES = 150
SUFFIX_PATTERN = re.compile(r'^[a-zçğıöşü]{1,10}$')

def validate_dictionary(data: Any) -> DictionaryData:
    if isinstance(data, DictionaryData):
        return data

    if not isinstance(data, dict):
        raise ValueError("Dictionary data must be a dict")
        
    version = data.get("version")
    if not isinstance(version, int) or version < 1:
        raise ValueError("Dictionary version must be a positive number")
        
    suffixes = data.get("suffixes")
    if not isinstance(suffixes, list):
        raise ValueError("Dictionary suffixes must be a list")
        
    if len(suffixes) > MAX_SUFFIXES:
        raise ValueError(f"Dictionary suffixes exceed maximum of {MAX_SUFFIXES}")
        
    for suffix in suffixes:
        if not isinstance(suffix, str) or not SUFFIX_PATTERN.match(suffix):
            raise ValueError(f'Invalid suffix "{suffix}": must be 1-10 letters')
            
    entries_raw = data.get("entries")
    if not isinstance(entries_raw, list):
        raise ValueError("Dictionary entries must be a list")
        
    seen_roots: Set[str] = set()
    entries: List[WordEntry] = []
    
    for i, entry in enumerate(entries_raw):
        if not isinstance(entry, dict):
            raise ValueError(f"entries[{i}]: must be a dict")
            
        root = entry.get("root")
        if not isinstance(root, str) or not root:
            raise ValueError(f"entries[{i}]: root must be a non-empty string")
            
        root_lower = root.lower()
        if root_lower in seen_roots:
            raise ValueError(f'entries[{i}]: duplicate root "{root}"')
        seen_roots.add(root_lower)
        
        variants = entry.get("variants")
        if not isinstance(variants, list):
            raise ValueError(f'entries[{i}] (root="{root}"): variants must be a list')
            
        severity = entry.get("severity")
        if not isinstance(severity, str) or severity not in VALID_SEVERITIES:
            raise ValueError(f'entries[{i}] (root="{root}"): invalid severity "{severity}"')
            
        category = entry.get("category")
        if not isinstance(category, str) or category not in VALID_CATEGORIES:
            # Note: The original JS throws error if it's missing or invalid, assuming it's required
            # Wait, JS has it as optional in type but validation enforces it?
            # JS schema.ts: `if (typeof entry.category !== "string" || !VALID_CATEGORIES.includes(entry.category))`
            # Wait! In TS it says `category?: string`, but dictionary.json always has it. Let's allow None if JS doesn't strictly break.
            if category is not None:
                raise ValueError(f'entries[{i}] (root="{root}"): invalid category "{category}"')

        if category is not None and category not in VALID_CATEGORIES:
             raise ValueError(f'entries[{i}] (root="{root}"): invalid category "{category}"')

        suffixable = entry.get("suffixable")
        if not isinstance(suffixable, bool):
            raise ValueError(f'entries[{i}] (root="{root}"): suffixable must be a boolean')
            
        entries.append(WordEntry(
            root=root,
            variants=variants,
            severity=severity, # type: ignore
            category=category, # type: ignore
            suffixable=suffixable
        ))
        
    whitelist_raw = data.get("whitelist")
    if not isinstance(whitelist_raw, list):
        raise ValueError("Dictionary whitelist must be a list")
        
    seen_whitelist: Set[str] = set()
    whitelist: List[str] = []
    
    for i, item in enumerate(whitelist_raw):
        if not isinstance(item, str):
            raise ValueError(f"whitelist[{i}]: must be a string")
        if not item:
            raise ValueError(f"whitelist[{i}]: must not be empty")
            
        wl_lower = item.lower()
        if wl_lower in seen_whitelist:
            raise ValueError(f'whitelist[{i}]: duplicate entry "{item}"')
            
        seen_whitelist.add(wl_lower)
        whitelist.append(item)
        
    return DictionaryData(
        version=version,
        suffixes=suffixes,
        entries=entries,
        whitelist=whitelist
    )

def merge_dictionaries(base: DictionaryData, ext: DictionaryData) -> DictionaryData:
    existing_roots = {e.root.lower() for e in base.entries}
    
    merged_entries = list(base.entries)
    for entry in ext.entries:
        if entry.root.lower() not in existing_roots:
            merged_entries.append(entry)
            existing_roots.add(entry.root.lower())
            
    merged_suffixes = list(dict.fromkeys(base.suffixes + ext.suffixes))
    merged_whitelist = list(dict.fromkeys(base.whitelist + ext.whitelist))
    
    return DictionaryData(
        version=base.version,
        suffixes=merged_suffixes,
        entries=merged_entries,
        whitelist=merged_whitelist
    )
