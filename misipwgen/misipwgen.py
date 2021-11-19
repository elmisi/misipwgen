from random import randint

from .cumulative import CumulativeDistribution
from .settings import SYLLABLES_FILE
from .syllables_loader import SyllablesLoader


class MisiPwGen:

    def __init__(self):
        self.syllables = SyllablesLoader(SYLLABLES_FILE).load()
        self.cumulative = CumulativeDistribution(weights=[s.weight for s in self.syllables])

    def generate(self, n=8):
        word = ""
        residual = n

        while residual > 0:
            syllable = self._random_syllable(residual)

            if syllable.is_usable(first_position=(residual == n)):
                syllable_letters = syllable.random()
                if syllable_letters[0] != word[-1:]:
                    word += syllable_letters
                    residual = n - len(word)

        return word

    def _random_syllable(self, residual):
        index = self.syllables.last_index(residual)
        max_weight = self.cumulative.weight_at(index)
        weight = randint(0, max_weight)
        choice = self.cumulative.invert(weight)
        return self.syllables[choice]
