# misipwgen

[![CI](https://github.com/elmisi/misipwgen/actions/workflows/ci.yml/badge.svg)](https://github.com/elmisi/misipwgen/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/elmisi/misipwgen/branch/main/graph/badge.svg)](https://codecov.io/gh/elmisi/misipwgen)
[![PyPI version](https://badge.fury.io/py/misipwgen.svg)](https://badge.fury.io/py/misipwgen)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Multilingual random word generator with natural pronunciation

Generates pronounceable random words in multiple languages:
- **Italian** (`it`) - Full support with language-specific syllabification
- **Spanish** (`es`) - Full support with language-specific syllabification

## Dependencies

Nothing

## Try it now!

Just generate a random word (specify language with `from_language()`):

```shell
# Italian
python -c "from misipwgen import MisiPwGen ; print(MisiPwGen.from_language('it').generate_word(7))"

# Spanish
python -c "from misipwgen import MisiPwGen ; print(MisiPwGen.from_language('es').generate_word(7))"
```

Or install locally and use the CLI (use `--lang` to select language):

```shell
pip install .
python -m misipwgen --sentence 16 --lang it --sep '-'
python -m misipwgen 5 5 --lang es --sep '-'
```

## Web Interface

A simple web interface is available for easy word, phrase, and sentence generation:

```shell
# Install web dependencies
pip install -r requirements-web.txt

# Run the web server
python webapp.py
```

Then open your browser to `http://localhost:5000` to use the interactive web interface.

Features:
- **Word Generator**: Generate single words with custom length
- **Phrase Generator**: Generate multiple words with custom separators
- **Sentence Generator**: Generate sentences with automatic word splitting
- **Language Selection**: Choose between Italian and Spanish
- **Copy to Clipboard**: Easy one-click copying of generated results

## Use

```python
from misipwgen import MisiPwGen

# Default generator is positional (v2). Use factories for clarity.
pwg = MisiPwGen.from_language("it")
word = pwg.generate_word(7)

# Need the legacy behavior/files? Use the legacy() factory
legacy = MisiPwGen.legacy()
print(legacy.generate(7))
```

## Build From Corpus

Generate syllables from a text corpus and load them at runtime (v2 writes a Python module):

```shell
# Italian (v2 module)
python scripts/build_syllables.py --lang it --corpus data/it/corpus.txt --alpha 0.7 --k 1 --min-count 3
# Spanish (v2 module)
python scripts/build_syllables.py --lang es --corpus data/es/corpus.txt --alpha 0.7 --k 1 --min-count 3

# Legacy schema (v1) CSV still supported
python scripts/build_syllables.py --lang it --corpus data/it/corpus.txt --schema v1
```

Notes:
- v2 CSV is no longer supported; the builder emits `misipwgen/data/<lang>/syllables_v2.py` and the generator imports it.
- Load explicitly via: `from misipwgen import MisiPwGenPositional; MisiPwGenPositional.from_module('misipwgen.data.it.syllables_v2')`.

### Spanish corpus example (Tatoeba TSV)

```shell
# Download Spanish sentences TSV (bz2)
mkdir -p data/es
curl -fL -o data/es/spa_sentences.tsv.bz2 \
  https://downloads.tatoeba.org/exports/per_language/spa/spa_sentences.tsv.bz2

# Extract only the sentence text (3rd column)
bunzip2 -c data/es/spa_sentences.tsv.bz2 | cut -f3 > data/es/corpus.txt

# Build Spanish syllables (v2 module)
python scripts/build_syllables.py --lang es --corpus data/es/corpus.txt --alpha 0.7 --k 1 --min-count 3

# Try it
python -c "from misipwgen import MisiPwGen; print(MisiPwGen.from_language('es').phrase(6,6, sep='-'))"
```

## Phrase & Sentence Mode

Generate multiple words joined by a separator or let the library pick a split for you:

```python
from misipwgen import MisiPwGen

pwg = MisiPwGen.from_language("it")

# Fixed lengths (joined with '_')
phrase = pwg.phrase(7, 2, 5, 1, 8)  # e.g., "sarbido_ti_accoa_i_ladrufo"

# Automatic partition to total length
sent = pwg.sentence(24)  # e.g., "tredoto_emile_leimioe"

# Custom separator
dash_phrase = pwg.phrase(5, 5, 5, sep="-")   # e.g., "torec-dalimo-castri"
space_sentence = pwg.sentence(18, sep=" ")   # e.g., "sodami trae cofe"
```

If you built corpus‑based syllables with the v2 schema, the default generator already supports it:

```python
from misipwgen import MisiPwGen

pwg2 = MisiPwGen.from_language("it")
print(pwg2.sentence(24))

# Or load from a Python module explicitly (exports SYLLABLES_V2)
from misipwgen import MisiPwGenPositional
pwg2 = MisiPwGenPositional.from_module("misipwgen.data.it.syllables_v2")
```

Advanced: reproducible generation via injected RNG

```python
import random
from misipwgen import MisiPwGen

rng = random.Random(42)
pwg = MisiPwGen.from_language("it", rng=rng)
print(pwg.generate_word(8))
```

## Development

### Setup

```shell
pip install -r requirements-dev.txt
pre-commit install  # Optional: install git hooks
```

### Code Formatting

```shell
black .
isort .
```

### Testing

```shell
# Run tests with pytest
pytest

# Run tests with coverage (87%+ coverage!)
python -m pytest -p pytest_cov --cov=misipwgen --cov-report=html --cov-report=term

# Or use coverage directly
coverage run -m pytest
coverage report
coverage html  # Generate HTML report
```

### Pre-commit Hooks

```shell
pre-commit run --all-files
```
