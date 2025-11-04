from unittest import TestCase, mock

from misipwgen import MisiPwGen


@mock.patch("misipwgen.misipwgen.SYLLABLES_FILE", "tests/fixtures/syllables2.csv")
class PhraseSentenceTestCase(TestCase):
    def test_phrase_lengths(self):
        pwg = MisiPwGen.legacy()
        out = pwg.phrase(4, 2, 4)
        parts = out.split("_")
        self.assertEqual(len(parts), 3)
        self.assertEqual([len(p) for p in parts], [4, 2, 4])

    def test_sentence_total_length(self):
        pwg = MisiPwGen.legacy()
        total = 12
        out = pwg.sentence(total)
        parts = out.split("_")
        self.assertEqual(sum(len(p) for p in parts), total)
        self.assertTrue(all(len(p) >= 1 for p in parts))
