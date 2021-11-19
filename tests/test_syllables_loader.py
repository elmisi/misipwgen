from unittest import TestCase
from misipwgen.syllables_loader import SyllablesLoader


class SyllablesLoaderTestCase(TestCase):
    def test_ignore_row(self):

        for row, expected in [
            ([], True),
            (["#"], True),
            (["xyz"], False),
        ]:
            with self.subTest(row=row):
                self.assertEqual(SyllablesLoader._ignore_row(row), expected)

    def test_only_data(self):

        rows = iter([[], ["xyz"], ["#"]])
        only_data_rows = list(SyllablesLoader(None)._only_data(rows))
        self.assertEqual(only_data_rows, [["xyz"]])

    def test_load(self):

        loader = SyllablesLoader("tests/fixtures/syllables.csv")
        syllables = loader.load()

        self.assertEqual(
            [str(s) for s in syllables],
            ["aeiou", "b-a", "b-r-aeiou", "n-v-aeiou", "t-t-r-aeiou"],
        )
