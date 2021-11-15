import csv

from utils.syllable import Syllable


class SyllablesLoader:

    def __init__(self, file):
        self.file = file

    def load(self):
        res = list()
        with open(self.file, newline='') as csv_file:
            syllable_definitions = csv.reader(csv_file, delimiter=';', quotechar='|')
            for row in self._only_data(syllable_definitions):
                s = Syllable(starting=int(row[0]) == 1, weight=int(row[1]), sequence=row[2:])
                res.append(s)
            res.sort(key=lambda x: (x.length(), str(x)))
        return res

    def _only_data(self, rows):
        for row in rows:
            if self._ignore_row(row):
                continue
            else:
                yield row

    @staticmethod
    def _ignore_row(row):
        return len(row) == 0 or row[0][0] == "#"
