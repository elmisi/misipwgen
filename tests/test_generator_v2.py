from unittest import TestCase
from unittest.mock import Mock

from misipwgen.generator_v2 import (
    SyllableV2,
    SyllableCollectionV2,
    SyllablesLoaderV2Py,
    CumulativeV2,
    MisiPwGenV2,
    GenerationError,
)


class SyllableV2TestCase(TestCase):
    def test_length(self):
        s = SyllableV2(w_start=1, w_middle=2, w_end=3, sequence=["b", "a"])
        self.assertEqual(s.length(), 2)

        s3 = SyllableV2(w_start=1, w_middle=2, w_end=3, sequence=["str", "a", "n"])
        self.assertEqual(s3.length(), 3)

    def test_str(self):
        s = SyllableV2(w_start=1, w_middle=2, w_end=3, sequence=["b", "a"])
        self.assertEqual(str(s), "b-a")

        s2 = SyllableV2(w_start=1, w_middle=2, w_end=3, sequence=["c", "io", "e"])
        self.assertEqual(str(s2), "c-io-e")

    def test_random(self):
        s = SyllableV2(w_start=1, w_middle=2, w_end=3, sequence=["bcd", "aei"])

        # Run multiple times to verify it generates valid characters
        for _ in range(20):
            result = s.random()
            self.assertEqual(len(result), 2)
            self.assertIn(result[0], "bcd")
            self.assertIn(result[1], "aei")


class SyllableCollectionV2TestCase(TestCase):
    def test_finalize_sorts_by_length_and_str(self):
        coll = SyllableCollectionV2()
        coll.append(SyllableV2(1, 2, 3, ["c", "a", "t"]))  # len 3
        coll.append(SyllableV2(1, 2, 3, ["b", "a"]))       # len 2
        coll.append(SyllableV2(1, 2, 3, ["d", "o", "g"]))  # len 3
        coll.append(SyllableV2(1, 2, 3, ["a"]))            # len 1

        coll.finalize()

        # Should be sorted by length first, then alphabetically
        self.assertEqual(len(coll), 4)
        self.assertEqual(coll[0].length(), 1)
        self.assertEqual(coll[1].length(), 2)
        self.assertEqual(coll[2].length(), 3)
        self.assertEqual(coll[3].length(), 3)
        self.assertEqual(str(coll[2]), "c-a-t")  # "c-a-t" before "d-o-g"
        self.assertEqual(str(coll[3]), "d-o-g")

    def test_last_syllable_by_length(self):
        coll = SyllableCollectionV2()
        coll.append(SyllableV2(1, 2, 3, ["a"]))
        coll.append(SyllableV2(1, 2, 3, ["b", "a"]))
        coll.append(SyllableV2(1, 2, 3, ["c", "o"]))
        coll.append(SyllableV2(1, 2, 3, ["d", "e", "f"]))

        coll.finalize()

        # Index of last syllable of each length
        self.assertEqual(coll.last_syllable_by_length[1], 0)  # last len-1
        self.assertEqual(coll.last_syllable_by_length[2], 2)  # last len-2
        self.assertEqual(coll.last_syllable_by_length[3], 3)  # last len-3

    def test_max_syllable_length(self):
        coll = SyllableCollectionV2()
        coll.append(SyllableV2(1, 2, 3, ["a"]))
        coll.append(SyllableV2(1, 2, 3, ["b", "a", "r", "k"]))

        coll.finalize()

        self.assertEqual(coll.max_syllable_length, 4)

    def test_last_index(self):
        coll = SyllableCollectionV2()
        coll.append(SyllableV2(1, 2, 3, ["a"]))           # len 1, idx 0
        coll.append(SyllableV2(1, 2, 3, ["b", "a"]))      # len 2, idx 1
        coll.append(SyllableV2(1, 2, 3, ["c", "a", "t"])) # len 3, idx 2

        coll.finalize()

        # Should return last index for given length
        self.assertEqual(coll.last_index(1), 0)
        self.assertEqual(coll.last_index(2), 1)
        self.assertEqual(coll.last_index(3), 2)

        # Edge cases: clamp to valid range
        self.assertEqual(coll.last_index(0), 0)   # < 1 -> return idx for len 1
        self.assertEqual(coll.last_index(10), 2)  # > max -> return max


