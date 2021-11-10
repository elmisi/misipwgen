import csv

from utils.syllable import Syllable


class SyllablesLoader:

    def __init__(self, file):
        self.file = file

    def load(self):
        res = list()
        with open(self.file, newline='') as csv_file:
            syllables = csv.reader(csv_file, delimiter=';', quotechar='|')
            for row in self._only_data(syllables):
                s = Syllable(
                    starting=int(row[0]) == 1,
                    weight=int(row[1]),
                    letters=row[2:]
                )
                res.append(s)
        return res

    def _only_data(self, iterable):
        for row in iterable:
            if self._ignore_row(row):
                continue
            else:
                yield row

    @staticmethod
    def _ignore_row(row):
        return len(row) == 0 or row[0][0] == "#"
