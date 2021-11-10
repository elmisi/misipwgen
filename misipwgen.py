from random import randint

from utils.syllables_loader import SyllablesLoader

SYLLABLES_FILE = 'syllables.csv'


class MisiPwGen:

    def __init__(self):
        self.syllables = SyllablesLoader(SYLLABLES_FILE).load()
        self.last_syllable_by_length = dict()
        self.cumulative_weights = dict()
        self._init_cumulative()

    def generate(self, n=8):
        word = ""
        residual = n

        while residual > 0:
            first_syllable = residual == n
            last_letter = word[-1:]
            max_weight = self._max_weight(residual)
            index = self._invert(randint(0, max_weight))
            syllable = self.syllables[index]
            if not first_syllable or syllable.starting:
                new_syllable = syllable.random()
                if new_syllable[0] != last_letter:
                    word += new_syllable
                    residual = n - len(word)

        return word

    def _init_cumulative(self):
        last_cum = 0
        for i, syllable in enumerate(self.syllables):
            self.last_syllable_by_length[syllable.length()] = i
            last_cum = self.cumulative_weights[i] = last_cum + syllable.weight

    def _max_weight(self, length):
        """ max cumulative weight depends on residual letters """
        length = 1 if length < 1 else 4 if length > 3 else length
        return self.cumulative_weights[self.last_syllable_by_length[length]]

    def _invert(self, weight):
        """ invert cumulative weights function """
        j = 0
        while self.cumulative_weights[j] < weight and j < len(self.cumulative_weights):
            j += 1
        return j