class SyllablesLoaderV2PyTestCase(TestCase):
    def test_load_from_module(self):
        loader = SyllablesLoaderV2Py("tests.fixtures.test_syllables_v2")
        coll = loader.load()

        self.assertIsInstance(coll, SyllableCollectionV2)
        self.assertEqual(len(coll), 10)

        # Verify first syllable loaded correctly
        first = coll[0]
        self.assertEqual(first.w_start, 5)
        self.assertEqual(first.w_middle, 0)
        self.assertEqual(first.w_end, 0)
        self.assertEqual(first.sequence, ["b", "a"])

    def test_load_custom_symbol(self):
        # Default symbol is SYLLABLES_V2
        loader = SyllablesLoaderV2Py("tests.fixtures.test_syllables_v2", symbol="SYLLABLES_V2")
        coll = loader.load()
        self.assertEqual(len(coll), 10)


class CumulativeV2TestCase(TestCase):
    def test_build_cumulative_weights(self):
        syllables = [
            SyllableV2(w_start=10, w_middle=5, w_end=2, sequence=["a"]),
            SyllableV2(w_start=20, w_middle=10, w_end=5, sequence=["b", "a"]),
            SyllableV2(w_start=15, w_middle=8, w_end=3, sequence=["c", "o"]),
        ]

        cum = CumulativeV2(syllables)

        # Check cumulative start weights
        self.assertEqual(cum.cum_start, [10, 30, 45])
        # Check cumulative middle weights
        self.assertEqual(cum.cum_middle, [5, 15, 23])
        # Check cumulative end weights
        self.assertEqual(cum.cum_end, [2, 7, 10])

    def test_ignore_negative_weights(self):
        syllables = [
            SyllableV2(w_start=-5, w_middle=10, w_end=0, sequence=["a"]),
            SyllableV2(w_start=20, w_middle=-3, w_end=5, sequence=["b", "a"]),
        ]

        cum = CumulativeV2(syllables)

        # Negative weights should be treated as 0
        self.assertEqual(cum.cum_start, [0, 20])
        self.assertEqual(cum.cum_middle, [10, 10])
        self.assertEqual(cum.cum_end, [0, 5])

    def test_weight_at(self):
        syllables = [
            SyllableV2(w_start=10, w_middle=5, w_end=2, sequence=["a"]),
            SyllableV2(w_start=20, w_middle=10, w_end=5, sequence=["b", "a"]),
        ]

        cum = CumulativeV2(syllables)

        self.assertEqual(cum.weight_at("start", 0), 10)
        self.assertEqual(cum.weight_at("start", 1), 30)
        self.assertEqual(cum.weight_at("middle", 0), 5)
        self.assertEqual(cum.weight_at("middle", 1), 15)
        self.assertEqual(cum.weight_at("end", 0), 2)
        self.assertEqual(cum.weight_at("end", 1), 7)

    def test_weight_at_invalid_which(self):
        syllables = [SyllableV2(w_start=10, w_middle=5, w_end=2, sequence=["a"])]
        cum = CumulativeV2(syllables)

        with self.assertRaises(ValueError):
            cum.weight_at("invalid", 0)

    def test_invert(self):
        syllables = [
            SyllableV2(w_start=10, w_middle=5, w_end=2, sequence=["a"]),
            SyllableV2(w_start=20, w_middle=10, w_end=5, sequence=["b", "a"]),
            SyllableV2(w_start=15, w_middle=8, w_end=3, sequence=["c", "o"]),
        ]

        cum = CumulativeV2(syllables)

        # Test start weights [10, 30, 45]
        self.assertEqual(cum.invert("start", 1), 0)   # 1 <= 10 -> idx 0
        self.assertEqual(cum.invert("start", 10), 0)  # 10 <= 10 -> idx 0
        self.assertEqual(cum.invert("start", 11), 1)  # 11 > 10 -> idx 1
        self.assertEqual(cum.invert("start", 30), 1)  # 30 <= 30 -> idx 1
        self.assertEqual(cum.invert("start", 31), 2)  # 31 > 30 -> idx 2
        self.assertEqual(cum.invert("start", 100), 2) # Out of range -> last idx

    def test_invert_in_range(self):
        syllables = [
            SyllableV2(w_start=10, w_middle=5, w_end=2, sequence=["a"]),
            SyllableV2(w_start=20, w_middle=10, w_end=5, sequence=["b", "a"]),
            SyllableV2(w_start=15, w_middle=8, w_end=3, sequence=["c", "o"]),
        ]

        cum = CumulativeV2(syllables)

        # Search in range [lower_index, upper_index]
        # start weights: [10, 30, 45]

        # Range from index 0 to 2: weight relative to base at index -1 (=0)
        idx = cum.invert_in_range("start", 5, -1, 2)
        self.assertEqual(idx, 0)  # 0 + 5 = 5 -> idx 0

        # Range from index 1 to 2: weight relative to base at index 0 (=10)
        idx = cum.invert_in_range("start", 5, 0, 2)
        self.assertEqual(idx, 1)  # 10 + 5 = 15 -> idx 1

        idx = cum.invert_in_range("start", 25, 0, 2)
        self.assertEqual(idx, 2)  # 10 + 25 = 35 -> idx 2


