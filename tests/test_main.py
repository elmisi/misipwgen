from unittest import TestCase
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

from misipwgen.__main__ import parse_args, main


class ParseArgsTestCase(TestCase):
    def test_default_args(self):
        args = parse_args(["8"])
        self.assertEqual(args.lengths, [8])
        self.assertEqual(args.lang, "it")
        self.assertEqual(args.sep, "_")
        self.assertIsNone(args.sentence)

    def test_multiple_lengths(self):
        args = parse_args(["4", "6", "8"])
        self.assertEqual(args.lengths, [4, 6, 8])

    def test_custom_lang(self):
        args = parse_args(["8", "--lang", "es"])
        self.assertEqual(args.lang, "es")

    def test_custom_separator(self):
        args = parse_args(["4", "6", "--sep", "-"])
        self.assertEqual(args.sep, "-")

    def test_sentence_mode(self):
        args = parse_args(["--sentence", "20"])
        self.assertEqual(args.sentence, 20)
        self.assertEqual(args.lengths, [])

    def test_sentence_and_lengths_mutually_exclusive(self):
        # sentence and lengths are mutually exclusive, but argparse allows both
        # The main() function should handle sentence mode first
        args = parse_args(["--sentence", "20", "5", "6"])
        self.assertEqual(args.sentence, 20)
        self.assertEqual(args.lengths, [5, 6])


class MainTestCase(TestCase):
    @patch("misipwgen.__main__.MisiPwGen")
    def test_single_length(self, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen.generate_word.return_value = "testword"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main(["8"])

        self.assertEqual(result, 0)
        mock_gen_class.from_language.assert_called_once_with("it")
        mock_gen.generate_word.assert_called_once_with(8)
        self.assertIn("testword", mock_stdout.getvalue())

    @patch("misipwgen.__main__.MisiPwGen")
    def test_multiple_lengths(self, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen.phrase.return_value = "word1_word2_word3"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main(["4", "6", "8"])

        self.assertEqual(result, 0)
        mock_gen.phrase.assert_called_once_with(4, 6, 8, sep="_")
        self.assertIn("word1_word2_word3", mock_stdout.getvalue())

    @patch("misipwgen.__main__.MisiPwGen")
    def test_sentence_mode(self, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen.sentence.return_value = "word1_word2"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main(["--sentence", "20"])

        self.assertEqual(result, 0)
        mock_gen.sentence.assert_called_once_with(20, sep="_")
        self.assertIn("word1_word2", mock_stdout.getvalue())

    @patch("misipwgen.__main__.MisiPwGen")
    def test_custom_language(self, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen.generate_word.return_value = "palabra"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stdout", new_callable=StringIO):
            result = main(["8", "--lang", "es"])

        self.assertEqual(result, 0)
        mock_gen_class.from_language.assert_called_once_with("es")

    @patch("misipwgen.__main__.MisiPwGen")
    def test_custom_separator(self, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen.phrase.return_value = "word1-word2"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main(["4", "6", "--sep", "-"])

        self.assertEqual(result, 0)
        mock_gen.phrase.assert_called_once_with(4, 6, sep="-")
        self.assertIn("word1-word2", mock_stdout.getvalue())

    @patch("misipwgen.__main__.MisiPwGen")
    @patch("sys.argv", ["misipwgen"])
    def test_no_lengths_and_no_sentence_returns_error(self, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main([])

        self.assertEqual(result, 2)
        self.assertIn("error", mock_stderr.getvalue().lower())

    @patch("misipwgen.__main__.MisiPwGen")
    def test_sentence_takes_precedence(self, mock_gen_class):
        # If both sentence and lengths are provided, sentence should take precedence
        mock_gen = MagicMock()
        mock_gen.sentence.return_value = "generated_sentence"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.stdout", new_callable=StringIO):
            result = main(["--sentence", "15", "5", "6"])

        self.assertEqual(result, 0)
        # Should call sentence, not phrase
        mock_gen.sentence.assert_called_once_with(15, sep="_")
        mock_gen.phrase.assert_not_called()
        mock_gen.generate_word.assert_not_called()

    @patch("misipwgen.__main__.MisiPwGen")
    def test_default_argv(self, mock_gen_class):
        # Test that None argv defaults to sys.argv[1:]
        mock_gen = MagicMock()
        mock_gen.generate_word.return_value = "default"
        mock_gen_class.from_language.return_value = mock_gen

        with patch("sys.argv", ["misipwgen", "10"]):
            with patch("sys.stdout", new_callable=StringIO):
                result = main(None)

        self.assertEqual(result, 0)
        mock_gen.generate_word.assert_called_once_with(10)
