from unittest import TestCase, mock

from utils.syllable import Syllable


class SyllableTestCase(TestCase):

    def test_can_print_syllable(self):

        s = Syllable(starting=True, weight=5, letters=['a', "lvrd", "a"])
        self.assertEqual(str(s), "True 5 ['a', 'lvrd', 'a']")

    def test_syllable_length(self):

        s = Syllable(starting=True, weight=5, letters=['a', "lvrd", "a"])
        self.assertEqual(s.length(), 3)

    @mock.patch('utils.syllable.randint', side_effect=[1, 2, 0])
    def test_random_generation(self, mock_randint):

        s = Syllable(starting=True, weight=5, letters=['aei', "lvrd", "aou"])
        self.assertEqual(s.random(), 'era')
        mock_randint.assert_called()
