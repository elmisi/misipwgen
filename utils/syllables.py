from random import randint


class Syllable:

    def __init__(self):
        self.starting = False
        self.weight = 0
        self.letters = list()

    def from_row(self, row):
        self.starting = int(row[0]) == 1
        self.weight = int(row[1])
        self.letters = row[2:]

        return self

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
