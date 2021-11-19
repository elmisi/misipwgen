from random import randint


class Syllable:

    def __init__(self, starting: bool, weight: int, sequence: list):
        self.starting = starting
        self.weight = weight
        self.sequence = sequence

    def random(self):
        s = ""
        for i in range(0, self.length()):
            pos = randint(0, len(self.sequence[i]) - 1)
            s += self.sequence[i][pos]
        return s

    def is_usable(self, first_position):
        return not first_position or self.starting

    def length(self):
        return len(self.sequence)

    def __str__(self):
        return "-".join(self.sequence)


# TODO: tests missing
class SyllableCollection(list):

    def __init__(self):
        super(SyllableCollection, self).__init__()
        self.last_syllable_by_length = dict()
        self.max_syllable_length = 0

    def finalize(self):
        self.sort(key=lambda x: (x.length(), str(x)))
        self.last_syllable_by_length = self._last_syllable_by_length()
        self.max_syllable_length = self[-1].length()

    def last_index(self, length):
        """ return last syllables index depending  """
        length = 1 if length < 1 else self.max_syllable_length if length >= self.max_syllable_length else length
        return self.last_syllable_by_length[length]

    def _last_syllable_by_length(self):
        res = dict()
        for i, syllable in enumerate(self):
            res[syllable.length()] = i
        return res