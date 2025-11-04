from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class LanguagePack:
    code: str
    vowels: str

    def syllabifier(self) -> "Syllabifier":
        if self.code == "it":
            return ItalianSyllabifier(self)
        if self.code == "es":
            return SpanishSyllabifier(self)
        raise ValueError(f"Unsupported language code: {self.code}")


class Syllabifier:
    def __init__(self, lang: LanguagePack):
        self.lang = lang

    def syllabify(self, word: str) -> List[str]:
        raise NotImplementedError

    def tokenize(self, text: str) -> Iterable[str]:
        # Default fallback tokenizer: ASCII letters only
        for token in re.findall(r"[a-zA-Z]+", text.lower()):
            if len(token) > 1:
                yield token


class ItalianSyllabifier(Syllabifier):
    """A pragmatic, rule-light Italian syllabifier.

    Notes:
    - Prioritizes open syllables (CV), allows simple clusters.
    - Intentionally simple and fast; suitable as a starting point.
    - Improve with maximal-onset and cluster tables as needed.
    """

    VOWELS = set("aeiouàèéìòóù")

    SIMPLE_ONSETS: Sequence[str] = (
        # common single consonants
        "b c d f g l m n p r s t v z".split()
        + [
            # frequent clusters (pragmatic subset)
            "br",
            "cr",
            "dr",
            "fr",
            "gr",
            "pr",
            "tr",
            "pl",
            "cl",
            "gl",
            "fl",
            "sc",
            "sp",
            "st",
            "ch",
            "gh",
        ]
    )

    def syllabify(self, word: str) -> List[str]:
        parts: List[str] = []
        i = 0
        n = len(word)
        while i < n:
            # nucleus: at least one vowel; extend over diphthongs
            onset_end = i
            # attach minimal onset (0..2 consonants with allowed cluster)
            if i + 2 <= n and word[i : i + 2] in self.SIMPLE_ONSETS:
                onset_end = i + 2
            elif i + 1 < n and word[i] not in self.VOWELS:
                onset_end = i + 1

            j = onset_end
            # find first vowel for nucleus
            while j < n and word[j] not in self.VOWELS:
                j += 1
            # include vowel(s)
            if j < n:
                j += 1
                if j < n and word[j] in self.VOWELS:
                    j += 1  # allow simple diphthong

            # try to keep next consonant for next onset when possible
            coda_end = j
            if j < n and word[j] not in self.VOWELS:
                # If two consonants ahead and form onset cluster, keep both for next syllable
                if j + 2 <= n and word[j : j + 2] in self.SIMPLE_ONSETS:
                    coda_end = j
                else:
                    # Allow single coda consonant; special-case 's' before stop
                    if word[j] == "s" and j + 1 < n and word[j + 1] not in self.VOWELS:
                        coda_end = j
                    else:
                        coda_end = j + 1

            if coda_end <= i:
                # safety to avoid infinite loops on odd inputs
                coda_end = min(i + 1, n)

            parts.append(word[i:coda_end])
            i = coda_end

        return parts

    def tokenize(self, text: str) -> Iterable[str]:
        # Include Italian accented vowels
        for token in re.findall(r"[a-zàèéìòóù]+", text.lower()):
            if len(token) > 1:
                yield token


class SpanishSyllabifier(Syllabifier):
    """Simplified Spanish syllabifier (pragmatic, CV‑biased).

    Notes:
    - Treats common onset clusters; keeps syllables mostly open (CV/CVC).
    - Handles accented vowels and ü; ñ is a consonant.
    - Not a full phonological model; good enough for syllable statistics.
    """

    VOWELS = set("aeiouáéíóúü")

    SIMPLE_ONSETS: Sequence[str] = (
        "b c d f g l m n p r s t v y z ñ".split()
        + [
            "br",
            "cr",
            "dr",
            "fr",
            "gr",
            "pr",
            "tr",
            "pl",
            "cl",
            "gl",
            "fl",
            "bl",
            "ch",
            # Historical digraphs; treat as permissible onsets
            "ll",
            "rr",
        ]
    )

    def syllabify(self, word: str) -> List[str]:
        parts: List[str] = []
        i = 0
        n = len(word)
        while i < n:
            # onset (allow 0..2 chars if in SIMPLE_ONSETS)
            onset_end = i
            if i + 2 <= n and word[i : i + 2] in self.SIMPLE_ONSETS:
                onset_end = i + 2
            elif i + 1 < n and word[i] not in self.VOWELS:
                onset_end = i + 1

            j = onset_end
            # find first vowel
            while j < n and word[j] not in self.VOWELS:
                j += 1
            # include vowel nucleus (allow simple diphthong)
            if j < n:
                j += 1
                if j < n and word[j] in self.VOWELS:
                    j += 1

            # keep next consonants for the next onset when they form a cluster
            coda_end = j
            if j < n and word[j] not in self.VOWELS:
                if j + 2 <= n and word[j : j + 2] in self.SIMPLE_ONSETS:
                    coda_end = j
                else:
                    coda_end = j + 1

            if coda_end <= i:
                coda_end = min(i + 1, n)

            parts.append(word[i:coda_end])
            i = coda_end

        return parts

    def tokenize(self, text: str) -> Iterable[str]:
        # Include Spanish accents, ü, and ñ
        for token in re.findall(r"[a-záéíóúüñ]+", text.lower()):
            if len(token) > 1:
                yield token


def to_sequence(syllable: str) -> List[str]:
    """Convert a syllable string into generator sequence columns.

    Example: "ba" -> ["b", "a"].
    """
    return list(syllable)
