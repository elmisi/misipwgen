# misipwgen

Random word generator pronounceable in Italian

## Dependencies

Nothing

## Try it now!

Just generate a random word:

```shell
python -c "from misipwgen import MisiPwGen ; p=MisiPwGen() ; print(p.generate(7))" 
```

## Use

```python

from misipwgen import MisiPwGen

pwg = MisiPwGen()
word = pwg.generate(7)
```

## Test

```shell
 python -m unittest -v
```

## Coverage

```shell
coverage run -m unittest -v
coverage report -m
```
