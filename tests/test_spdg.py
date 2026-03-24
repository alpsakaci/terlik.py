import pytest
import os
import json
from terlik.terlik import Terlik

SPDG_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "tools",
    "Synthetic-Profanity-Dataset-Generator",
    "output",
)
LANGUAGES = ["tr"]

POSITIVE_THRESHOLDS = {
    "easy": 85,
    "medium": 70,
    "hard": 40,
    "extreme": None,
}
FALSE_POSITIVE_LIMIT = 5


def parse_jsonl(file_path):
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


class TestSPDGA:
    def test_spdg(self):
        for lang in LANGUAGES:
            file_path = os.path.join(SPDG_OUTPUT_DIR, f"export-{lang}.jsonl")
            if not os.path.exists(file_path):
                continue

            entries = parse_jsonl(file_path)
            t = Terlik(
                options=type(
                    "Opts", (), {**Terlik().options.__dict__, "language": lang}
                )()
            )

            positives = [e for e in entries if e["label"] == 1]
            negatives = [e for e in entries if e["label"] == 0]

            by_difficulty = {}
            for e in positives:
                diff = e["difficulty"]
                if diff not in by_difficulty:
                    by_difficulty[diff] = []
                by_difficulty[diff].append(e)

            # Test positives
            for diff, group in by_difficulty.items():
                detected = sum(1 for e in group if t.contains_profanity(e["text"]))
                rate = (detected / len(group)) * 100
                threshold = POSITIVE_THRESHOLDS.get(diff)
                if threshold is not None:
                    assert (
                        rate >= threshold
                    ), f"[{lang.upper()}] {diff} detection rate {rate:.1f}% < threshold {threshold}%"

            # Test negatives
            if negatives:
                false_positives = sum(
                    1 for e in negatives if t.contains_profanity(e["text"])
                )
                fp_rate = (false_positives / len(negatives)) * 100
                assert (
                    fp_rate < FALSE_POSITIVE_LIMIT
                ), f"[{lang.upper()}] False positive rate {fp_rate:.1f}% >= {FALSE_POSITIVE_LIMIT}%"
