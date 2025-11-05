from unittest import TestCase, mock

from misipwgen.misipwgen import MisiPwGen


@mock.patch("misipwgen.misipwgen.SYLLABLES_FILE", "tests/fixtures/syllables2.csv")
class MisiPwGenTestCase(TestCase):
    def test_misipwgen_loads_syllables(self):
        # Test default initialization with mocked SYLLABLES_FILE
        pwg = MisiPwGen()

        self.assertEqual([str(s) for s in pwg.syllables], ["b-ae", "c-io", "d-ua", "f-ai"])
        self.assertEqual(pwg.cumulative.cumulative, {0: 5, 1: 10, 2: 15, 3: 20})

    def test_generate(self):
        # Test default initialization with mocked SYLLABLES_FILE
        pwg = MisiPwGen()

        for i in range(100):
            self.assertIn(pwg.generate(4), self._all_combinations())

    def test_init_with_lang_parameter(self):
        """Test initialization with lang parameter"""
        pwg = MisiPwGen(lang="it")
        self.assertIsNotNone(pwg.syllables)
        self.assertTrue(len(pwg.syllables) > 0)

    def test_init_with_syllables_path(self):
        """Test initialization with syllables_path parameter"""
        pwg = MisiPwGen(syllables_path="tests/fixtures/syllables2.csv")
        self.assertEqual([str(s) for s in pwg.syllables], ["b-ae", "c-io", "d-ua", "f-ai"])
        # Test that we can actually use it
        word = pwg.generate(4)
        self.assertEqual(len(word), 4)

    def test_factory_from_language(self):
        """Test from_language factory method"""
        pwg = MisiPwGen.from_language("it")
        self.assertIsNotNone(pwg.syllables)

    def test_factory_from_csv(self):
        """Test from_csv factory method"""
        pwg = MisiPwGen.from_csv("tests/fixtures/syllables2.csv")
        self.assertEqual([str(s) for s in pwg.syllables], ["b-ae", "c-io", "d-ua", "f-ai"])
        # Test that we can actually use it
        word = pwg.generate(4)
        self.assertEqual(len(word), 4)

    def test_phrase_empty_lengths_raises_error(self):
        """Test phrase with no lengths raises ValueError"""
        pwg = MisiPwGen(lang="it")
        with self.assertRaises(ValueError) as ctx:
            pwg.phrase()
        self.assertIn("at least one length", str(ctx.exception))

    def test_phrase_with_lengths(self):
        """Test phrase generation with multiple word lengths"""
        pwg = MisiPwGen(lang="it")
        result = pwg.phrase(4, 4, 4)
        words = result.split("_")
        self.assertEqual(len(words), 3)
        for word in words:
            self.assertEqual(len(word), 4)

    def test_phrase_custom_separator(self):
        """Test phrase with custom separator"""
        pwg = MisiPwGen(lang="it")
        result = pwg.phrase(4, 4, sep="-")
        self.assertIn("-", result)
        self.assertNotIn("_", result)

    def test_sentence_invalid_length_raises_error(self):
        """Test sentence with invalid length raises ValueError"""
        pwg = MisiPwGen(lang="it")
        with self.assertRaises(ValueError) as ctx:
            pwg.sentence(0)
        self.assertIn("must be >= 1", str(ctx.exception))

    def test_sentence_generation(self):
        """Test sentence generation"""
        pwg = MisiPwGen(lang="it")
        result = pwg.sentence(20)
        # Remove separators to count letters
        letters_only = result.replace("_", "")
        self.assertEqual(len(letters_only), 20)

    def test_sentence_custom_separator(self):
        """Test sentence with custom separator"""
        pwg = MisiPwGen(lang="it")
        result = pwg.sentence(20, sep="-")
        self.assertIn("-", result)

    def test_partition_length_small(self):
        """Test _partition_length with small values"""
        result = MisiPwGen._partition_length(1)
        self.assertEqual(result, [1])
        result = MisiPwGen._partition_length(2)
        self.assertEqual(result, [2])
        result = MisiPwGen._partition_length(3)
        self.assertEqual(result, [3])

    def test_partition_length_large(self):
        """Test _partition_length with larger values"""
        result = MisiPwGen._partition_length(30)
        self.assertEqual(sum(result), 30)
        self.assertTrue(2 <= len(result) <= 6)
        self.assertTrue(all(x >= 1 for x in result))

    def test_generate_word(self):
        """Test generate_word helper"""
        pwg = MisiPwGen(lang="it")
        word = pwg.generate_word(6)
        self.assertEqual(len(word), 6)

    def test_generate_words(self):
        """Test generate_words helper"""
        pwg = MisiPwGen(lang="it")
        words = pwg.generate_words([4, 6, 8])
        self.assertEqual(len(words), 3)
        self.assertEqual(len(words[0]), 4)
        self.assertEqual(len(words[1]), 6)
        self.assertEqual(len(words[2]), 8)

    def test_generate_sentence_parts_auto(self):
        """Test generate_sentence_parts without word count"""
        pwg = MisiPwGen(lang="it")
        parts = pwg.generate_sentence_parts(25)
        self.assertEqual(sum(parts), 25)

    def test_generate_sentence_parts_with_words(self):
        """Test generate_sentence_parts with specific word count"""
        pwg = MisiPwGen(lang="it")
        parts = pwg.generate_sentence_parts(20, words=4)
        self.assertEqual(len(parts), 4)
        self.assertEqual(sum(parts), 20)

    def test_generate_sentence_parts_invalid_length(self):
        """Test generate_sentence_parts with invalid length"""
        pwg = MisiPwGen(lang="it")
        with self.assertRaises(ValueError):
            pwg.generate_sentence_parts(0)

    def test_render_syllable_with_rng(self):
        """Test _render_syllable with custom RNG"""
        from random import Random
        rng = Random(42)
        pwg = MisiPwGen(lang="it", rng=rng)
        # Generate a few words to exercise the _render_syllable method
        word1 = pwg.generate(8)
        # Reset the RNG to get the same result
        rng = Random(42)
        pwg2 = MisiPwGen(lang="it", rng=rng)
        word2 = pwg2.generate(8)
        self.assertEqual(word1, word2)

    def test_reject_by_boundary_empty_candidate(self):
        """Test _reject_by_boundary with empty candidate"""
        self.assertTrue(MisiPwGen._reject_by_boundary("ab", "", 2))

    def test_reject_by_boundary_repeated_letter(self):
        """Test _reject_by_boundary rejects repeated boundary letter"""
        self.assertTrue(MisiPwGen._reject_by_boundary("ab", "ba", 2))

    def test_reject_by_boundary_accent_not_final(self):
        """Test _reject_by_boundary rejects accent before final syllable"""
        # Accented vowel in non-final position should be rejected
        self.assertTrue(MisiPwGen._reject_by_boundary("", "pà", 4))

    def test_reject_by_boundary_accent_final(self):
        """Test _reject_by_boundary allows accent in final syllable"""
        # Accented vowel in final position (residual == len(candidate))
        # In this case: current="cit" (3 chars), candidate="tà" (2 chars), residual=2
        # Since residual == len(candidate), this is the final syllable - should be allowed
        # But "t" followed by "t" is repeated, so it should be rejected!
        self.assertTrue(MisiPwGen._reject_by_boundary("cit", "tà", 2))
        # Try with no repeated letter at boundary
        self.assertFalse(MisiPwGen._reject_by_boundary("ci", "tà", 2))

    def test_reject_by_boundary_vowel_vowel_mid(self):
        """Test _reject_by_boundary rejects vowel-vowel in middle"""
        # Vowel followed by vowel in middle position should be rejected
        self.assertTrue(MisiPwGen._reject_by_boundary("ba", "ab", 4))

    def test_reject_by_boundary_vowel_vowel_final(self):
        """Test _reject_by_boundary allows vowel-vowel at end"""
        # Vowel followed by vowel at final position (residual == len(candidate))
        # current="ba", candidate="ab", residual=2
        # "a" followed by "a" is repeated boundary letter - should be rejected first
        self.assertTrue(MisiPwGen._reject_by_boundary("ba", "ab", 2))
        # Try without repeated letter
        self.assertFalse(MisiPwGen._reject_by_boundary("bi", "ao", 2))

    def test_reject_by_boundary_consonant_consonant(self):
        """Test _reject_by_boundary rejects consonant-consonant"""
        self.assertTrue(MisiPwGen._reject_by_boundary("ab", "bc", 4))

    def test_reject_by_boundary_single_vowel_middle(self):
        """Test _reject_by_boundary rejects single vowel in middle"""
        self.assertTrue(MisiPwGen._reject_by_boundary("ab", "a", 4))

    def test_reject_by_boundary_relax_vowel_vowel(self):
        """Test _reject_by_boundary with relax_vowel_vowel flag"""
        # With relax flag, vowel-vowel should be allowed (if not repeated letter)
        # "ba" ending with "a", candidate "ob" starting with "o", residual=4 (not final)
        # Without relax: vowel-vowel in middle should be rejected
        self.assertTrue(MisiPwGen._reject_by_boundary("ba", "ob", 4, relax_vowel_vowel=False))
        # With relax: should be allowed
        self.assertFalse(MisiPwGen._reject_by_boundary("ba", "ob", 4, relax_vowel_vowel=True))

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
