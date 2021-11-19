from unittest import TestCase, mock

from misipwgen import MisiPwGen


@mock.patch("misipwgen.misipwgen.SYLLABLES_FILE", "tests/fixtures/syllables2.csv")
class MisiPwGenTestCase(TestCase):

    def test_misipwgen_loads_syllables(self):
        pwg = MisiPwGen()

        self.assertEqual([str(s) for s in pwg.syllables],  ['b-ae', 'c-io', 'd-ua', 'f-ai'])
        self.assertEqual(pwg.cumulative.cumulative,  {0: 5, 1: 10, 2: 15, 3: 20})

    def test_generate(self):
        pwg = MisiPwGen()

        for i in range(100):
            self.assertIn(pwg.generate(4), self._all_combinations())

    def _all_combinations(self):
        return [
            "babe",
            "baci",
            "baco",
            "bada",
            "baba",
            "badu",
            "bafa",
            "bafi",
            "beba",
            "bebe",
            "beci",
            "beco",
            "beda",
            "bedu",
            "befa",
            "befi",
            "ciba",
            "cibe",
            "cici",
            "cico",
            "cida",
            "cidu",
            "cifa",
            "cifi",
            "coba",
            "cobe",
            "coci",
            "coco",
            "coda",
            "codu",
            "cofa",
            "cofi",
            "daba",
            "dabe",
            "daci",
            "daco",
            "dada",
            "dadu",
            "dafa",
            "dafi",
            "duba",
            "dube",
            "duci",
            "duco",
            "duda",
            "dudu",
            "dufa",
            "dufi",
            "faba",
            "fabe",
            "faci",
            "faco",
            "fada",
            "fadu",
            "fafa",
            "fafi",
            "fiba",
            "fibe",
            "fici",
            "fico",
            "fida",
            "fidu",
            "fifa",
            "fifi",
        ]
