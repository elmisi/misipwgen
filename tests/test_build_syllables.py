import importlib.util
import io
import os
import sys
import tempfile
import types
import gzip
import bz2
import unittest


def load_build_module() -> types.ModuleType:
    """Load scripts/build_syllables.py as a module for testing."""
    root = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(root, "scripts", "build_syllables.py")
    spec = importlib.util.spec_from_file_location("build_syllables", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[assignment]
    return mod


class BuildSyllablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_build_module()

    def test_weight_transform(self):
        wt = self.mod.weight_transform
        self.assertGreaterEqual(wt(0, 1.0, 0.7), 1)
        self.assertLess(wt(10, 1.0, 0.5), wt(100, 1.0, 0.5))

    def test_open_text_auto_plain_gz_bz2(self):
        with tempfile.TemporaryDirectory() as td:
            plain = os.path.join(td, "x.txt")
            gz = os.path.join(td, "x.txt.gz")
            bz = os.path.join(td, "x.txt.bz2")
            content = "Hola mundo\nCiao mondo\n"
            with open(plain, "w", encoding="utf-8") as f:
                f.write(content)
            with gzip.open(gz, "wt", encoding="utf-8") as f:
                f.write(content)
            with bz2.open(bz, "wt", encoding="utf-8") as f:
                f.write(content)

            for p in (plain, gz, bz):
                with self.mod._open_text_auto(p) as fh:
                    data = fh.read()
                    self.assertIn("Hola", data)

    def test_tokenize_and_counts_es(self):
        lang = self.mod.LanguagePack(code="es", vowels="aeiouáéíóúü")
        text = "El pingüino toca la guitarra y corre rápido."
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, "es.txt")
            with open(fp, "w", encoding="utf-8") as f:
                f.write(text)
            tokens = list(self.mod.read_corpus_tokens(lang, fp))
            self.assertTrue(any("ping" in t or "pingü" in t for t in tokens))

            # Syllable counts should produce some start/middle entries
            start, middle = self.mod.syllable_counts(lang, tokens)
            self.assertTrue(len(start) > 0)
            self.assertTrue(isinstance(start, dict) and isinstance(middle, dict))

    def test_open_syllable_heuristics(self):
        self.assertTrue(self.mod._is_open_syllable_it("bra"))
        self.assertFalse(self.mod._is_open_syllable_it("br"))
        self.assertTrue(self.mod._is_open_syllable_es("tra"))
        self.assertFalse(self.mod._is_open_syllable_es("tr"))

    def test_write_v2_py_and_import(self):
        # Construct tiny counts
        start = {"ca": 10, "bra": 5}
        middle = {"sa": 3}
        end = {"do": 8}
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "syllables_v2.py")
            self.mod.write_v2_py(out, start, middle, end, k=1.0, alpha=0.7)
            self.assertTrue(os.path.exists(out))
            spec = importlib.util.spec_from_file_location("syll_v2", out)
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            assert spec and spec.loader
            spec.loader.exec_module(mod)  # type: ignore[assignment]
            data = getattr(mod, "SYLLABLES_V2")
            self.assertTrue(any(list(item[3]) == ["c", "a"] for item in data))

    def test_write_legacy_csv(self):
        start = {"ca": 4, "a": 2}
        middle = {"sa": 3, "e": 1}
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "legacy.csv")
            self.mod.write_legacy_csv(out, start, middle, k=1.0, alpha=0.7)
            with open(out, "r", encoding="utf-8") as f:
                text = f.read()
            self.assertIn("schema=1", text)
            self.assertIn(";", text)  # has separators

    def test_main_end_to_end_v2_es(self):
        # Small Spanish corpus
        lang = self.mod.LanguagePack(code="es", vowels="aeiouáéíóúü")
        text = """La bruja corre rapido. El carro blanco pasa. guitarra llaves perro.
        """
        with tempfile.TemporaryDirectory() as td:
            corpus = os.path.join(td, "corpus.txt")
            with open(corpus, "w", encoding="utf-8") as f:
                f.write(text)
            out = os.path.join(td, "out")  # no extension; script should add .py
            argv = [
                "build_syllables",
                "--lang",
                "es",
                "--corpus",
                corpus,
                "--output",
                out,
                "--schema",
                "v2",
                "--alpha",
                "0.7",
                "--k",
                "1",
                "--min-count",
                "1",
            ]
            old_argv = sys.argv[:]
            try:
                sys.argv = argv
                self.mod.main()
            finally:
                sys.argv = old_argv
            self.assertTrue(os.path.exists(out + ".py"))

    def test_main_end_to_end_v1_it(self):
        text = "ciao mondo bella casa prato strada"
        with tempfile.TemporaryDirectory() as td:
            corpus = os.path.join(td, "corpus.txt")
            with open(corpus, "w", encoding="utf-8") as f:
                f.write(text)
            out = os.path.join(td, "legacy.csv")
            argv = [
                "build_syllables",
                "--lang",
                "it",
                "--corpus",
                corpus,
                "--output",
                out,
                "--schema",
                "v1",
                "--alpha",
                "0.7",
                "--k",
                "1",
                "--min-count",
                "1",
            ]
            old_argv = sys.argv[:]
            try:
                sys.argv = argv
                self.mod.main()
            finally:
                sys.argv = old_argv
            self.assertTrue(os.path.exists(out))

    def test_main_errors(self):
        # Empty corpus -> no tokens
        with tempfile.TemporaryDirectory() as td:
            corpus = os.path.join(td, "empty.txt")
            open(corpus, "w", encoding="utf-8").close()
            argv = [
                "build_syllables",
                "--lang",
                "es",
                "--corpus",
                corpus,
                "--schema",
                "v2",
            ]
            old_argv = sys.argv[:]
            try:
                sys.argv = argv
                with self.assertRaises(SystemExit):
                    self.mod.main()
            finally:
                sys.argv = old_argv

        # Overly strict min-count filters out everything
        with tempfile.TemporaryDirectory() as td:
            corpus = os.path.join(td, "c.txt")
            with open(corpus, "w", encoding="utf-8") as f:
                f.write("casa casa")
            argv = [
                "build_syllables",
                "--lang",
                "es",
                "--corpus",
                corpus,
                "--schema",
                "v2",
                "--min-count",
                "9999",
            ]
            old_argv = sys.argv[:]
            try:
                sys.argv = argv
                with self.assertRaises(SystemExit):
                    self.mod.main()
            finally:
                sys.argv = old_argv
