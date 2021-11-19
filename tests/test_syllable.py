from unittest import TestCase, mock

from utils.syllable import Syllable


class SyllableTestCase(TestCase):

    def test_can_print_syllable(self):
        s = Syllable(starting=True, weight=5, sequence=["abc"])
        self.assertEqual(str(s), "abc")

        s = Syllable(starting=True, weight=5, sequence=["a", "lvrd", "a"])
        self.assertEqual(str(s), "a-lvrd-a")

    def test_syllable_length(self):

        s = Syllable(starting=True, weight=5, sequence=["a", "lvrd", "a"])
        self.assertEqual(s.length(), 3)

        s = Syllable(starting=True, weight=5, sequence=["a", "b", "c", "d"])
        self.assertEqual(s.length(), 4)

    def test_random_generation(self):

        s = Syllable(starting=True, weight=5, sequence=["x", "y", "z"])
        self.assertEqual(s.random(), "xyz")

        s = Syllable(starting=True, weight=5, sequence=["ab", "cd"])
        self.assertIn(s.random(), ["ac", "ad", "bc", "bd"])

        s = Syllable(starting=True, weight=5, sequence=["aei", "lvrd", "aou"])
        with mock.patch("utils.syllable.randint", side_effect=[1, 2, 0]):
            self.assertEqual(s.random(), "era")

    def test_is_usable(self):

        s = Syllable(starting=True, weight=5, sequence=["x"])
        self.assertTrue(s.is_usable(first_position=True))
        self.assertTrue(s.is_usable(first_position=False))

        s = Syllable(starting=False, weight=5, sequence=["x"])
        self.assertFalse(s.is_usable(first_position=True))
        self.assertTrue(s.is_usable(first_position=False))
