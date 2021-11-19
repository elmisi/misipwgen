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
