# Test fixture for v2 syllables
SYLLABLES_V2 = [
    (5, 0, 0, ['b', 'a']),      # ba - start only
    (0, 10, 0, ['c', 'o']),     # co - middle only
    (0, 0, 15, ['d', 'e']),     # de - end only
    (3, 7, 2, ['f', 'i']),      # fi - all positions
    (4, 0, 8, ['g', 'u']),      # gu - start + end
    (0, 5, 5, ['l', 'a']),      # la - middle + end
    (6, 6, 0, ['m', 'e']),      # me - start + middle
    (10, 10, 10, ['n', 'o']),   # no - balanced weights
    (2, 0, 0, ['p', 'rae']),    # pra - 3 chars, start
    (0, 3, 0, ['str', 'aio']),  # str-a/i/o - complex, middle
]
