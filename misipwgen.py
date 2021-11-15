from utils.cumulative import CumulativeDistribution
from utils.syllables_loader import SyllablesLoader

SYLLABLES_FILE = 'syllables.csv'


class MisiPwGen:

    def __init__(self):
        self.syllables = SyllablesLoader(SYLLABLES_FILE).load()
        self.last_syllable_by_length = self._last_syllable_by_length()
        self.max_syllable_length = self.syllables[-1].length()
        self.cumulative = CumulativeDistribution(weights=[s.weight for s in self.syllables])

    def generate(self, n=8):
        word = ""
        residual = n

        while residual > 0:
            first_syllable = residual == n
            last_letter = word[-1:]

            max_index = self._last_index(residual)
            choice = self.cumulative.random_invert(max_index)
            syllable = self.syllables[choice]

            if syllable.apply(first_syllable):
                syllable_letters = syllable.random()
                if syllable_letters[0] != last_letter:
                    word += syllable_letters
                    residual = n - len(word)

        return word

    def _last_syllable_by_length(self):
        res = dict()
        for i, syllable in enumerate(self.syllables):
            res[syllable.length()] = i
        return res

    def _last_index(self, length):
        """ return last syllables index depending  """
        length = 1 if length < 1 else self.max_syllable_length if length >= self.max_syllable_length else length
        return self.last_syllable_by_length[length]


