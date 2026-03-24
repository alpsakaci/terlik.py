# terlik

> **Note:** This is the Python port of the original [terlik.js](https://github.com/badursun/terlik.js) project.

Multi-language profanity detection and filtering engine for Python. Designed Turkish-first and **extensible to any language**. Not a naive blacklist — a multi-layered normalization and pattern engine that catches what simple string matching misses.

Ships with **Turkish** (flagship, full coverage), **English**, **Spanish**, and **German** built-in. Add any language easily, or extend at runtime via `extend_dictionary`.

> **Turkçe:** Türkçe öncelikli, her dile genişletilebilir küfür tespit ve filtreleme motoru. Leet speak, karakter tekrarı, ayırıcı karakterler ve Türkçe ek sistemi desteği ile yaratıcı küfür denemelerini yakalar. Typed, hızlı ve modern Python tasarımı.

## Features

- **Extensible to any language** — ships with TR/EN/ES/DE, add more via language packs
- Catches leet speak, separators, char repetition, mixed case, zero-width chars
- Turkish suffix engine (83 suffixes, ~10,000+ detectable forms from 147 roots)
- Three detection modes: strict, balanced, loose (with fuzzy matching)
- Fully typed with Python type hints for great IDE support
- Lazy compilation: regex patterns are compiled on first use
- ReDoS-safe regex patterns with timeout safety net
- Background thread warmup support available

## Why terlik?

Turkish profanity evasion is creative. Users write `s2k`, `$1kt1r`, `s.i.k.t.i.r`, `SİKTİR`, `siiiiiktir`, `i8ne`, `or*spu`, `pu$ttt`, `6öt` — and expect to get away with it. Turkish is agglutinative — a single root like `sik` spawns dozens of forms: `siktiler`, `sikerim`, `siktirler`, `sikimsonik`. Manually listing every variant doesn't scale.

`terlik` catches all of these with a **suffix engine** that automatically recognizes Turkish grammatical suffixes on profane roots. Here's what a single call handles:

```python
from terlik import Terlik

terlik = Terlik()
cleaned = terlik.clean("s2mle yüzle$ g0t_v3r3n o r o s p u pezev3nk i8ne pu$ttt or*spu")
print(cleaned)
# "***** yüzle$ ********* *********** ******** **** ****** ******"
```

## Install

```bash
pip install terlik
```

*(Note: Requires Python 3.9 or higher)*

## Quick Start

```python
from terlik import Terlik
from terlik.types import TerlikOptions

# Turkish (default)
tr = Terlik()
tr.contains_profanity("siktir git")  # True
tr.clean("siktir git burdan")        # "****** git burdan"

# English
en = Terlik(TerlikOptions(language="en"))
en.contains_profanity("what the fuck") # True
en.contains_profanity("siktir git")    # False (Turkish not loaded in English setup)

# Spanish & German
es = Terlik(TerlikOptions(language="es"))
de = Terlik(TerlikOptions(language="de"))
es.contains_profanity("hijo de puta")  # True
de.contains_profanity("scheiße")       # True
```

## What It Catches

| Evasion technique      | Example                                                | Detected as         |
| ---------------------- | ------------------------------------------------------ | ------------------- |
| Plain text             | `siktir`                                               | sik                 |
| Turkish İ/I            | `SİKTİR`                                               | sik                 |
| Leet speak             | `$1kt1r`, `@pt@l`                                      | sik, aptal          |
| Visual leet (TR)       | `8ok`, `6öt`, `i8ne`, `s2k`                            | bok, göt, ibne, sik |
| Turkish number words   | `s2mle` (s+iki+mle)                                    | sik (sikimle)       |
| Separators             | `s.i.k.t.i.r`, `s_i_k`                                 | sik                 |
| Spaces                 | `o r o s p u`                                          | orospu              |
| Char repetition        | `siiiiiktir`, `pu$ttt`                                 | sik, puşt           |
| Mixed punctuation      | `or*spu`, `g0t_v3r3n`                                  | orospu, göt         |
| Combined               | `$1kt1r g0t_v3r3n`                                     | both caught         |
| **Suffix forms**       | `siktiler`, `orospuluk`, `gotune`                      | sik, orospu, göt    |
| **Suffix + evasion**   | `s.i.k.t.i.r.l.e.r`, `$1kt1rler`                       | sik                 |
| **Suffix chaining**    | `siktirler` (sik+tir+ler)                              | sik                 |
| **Deep agglutination** | `siktiğimin`, `sikermisiniz`, `siktirmişcesine`        | sik                 |
| **Zero-width chars**   | `s\u200Bi\u200Bk\u200Bt\u200Bi\u200Br` (ZWSP/ZWNJ/ZWJ) | sik                 |

### What It Doesn't Catch (on purpose)

Whitelist prevents false positives on legitimate words:

```python
terlik.contains_profanity("Amsterdam")   # False
terlik.contains_profanity("sikke")       # False (Ottoman coin)
terlik.contains_profanity("ambulans")    # False
terlik.contains_profanity("siklet")      # False (boxing weight class)
terlik.contains_profanity("memur")       # False
```

## Options

Configure `Terlik` with `TerlikOptions`:

```python
from terlik import Terlik
from terlik.types import TerlikOptions

options = TerlikOptions(
    language="tr",                # built-in: "tr" | "en" | "es" | "de" (default: "tr")
    mode="balanced",              # "strict" | "balanced" | "loose"
    mask_style="stars",           # "stars" | "partial" | "replace"
    replace_mask="[***]",         # mask text for "replace" style
    custom_list=["customword"],   # additional words to detect
    whitelist=["safeword"],       # additional words to whitelist
    enable_fuzzy=False,           # enable fuzzy matching
    fuzzy_threshold=0.8,          # similarity threshold (0-1)
    fuzzy_algorithm="levenshtein",# "levenshtein" | "dice"
    max_length=10000,             # truncate input beyond this characters
    background_warmup=False,      # compile patterns in background thread
    extend_dictionary=None,       # DictionaryData object to merge
    disable_leet_decode=False,    # skip leet-speak decoding
    disable_compound=False,       # skip CamelCase decompounding pass
)

terlik = Terlik(options)
```

## Detection Modes

| Mode       | What it does                                               | Best for                         |
| ---------- | ---------------------------------------------------------- | -------------------------------- |
| `strict`   | Normalize + exact match only                               | Minimum false positives          |
| `balanced` | Normalize + pattern matching with separator/leet tolerance | **General use (default)**        |
| `loose`    | Pattern + fuzzy matching (Levenshtein or Dice)             | Maximum coverage, typo tolerance |

## Dictionary Strategy

terlik ships with a **deliberately narrow dictionary** — the goal is to **minimize false positives** while catching real-world evasion patterns. A root like `sik` with 83 possible suffixes, leet decoding, separator tolerance, and repeat collapse produces thousands of detectable surface forms.

```python
# Add domain-specific words
terlik.add_words(["customSlang", "anotherWord"])

# Or at construction time
terlik = Terlik(TerlikOptions(
    custom_list=["customSlang", "anotherWord"],
    whitelist=["legitimateWord"],
))

# Remove a built-in word if it causes false positives in your domain
terlik.remove_words(["damn"])
```

## API

### `terlik.contains_profanity(text: str, options: Optional[DetectOptions] = None) -> bool`

Quick boolean check. Runs full detection internally and returns `True` if any match exists.

### `terlik.get_matches(text: str, options: Optional[DetectOptions] = None) -> List[MatchResult]`

Returns all matches with details:

```python
# MatchResult DataClass Details:
# match.word      (str) -> matched text from original input
# match.root      (str) -> dictionary root word
# match.index     (int) -> position in original text
# match.severity  (Severity) -> "high" | "medium" | "low"
# match.category  (Category) -> "sexual" | "insult" | "slur" | "general"
# match.method    (MatchMethod) -> "exact" | "pattern" | "fuzzy"
```

### `terlik.clean(text: str, options: Optional[CleanOptions] = None) -> str`

Returns text with profanity masked. Three styles:

```python
terlik.clean("siktir git")                                            # "****** git"
terlik.clean("siktir git", CleanOptions(mask_style="partial"))        # "s****r git"
terlik.clean("siktir git", CleanOptions(mask_style="replace", replace_mask="[küfür]")) # "[küfür] git"
```

### `Terlik.warmup(languages: Optional[List[str]] = None, base_options: Optional[TerlikOptions] = None) -> Dict[str, Terlik]`

Static method. Creates and warm-ups instances for multiple languages at once.

```python
cache = Terlik.warmup(["tr", "en", "es", "de"])
cache["en"].contains_profanity("fuck") # True — instantly ready without cold starts
```

## Testing & Contributing

If you'd like to contribute word lists or logic:

```bash
# Set up a venv and install dependencies
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest
```

Pre-commit hooks and type checking (via `mypy`) ensure code quality.

## License

MIT
