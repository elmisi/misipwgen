from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from bisect import bisect_left
from random import randrange
from typing import Iterable, List, Optional, Sequence


class SyllableCollectionV2(list):
    def __init__(self):
        super().__init__()
        self.last_syllable_by_length = dict()
        self.max_syllable_length = 0

    def finalize(self):
        self.sort(key=lambda x: (x.length(), str(x)))
        self.last_syllable_by_length = dict()
        for i, syllable in enumerate(self):
            self.last_syllable_by_length[syllable.length()] = i
        self.max_syllable_length = self[-1].length()

    def last_index(self, length: int) -> int:
        length = 1 if length < 1 else (self.max_syllable_length if length >= self.max_syllable_length else length)
        return self.last_syllable_by_length[length]


@dataclass
class SyllableV2:
    w_start: int
    w_middle: int
    w_end: int
    sequence: Sequence[str]

    def random(self) -> str:
        from random import randint

        s = ""
        for i in range(0, self.length()):
            pos = randint(0, len(self.sequence[i]) - 1)
            s += self.sequence[i][pos]
        return s

    def length(self) -> int:
        return len(self.sequence)

    def __str__(self) -> str:
        return "-".join(self.sequence)


class SyllablesLoaderV2:
    def __init__(self, file: str):
        self.file = file

    def load(self) -> SyllableCollectionV2:
        import csv

        coll = SyllableCollectionV2()
        with open(self.file, newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file, delimiter=";", quotechar="|")
            for row in reader:
                if not row or (row[0] and row[0].startswith("#")):
                    continue
                # Expect: w_start; w_middle; w_end; seq1; [seq2; ...]
                if len(row) < 4:
                    continue
                try:
                    ws = int(row[0])
                    wm = int(row[1])
                    we = int(row[2])
                except ValueError:
                    continue
                seq = row[3:]
                coll.append(SyllableV2(w_start=ws, w_middle=wm, w_end=we, sequence=seq))
        coll.finalize()
        return coll


class SyllablesLoaderV2Py:
    """Load v2 syllables from a Python module exporting SYLLABLES_V2.

    Expected format:
      SYLLABLES_V2 = [ (w_start, w_middle, w_end, [seq1, seq2, ...]), ... ]
    """

    def __init__(self, module: str, symbol: str = "SYLLABLES_V2"):
        self.module = module
        self.symbol = symbol

    def load(self) -> SyllableCollectionV2:
        coll = SyllableCollectionV2()
        mod = __import__(self.module, fromlist=[self.symbol])
        data = getattr(mod, self.symbol)
        for item in data:
            ws, wm, we, seq = item
            coll.append(SyllableV2(w_start=int(ws), w_middle=int(wm), w_end=int(we), sequence=list(seq)))
        coll.finalize()
        return coll


class CumulativeV2:
    def __init__(self, syllables: Sequence[SyllableV2]):
        # Build cumulative lists aligned to syllable order
        self.cum_start: List[int] = []
        self.cum_middle: List[int] = []
        self.cum_end: List[int] = []
        cs = cm = ce = 0
        for s in syllables:
            cs += max(0, s.w_start)
            cm += max(0, s.w_middle)
            ce += max(0, s.w_end)
            self.cum_start.append(cs)
            self.cum_middle.append(cm)
            self.cum_end.append(ce)

    def weight_at(self, which: str, index: int) -> int:
        if which == "start":
            return self.cum_start[index]
        if which == "middle":
            return self.cum_middle[index]
        if which == "end":
            return self.cum_end[index]
        raise ValueError("which must be start|middle|end")

    def invert(self, which: str, weight: int) -> int:
        arr = self._arr(which)
        idx = bisect_left(arr, weight)
        if idx >= len(arr):
            idx = len(arr) - 1
        return idx

    def invert_in_range(self, which: str, weight: int, lower_index: int, upper_index: int) -> int:
        base = self.weight_at(which, lower_index) if lower_index >= 0 else 0
        target = base + weight
        arr = self._arr(which)
        idx = bisect_left(arr, target, lo=lower_index + 1, hi=upper_index + 1)
        if idx > upper_index:
            idx = upper_index
        return idx

    def _arr(self, which: str) -> List[int]:
        return {"start": self.cum_start, "middle": self.cum_middle, "end": self.cum_end}[which]


