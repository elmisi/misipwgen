from random import randrange
from typing import Iterable, Optional

from importlib import resources

from .cumulative import CumulativeDistribution
from .settings import SYLLABLES_FILE
from .syllables_loader import SyllablesLoader


class MisiPwGen:
    def __init__(self, lang: Optional[str] = None, syllables_path: Optional[str] = None, *, rng=None):
        """
        Create a password/word generator.

        - If `syllables_path` is provided, load from that CSV (tests can override).
        - Else if `lang` is provided, load package data from `misipwgen/data/{lang}/syllables.csv`.
        - Else fall back to legacy path from settings (`SYLLABLES_FILE`).
        """
        self.rng = rng

        if syllables_path:
            self.syllables = SyllablesLoader(syllables_path).load()
        elif lang:
            res = resources.files("misipwgen").joinpath(f"data/{lang}/syllables.csv")
            # Ensure a real filesystem path (works under zipimport)
            with resources.as_file(res) as p:
                self.syllables = SyllablesLoader(str(p)).load()
        else:
            self.syllables = SyllablesLoader(SYLLABLES_FILE).load()
        self.cumulative = CumulativeDistribution(weights=[s.weight for s in self.syllables])

    def generate(self, n=8):
        word = ""
        residual = n

        attempts = 0
        while residual > 0:
            syllable = self._random_syllable(residual)

            if syllable.is_usable(first_position=(residual == n)):
                syllable_letters = self._render_syllable(syllable)
                if not self._reject_by_boundary(word, syllable_letters, residual):
                    word += syllable_letters
                    residual = n - len(word)
                    attempts = 0
                else:
                    attempts += 1
                    # Safeguard to avoid infinite loops under strict constraints
                    if attempts > 10000:
                        # Relax only the vowel-vowel rule to allow progress
                        if not self._reject_by_boundary(word, syllable_letters, residual, relax_vowel_vowel=True):
                            word += syllable_letters
                            residual = n - len(word)
                            attempts = 0

        return word

    def _random_syllable(self, residual):
        index = self.syllables.last_index(residual)
        max_weight = self.cumulative.weight_at(index)
        rnd = self.rng.randrange if self.rng else randrange
        weight = rnd(1, max_weight + 1)
        choice = self.cumulative.invert(weight)
        return self.syllables[choice]

    @staticmethod
    def _reject_by_boundary(current: str, candidate: str, residual: int, *, relax_vowel_vowel: bool = False) -> bool:
        """Enforce simple pronounceability rules at syllable joins.

        - Avoid doubling the boundary letter.
        - Avoid vowel-vowel and consonant-consonant joins.
        - Accented vowels are only allowed in the final syllable.
        """
        if not candidate:
            return True
        prev = current[-1:] if current else ""
        first = candidate[0]

        # Rule 1: avoid repeated boundary letter
        if prev and first == prev:
            return True

        V = set("aeiouàèéìòóù")
        ACC = set("àèéìòóù")

        # Rule 2: disallow accent before final syllable
        if any(ch in ACC for ch in candidate):
            if residual != len(candidate):
                return True

        # If there is no previous letter, accept
        if not prev:
            return False

        prev_is_v = prev in V
        next_is_v = first in V
        # Rule 3: avoid vowel-vowel and consonant-consonant joins
        # Allow vowel-vowel if this is the final syllable (residual == len(candidate)),
        # or if we are explicitly relaxing this rule to make progress.
        if prev_is_v == next_is_v:
            if next_is_v and (residual == len(candidate) or relax_vowel_vowel):
                return False
            return True

        # Additional guard: disallow single-vowel syllables in middle positions
        if residual != len(candidate) and len(candidate) == 1 and next_is_v:
            return True

        return False

    # --- Phrase/Sentence helpers (feature: sentence mode) ---
    def phrase(self, *lengths: int, sep: str = "_") -> str:
        """Generate multiple words of specified lengths and join with separator.

        Example: phrase(7,2,5,1,8) -> "sarbido_ti_accoa_i_ladrufo"
        """
        if not lengths:
            raise ValueError("Provide at least one length")
        words = [self.generate(int(n)) for n in lengths]
        return sep.join(words)

    def sentence(self, total_length: int, sep: str = "_") -> str:
        """Generate a sentence-like string whose total letters sum to total_length.

        Word count and split are chosen automatically.
        """
        if total_length < 1:
            raise ValueError("total_length must be >= 1")
        parts = self._partition_length(total_length)
        return self.phrase(*parts, sep=sep)

    @staticmethod
    def _partition_length(n: int) -> list:
        """Partition n into 2-6 positive integers, biased around 4-8 per word."""
        from random import randint

        if n <= 3:
            return [n]
        avg_target = 6
        k = max(2, min(6, n // avg_target + (1 if n % avg_target else 0)))
        # start with floor division then distribute remainder randomly
        base = [n // k] * k
        rem = n % k
        while rem > 0:
            i = randint(0, k - 1)
            base[i] += 1
            rem -= 1
        # ensure no zero segments (shouldn't happen) and small jitter
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
            # Evenly partition into the requested number of words
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
    def from_language(cls, lang: str, *, rng=None) -> "MisiPwGen":
        return cls(lang=lang, rng=rng)

    @classmethod
    def from_csv(cls, path, *, rng=None) -> "MisiPwGen":
        return cls(syllables_path=str(path), rng=rng)

    def _render_syllable(self, syllable):
        if self.rng is None:
            return syllable.random()
        # Deterministic per provided RNG
        letters = ""
        for seq in syllable.sequence:
            idx = self.rng.randrange(0, len(seq))
            letters += seq[idx]
        return letters