class MisiPwGenV2TestCase(TestCase):
    def test_init_with_lang(self):
        gen = MisiPwGenV2(lang="it")
        self.assertIsNotNone(gen.syllables)
        self.assertIsNotNone(gen.cumulative)
        self.assertGreater(len(gen.syllables), 0)

    def test_init_with_syllables_path(self):
        gen = MisiPwGenV2(syllables_path="tests.fixtures.test_syllables_v2")
        self.assertEqual(len(gen.syllables), 10)

    def test_init_without_lang_or_path_raises(self):
        with self.assertRaises(ValueError) as ctx:
            MisiPwGenV2()
        self.assertIn("Specify either lang or syllables_path", str(ctx.exception))

    def test_init_with_invalid_lang_raises(self):
        with self.assertRaises(ValueError) as ctx:
            MisiPwGenV2(lang="invalid_lang_xyz")
        self.assertIn("Could not import", str(ctx.exception))

    def test_generate_basic(self):
        gen = MisiPwGenV2(lang="it")

        word = gen.generate(8)
        self.assertEqual(len(word), 8)
        self.assertTrue(word.isalpha())

    def test_generate_with_fixed_rng(self):
        # Use a mock RNG for deterministic testing
        mock_rng = Mock()
        # Return 0 for index to avoid IndexError with single-char sequences
        mock_rng.randrange = Mock(return_value=0)

        gen = MisiPwGenV2(syllables_path="tests.fixtures.test_syllables_v2", rng=mock_rng)
        word = gen.generate(4)

        # Should generate something (exact value depends on fixture)
        self.assertGreater(len(word), 0)
        self.assertLessEqual(len(word), 4)

    def test_generate_different_lengths(self):
        gen = MisiPwGenV2(lang="it")

        for length in [3, 5, 8, 12, 20]:
            with self.subTest(length=length):
                word = gen.generate(length)
                self.assertEqual(len(word), length)

    def test_phrase(self):
        gen = MisiPwGenV2(lang="it")

        result = gen.phrase(4, 6, 8)
        parts = result.split("_")

        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[0]), 4)
        self.assertEqual(len(parts[1]), 6)
        self.assertEqual(len(parts[2]), 8)

    def test_phrase_custom_separator(self):
        gen = MisiPwGenV2(lang="it")

        result = gen.phrase(3, 5, sep="-")
        parts = result.split("-")

        self.assertEqual(len(parts), 2)
        self.assertEqual(len(parts[0]), 3)
        self.assertEqual(len(parts[1]), 5)

    def test_phrase_no_lengths_raises(self):
        gen = MisiPwGenV2(lang="it")

        with self.assertRaises(ValueError):
            gen.phrase()

    def test_sentence(self):
        gen = MisiPwGenV2(lang="it")

        total = 20
        result = gen.sentence(total)
        parts = result.split("_")

        # Total length should match
        self.assertEqual(sum(len(p) for p in parts), total)
        # All parts should have at least 1 character
        self.assertTrue(all(len(p) >= 1 for p in parts))

    def test_sentence_invalid_length_raises(self):
        gen = MisiPwGenV2(lang="it")

        with self.assertRaises(ValueError):
            gen.sentence(0)

    def test_generate_word(self):
        gen = MisiPwGenV2(lang="it")

        word = gen.generate_word(10)
        self.assertEqual(len(word), 10)

    def test_generate_words(self):
        gen = MisiPwGenV2(lang="it")

        words = gen.generate_words([3, 5, 7])

        self.assertEqual(len(words), 3)
        self.assertEqual(len(words[0]), 3)
        self.assertEqual(len(words[1]), 5)
        self.assertEqual(len(words[2]), 7)

    def test_generate_sentence_parts_auto(self):
        gen = MisiPwGenV2(lang="it")

        parts = gen.generate_sentence_parts(20)

        # Should return a list of lengths that sum to 20
        self.assertEqual(sum(parts), 20)
        self.assertTrue(all(p >= 1 for p in parts))

    def test_generate_sentence_parts_with_word_count(self):
        gen = MisiPwGenV2(lang="it")

        parts = gen.generate_sentence_parts(24, words=4)

        self.assertEqual(len(parts), 4)
        self.assertEqual(sum(parts), 24)
        self.assertTrue(all(p >= 1 for p in parts))

    def test_from_language_factory(self):
        gen = MisiPwGenV2.from_language("it")

        self.assertIsInstance(gen, MisiPwGenV2)
        word = gen.generate(6)
        self.assertEqual(len(word), 6)

    def test_from_module_factory(self):
        gen = MisiPwGenV2.from_module("tests.fixtures.test_syllables_v2")

        self.assertIsInstance(gen, MisiPwGenV2)
        self.assertEqual(len(gen.syllables), 10)

    def test_legacy_factory(self):
        # Test that legacy() returns the old MisiPwGen class
        legacy_gen = MisiPwGenV2.legacy()

        # Should be able to generate words
        word = legacy_gen.generate(8)
        self.assertEqual(len(word), 8)


