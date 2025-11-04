from __future__ import annotations

import argparse
import sys
from typing import List

from . import MisiPwGen


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate pronounceable random words")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--sentence", type=int, help="Total length to split into multiple words")
    p.add_argument("lengths", nargs="*", type=int, help="Word lengths (one or more)")
    p.add_argument("--lang", default="it", help="Language code (default: it)")
    p.add_argument("--sep", default="_", help="Separator for multiple words (default: _)")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    gen = MisiPwGen.from_language(ns.lang)

    if ns.sentence is not None:
        print(gen.sentence(ns.sentence, sep=ns.sep))
        return 0

    if not ns.lengths:
        print("error: provide either --sentence TOTAL or one or more lengths", file=sys.stderr)
        return 2

    if len(ns.lengths) == 1:
        print(gen.generate_word(ns.lengths[0]))
        return 0

    print(gen.phrase(*ns.lengths, sep=ns.sep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

