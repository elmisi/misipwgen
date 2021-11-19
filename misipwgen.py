from utils.cumulative import CumulativeDistribution
from utils.syllables_loader import SyllablesLoader

SYLLABLES_FILE = 'syllables.csv'


# TODO: tests missing
class MisiPwGen:

    def __init__(self):
        self.syllables = SyllablesLoader(SYLLABLES_FILE).load()
        self.cumulative = CumulativeDistribution(weights=[s.weight for s in self.syllables])

    def generate(self, n=8):
        word = ""
        residual = n

        while residual > 0:
            max_index = self.syllables.last_index(residual)
            choice = self.cumulative.random_invert(max_index)
            syllable = self.syllables[choice]

            if syllable.is_usable(first_position=(residual == n)):
                syllable_letters = syllable.random()
                if syllable_letters[0] != word[-1:]:
                    word += syllable_letters
                    residual = n - len(word)

        return word
