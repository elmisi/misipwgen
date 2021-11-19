from unittest import TestCase

from misipwgen.syllable import Syllable
from misipwgen.syllable_collection import SyllableCollection


class SyllableCollectionTestCase(TestCase):
    
    def setUp(self) -> None:
        super(SyllableCollectionTestCase, self).setUp()

        s1 = Syllable(starting=True, weight=10, sequence=["lmd", "a", "mn", "a"])
        s2 = Syllable(starting=True, weight=10, sequence=["lmd", "a"])
        s3 = Syllable(starting=True, weight=10, sequence=["a", "lmd", "a"])

        self.collection = SyllableCollection()
        self.collection.append(s1)
        self.collection.append(s2)
        self.collection.append(s3)

    def test_finalize(self):

        self.collection.finalize()

        self.assertEqual(self.collection.last_syllable_by_length, {2: 0, 3: 1, 4: 2})
        self.assertEqual(self.collection.max_syllable_length, 4)

    def test_last_index(self):

        self.collection.finalize()

        with self.assertRaises(KeyError):
            self.assertEqual(self.collection.last_index(0), 0)

        with self.assertRaises(KeyError):
            self.assertEqual(self.collection.last_index(1), 0)

        self.assertEqual(self.collection.last_index(2), 0)
        self.assertEqual(self.collection.last_index(3), 1)
        self.assertEqual(self.collection.last_index(4), 2)
        self.assertEqual(self.collection.last_index(5), 2)
