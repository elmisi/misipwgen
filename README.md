# misipwgen

Random word generator pronounceable in Italian

## Dependencies

Nothing

## Try it now!

Just generate a random word:

```commandline
python -c "from misipwgen import MisiPwGen ; print(MisiPwGen().generate(7))" 
```

## Use

```python

from misipwgen import MisiPwGen

pwg = MisiPwGen()
word = pwg.generate(7)
```

## black

```commandline
black .
```

## isort

```commandline
isort .
```


## Test

```commandline
python -m unittest -v
```

## Coverage

```commandline
coverage run -m unittest -v
coverage report
```
