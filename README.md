# misipwgen

Random word generator pronounceable in Italian

## Dependencies

Nothing

## Try it now!

Just generate a random word:

```shell
python -c "from misipwgen import MisiPwGen ; print(MisiPwGen.from_language('it').generate_word(7))" 
```

Or install locally and use the CLI:

```shell
pip install .
python -m misipwgen --sentence 16 --lang it --sep '-'
python -m misipwgen 5 5 --lang es --sep '-'
```

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

## black

```shell
black .
```

## isort

```shell
isort .
```

## Test

```shell
python -m unittest -v
```

## Coverage

```shell
coverage run -m unittest -v
coverage report
```
