from typing import Callable, Set


def levenshtein_distance(a: str, b: str) -> int:
    m = len(a)
    n = len(b)

    if m == 0:
        return n
    if n == 0:
        return m

    prev = list(range(n + 1))
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,  # deletion
                curr[j - 1] + 1,  # insertion
                prev[j - 1] + cost,  # substitution
            )
        prev, curr = curr, prev

    return prev[n]


def levenshtein_similarity(a: str, b: str) -> float:
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    return 1.0 - levenshtein_distance(a, b) / max_len


def _bigrams(s: str) -> Set[str]:
    return {s[i : i + 2] for i in range(len(s) - 1)}


def dice_similarity(a: str, b: str) -> float:
    if len(a) < 2 or len(b) < 2:
        return 1.0 if a == b else 0.0

    bigrams_a = _bigrams(a)
    bigrams_b = _bigrams(b)

    intersection = sum(1 for bg in bigrams_a if bg in bigrams_b)

    return (2.0 * intersection) / (len(bigrams_a) + len(bigrams_b))


def get_fuzzy_matcher(algorithm: str) -> Callable[[str, str], float]:
    if algorithm == "levenshtein":
        return levenshtein_similarity
    elif algorithm == "dice":
        return dice_similarity
    raise ValueError(f"Unknown algorithm: {algorithm}")
