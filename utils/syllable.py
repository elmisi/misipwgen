from random import randint


class Syllable:

    def __init__(self, starting: bool, weight: int, letters: list):
        self.starting = starting
        self.weight = weight
        self.letters = letters

    def random(self):
        s = ""
        for i in range(0, self.length()):
            pos = randint(0, len(self.letters[i])-1)
            s += self.letters[i][pos]
        return s

    def length(self):
        return len(self.letters)

    def __str__(self):
        return f"{self.starting} {self.weight} {self.letters}"