class GenerationErrorTestCase(TestCase):
    def test_is_exception(self):
        err = GenerationError("test error")
        self.assertIsInstance(err, Exception)
        self.assertEqual(str(err), "test error")


class CumulativeV2EdgeCasesTestCase(TestCase):
    """Additional tests for edge cases in CumulativeV2"""

    def test_invert_in_range_clamps_to_upper(self):
        """Test that invert_in_range clamps idx to upper_index when out of bounds (line 109)"""
        s1 = SyllableV2(w_start=10, w_middle=5, w_end=2, sequence=["a"])
        s2 = SyllableV2(w_start=20, w_middle=10, w_end=5, sequence=["b", "a"])

        coll = SyllableCollectionV2()
        coll.append(s1)
        coll.append(s2)
        coll.finalize()

        cum = CumulativeV2(coll)

        # Request a weight that would be beyond upper_index
        idx = cum.invert_in_range("start", 9999, 0, 1)
        self.assertEqual(idx, 1)  # Should clamp to upper_index


class MisiPwGenV2EdgeCasesTestCase(TestCase):
    """Additional tests for edge cases in MisiPwGenV2"""

    def test_partition_length_small_values(self):
        """Test _partition_length with values <= 3 (line 211)"""
        self.assertEqual(MisiPwGenV2._partition_length(1), [1])
        self.assertEqual(MisiPwGenV2._partition_length(2), [2])
        self.assertEqual(MisiPwGenV2._partition_length(3), [3])

    def test_partition_length_larger_values(self):
        """Test _partition_length with larger values (lines 217-219)"""
        result = MisiPwGenV2._partition_length(30)
        # Check that the sum is correct
        self.assertEqual(sum(result), 30)
        # Check that number of parts is in range
        self.assertTrue(2 <= len(result) <= 6)
        # Check all parts are at least 1
        self.assertTrue(all(x >= 1 for x in result))

    def test_generate_sentence_parts_invalid_total_length(self):
        """Test generate_sentence_parts with invalid total_length (line 231)"""
        gen = MisiPwGenV2(lang="it")
        with self.assertRaises(ValueError) as ctx:
            gen.generate_sentence_parts(0)
        self.assertIn("must be >= 1", str(ctx.exception))

    def test_generate_sentence_parts_custom_word_count(self):
        """Test generate_sentence_parts with custom word count (lines 238-240)"""
        gen = MisiPwGenV2(lang="it")
        # Test with uneven distribution to trigger while loop
        parts = gen.generate_sentence_parts(23, words=5)
        self.assertEqual(len(parts), 5)
        self.assertEqual(sum(parts), 23)
        self.assertTrue(all(x >= 1 for x in parts))