class MisiPwGenV2:
    def __init__(self, lang: Optional[str] = None, syllables_path: Optional[str] = None, *, rng=None):
        """Position-aware generator using schema v2 CSV.

        - If `syllables_path` is provided, load that CSV.
        - Else if `lang` is provided, load `misipwgen/data/{lang}/syllables_v2.csv`.
        """
        self.rng = rng

        if syllables_path:
            loader_path = syllables_path
        elif lang:
            # Prefer Python module if present (best performance)
            module_candidates = [
                f"misipwgen.data.{lang}.syllables_v2",
                f"misipwgen.data.{lang}_syllables_v2",
            ]
            loader_path = None
            for module_name in module_candidates:
                try:
                    self.syllables = SyllablesLoaderV2Py(module_name).load()
                    loader_path = None
                    break
                except Exception:
                    continue
            if self.syllables is None or loader_path is not None:
                res = resources.files("misipwgen").joinpath(f"data/{lang}/syllables_v2.csv")
                with resources.as_file(res) as p:
                    loader_path = str(p)
        else:
            raise ValueError("Specify either lang or syllables_path for v2 generator")

        if loader_path:
            self.syllables = SyllablesLoaderV2(loader_path).load()
        self.cumulative = CumulativeV2(self.syllables)

    def generate(self, n: int = 8) -> str:
        word = ""
        residual = n

        while residual > 0:
            first = len(word) == 0
            # Determine length bounds
            last_idx = self.syllables.last_index(residual)

            # If we can finish now, try end-weighted pick among exact-length syllables
            end_idx = self.syllables.last_syllable_by_length.get(residual)
            prev_len_idx = self.syllables.last_syllable_by_length.get(residual - 1, -1)

            picked_index: Optional[int] = None

            if end_idx is not None:
                total_end = self.cumulative.weight_at("end", end_idx) - (
                    self.cumulative.weight_at("end", prev_len_idx) if prev_len_idx >= 0 else 0
                )
                if total_end > 0:
                    rnd = self.rng.randrange if self.rng else randrange
                    w = rnd(1, total_end + 1)
                    picked_index = self.cumulative.invert_in_range("end", w, prev_len_idx, end_idx)

            if picked_index is None:
                which = "start" if first else "middle"
                total = self.cumulative.weight_at(which, last_idx)
                if total == 0:
                    # Fallback to any end if available (shouldn't happen with good data)
                    total = self.cumulative.weight_at("end", last_idx)
                    which = "end"
                    if total == 0:
                        raise GenerationError("No available syllables for current residual")
                rnd = self.rng.randrange if self.rng else randrange
                w = rnd(1, total + 1)
                picked_index = self.cumulative.invert(which, w)

            syllable = self.syllables[picked_index]
            letters = self._render_syllable(syllable)
            word += letters
            residual = n - len(word)

        return word

    # Convenience API parity with legacy
    def phrase(self, *lengths: int, sep: str = "_") -> str:
        if not lengths:
            raise ValueError("Provide at least one length")
        return sep.join(self.generate(int(n)) for n in lengths)

    def sentence(self, total_length: int, sep: str = "_") -> str:
        if total_length < 1:
            raise ValueError("total_length must be >= 1")
        parts = self._partition_length(total_length)
        return self.phrase(*parts, sep=sep)

    @staticmethod
    def _partition_length(n: int) -> list:
        from random import randint
        if n <= 3:
            return [n]
        avg_target = 6
        k = max(2, min(6, n // avg_target + (1 if n % avg_target else 0)))
        base = [n // k] * k
        rem = n % k
        while rem > 0:
            i = randint(0, k - 1)
            base[i] += 1
            rem -= 1
        return [max(1, x) for x in base]

    # Pythonic helpers
    def generate_word(self, length: int = 8) -> str:
        return self.generate(length)

    def generate_words(self, lengths: Iterable[int]) -> list:
        return [self.generate(int(n)) for n in lengths]

    def generate_sentence_parts(self, total_length: int, words: Optional[int] = None) -> list:
        if total_length < 1:
            raise ValueError("total_length must be >= 1")
        if words is not None and words > 0:
            k = words
            base = [total_length // k] * k
            rem = total_length % k
            i = 0
            while rem > 0:
                base[i % k] += 1
                rem -= 1
                i += 1
            return [max(1, x) for x in base]
        return self._partition_length(total_length)

    # Factories
    @classmethod
    def from_language(cls, lang: str, *, rng=None) -> "MisiPwGenV2":
        return cls(lang=lang, rng=rng)

    @classmethod
    def from_csv(cls, path, *, rng=None) -> "MisiPwGenV2":
        return cls(syllables_path=str(path), rng=rng)

    def _render_syllable(self, syllable):
        if self.rng is None:
            return syllable.random()
        letters = ""
        for seq in syllable.sequence:
            idx = self.rng.randrange(0, len(seq))
            letters += seq[idx]
        return letters

class GenerationError(Exception):
    pass

    # Legacy access
    @classmethod
    def legacy(cls, *args, **kwargs):
        # Import lazily to avoid circular import
        from .misipwgen import MisiPwGen as _Legacy

        return _Legacy(*args, **kwargs)
