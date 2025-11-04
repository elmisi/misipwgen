# misipwgen

Random word generator pronounceable in Italian

## Dependencies

Nothing

## Try it now!

Just generate a random word:

```shell
python -c "from misipwgen import MisiPwGen ; print(MisiPwGen.from_language('it').generate_word(7))" 
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

# You can also load from a CSV directly
pwg2 = MisiPwGen.from_csv("misipwgen/data/it/syllables_v2.csv")
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
