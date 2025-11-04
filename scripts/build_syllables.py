#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import math
import os
from datetime import datetime, timezone
import gzip
import bz2
from typing import Dict, Iterable, List, Tuple

# Local imports via relative path when run from repo; falls back to package when installed
try:  # pragma: no cover - convenience for local script execution
    from misipwgen.lang.core import LanguagePack
    from misipwgen.lang.core import to_sequence
except Exception:  # noqa: BLE001
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from misipwgen.lang.core import LanguagePack, to_sequence  # type: ignore


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build syllables CSV from a text corpus")
    p.add_argument("--lang", required=True, help="Language code, e.g. it")
    p.add_argument("--corpus", required=True, help="Path to corpus text file")
    p.add_argument(
        "--output",
        help=(
            "Output CSV path (defaults: schema v2 -> misipwgen/data/{lang}/syllables_v2.csv; "
            "legacy -> misipwgen/data/{lang}/syllables.csv)"
        ),
    )
    p.add_argument("--alpha", type=float, default=0.7, help="Power transform exponent (0<alpha<=1)")
    p.add_argument("--k", type=float, default=1.0, help="Additive smoothing constant (>=0)")
    p.add_argument("--min-count", type=int, default=3, help="Minimum raw count to include a syllable")
    p.add_argument("--schema", choices=["v1", "v2"], default="v2", help="Output schema version")
    p.add_argument("--format", choices=["csv", "py"], default="csv", help="Output format for v2 (csv or py module)")
    return p.parse_args()


def _open_text_auto(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    if path.endswith(".bz2"):
        return bz2.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")


def read_corpus_tokens(lang: LanguagePack, path: str) -> Iterable[str]:
    with _open_text_auto(path) as f:
        for line in f:
            yield from lang.syllabifier().tokenize(line)


def syllable_counts(lang: LanguagePack, tokens: Iterable[str]) -> Tuple[Dict[str, int], Dict[str, int]]:
    s = lang.syllabifier()
    start: Dict[str, int] = collections.Counter()
    middle: Dict[str, int] = collections.Counter()
    for token in tokens:
        sylls = s.syllabify(token)
        if not sylls:
            continue
        if len(sylls) == 1:
            start[sylls[0]] += 1
        else:
            start[sylls[0]] += 1
            for m in sylls[1:]:
                middle[m] += 1
    return start, middle


def weight_transform(count: int, k: float, alpha: float) -> int:
    return max(1, int(round(math.pow(count + k, alpha))))


def _is_open_syllable_it(s: str) -> bool:
    """Heuristic filter: keep Italian-like open syllables (onset + vowel nucleus).

    - Ends with a vowel (open syllable)
    - Onset is empty, a single consonant, or a common cluster (br, tr, pr, sc, ch, gh, gl, gn, cr, gr, fr, pl, cl, fl, sp, st)
    - Contains at least one vowel
    """
    V = set("aeiouàèéìòóù")
    if not s or s[-1] not in V:
        return False
    # find first vowel position
    j = 0
    while j < len(s) and s[j] not in V:
        j += 1
    if j == len(s):
        return False
    onset = s[:j]
    allowed_onsets = {
        "",
        "b",
        "c",
        "d",
        "f",
        "g",
        "l",
        "m",
        "n",
        "p",
        "r",
        "s",
        "t",
        "v",
        "z",
        "br",
        "cr",
        "dr",
        "fr",
        "gr",
        "pr",
        "tr",
        "pl",
        "cl",
        "gl",
        "fl",
        "sc",
        "sp",
        "st",
        "ch",
        "gh",
        "gn",
    }
    return onset in allowed_onsets


def write_legacy_csv(output_path: str, start: Dict[str, int], middle: Dict[str, int], *, k: float, alpha: float) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# schema=1; lang=legacy; generated=" + ts + "\n")
        out.write("# starting;weight;sequence1[;sequence2;...;sequenceN]\n\n")

        # One-letter vowels (nucleus-only) based on presence in data
        vowels = set([s for s in list(start.keys()) + list(middle.keys()) if len(s) == 1])
        if vowels:
            w = weight_transform(sum(start.get(v, 0) + middle.get(v, 0) for v in vowels), k, alpha)
            out.write(f"1;{w};" + "".join(sorted(vowels)) + "\n\n")

        # Two+ letters: merge start and middle counts (legacy format has single weight)
        all_sylls = set(start) | set(middle)
        rows: List[Tuple[int, str]] = []
        for syl in all_sylls:
            if len(syl) < 1:
                continue
            total = start.get(syl, 0) + middle.get(syl, 0)
            if total <= 0:
                continue
            w = weight_transform(total, k, alpha)
            seq = ";".join(to_sequence(syl))
            starting_flag = 1 if start.get(syl, 0) > 0 else 0
            rows.append((starting_flag, f"{starting_flag};{w};{seq}"))

        # Stable sort: longer syllables later to match existing style
        rows.sort(key=lambda x: (x[0], len(x[1]), x[1]))
        for _, line in rows:
            out.write(line + "\n")


def write_v2_csv(output_path: str, start: Dict[str, int], middle: Dict[str, int], end: Dict[str, int], *, k: float, alpha: float) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# schema=2; generated=" + ts + "\n")
        out.write("# w_start;w_middle;w_end;sequence1[;sequence2;...;sequenceN]\n\n")

        all_sylls = set(start) | set(middle) | set(end)
        rows: List[str] = []
        for syl in all_sylls:
            ws = weight_transform(start.get(syl, 0), k, alpha) if start.get(syl, 0) > 0 else 0
            wm = weight_transform(middle.get(syl, 0), k, alpha) if middle.get(syl, 0) > 0 else 0
            we = weight_transform(end.get(syl, 0), k, alpha) if end.get(syl, 0) > 0 else 0
            if ws == 0 and wm == 0 and we == 0:
                continue
            seq = ";".join(to_sequence(syl))
            rows.append(f"{ws};{wm};{we};{seq}")

        rows.sort(key=lambda r: (len(r.split(";")) - 3, r))
        for line in rows:
            out.write(line + "\n")


def write_v2_py(output_path: str, start: Dict[str, int], middle: Dict[str, int], end: Dict[str, int], *, k: float, alpha: float) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: List[str] = []
    lines.append("# Generated syllables (schema v2)\n")
    lines.append(f"# generated: {ts}\n\n")
    lines.append("SYLLABLES_V2 = [\n")

    all_sylls = set(start) | set(middle) | set(end)
    def w(v):
        return max(0, int(round(math.pow(v + 1.0, alpha)))) if v > 0 else 0

    # Stable sort by length then representation
    for syl in sorted(all_sylls, key=lambda s: (len(s), s)):
        ws = w(start.get(syl, 0))
        wm = w(middle.get(syl, 0))
        we = w(end.get(syl, 0))
        if ws == 0 and wm == 0 and we == 0:
            continue
        seq = ", ".join(repr(ch) for ch in to_sequence(syl))
        lines.append(f"    ({ws}, {wm}, {we}, [{seq}]),\n")

    lines.append("]\n")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(lines))


def main() -> None:
    args = parse_args()
    lang = LanguagePack(code=args.lang, vowels="aeiouàèéìòóù")
    default_name = (
        ("syllables_v2.py" if args.format == "py" else "syllables_v2.csv")
        if args.schema == "v2"
        else "syllables.csv"
    )
    out_path = args.output or os.path.join("misipwgen", "data", args.lang, default_name)

    tokens = read_corpus_tokens(lang, args.corpus)
    start, middle = syllable_counts(lang, tokens)
    # End counts (last syllables in tokens)
    end = collections.Counter()
    tokens2 = read_corpus_tokens(lang, args.corpus)
    s = lang.syllabifier()
    for t in tokens2:
        sylls = s.syllabify(t)
        if not sylls:
            continue
        end[sylls[-1]] += 1

    total_raw = sum(start.values()) + sum(middle.values()) + sum(end.values())
    if total_raw == 0:
        raise SystemExit(
            "No tokens or syllables found in corpus. Check the corpus path/format or try a different source."
        )

    # Drop low-frequency syllables
    start = {k: v for k, v in start.items() if v >= args.min_count}
    middle = {k: v for k, v in middle.items() if v >= args.min_count}
    end = {k: v for k, v in end.items() if v >= args.min_count}

    # Language-specific filtering to improve pronounceability (Italian)
    if args.lang == "it":
        start = {k: v for k, v in start.items() if _is_open_syllable_it(k)}
        middle = {k: v for k, v in middle.items() if _is_open_syllable_it(k)}
        end = {k: v for k, v in end.items() if _is_open_syllable_it(k)}
        # Disallow single-vowel syllables in middle position to avoid long vowel runs
        middle = {k: v for k, v in middle.items() if len(k) > 1}
        # Accented vowels allowed at end only
        ACC = set("àèéìòóù")
        def strip_accent_mid_start(d: Dict[str, int]) -> Dict[str, int]:
            return {k: (0 if any(ch in ACC for ch in k) else v) for k, v in d.items()}
        start = strip_accent_mid_start(start)
        middle = strip_accent_mid_start(middle)

    if not start and not middle and not end:
        raise SystemExit(
            "All syllables filtered out by min-count. Lower --min-count or use a larger corpus."
        )

    if args.schema == "v2":
        if args.format == "py":
            # Ensure .py extension for module output
            if not out_path.endswith(".py"):
                out_path = os.path.splitext(out_path)[0] + ".py"
            write_v2_py(out_path, start, middle, end, k=args.k, alpha=args.alpha)
        else:
            write_v2_csv(out_path, start, middle, end, k=args.k, alpha=args.alpha)
        kept = len(set(start) | set(middle) | set(end))
    else:
        write_legacy_csv(out_path, start, middle, k=args.k, alpha=args.alpha)
        kept = len(set(start) | set(middle))
    print(
        f"Wrote syllables to {out_path} (raw={total_raw}, kept={kept}, schema={args.schema}, format={args.format if args.schema=='v2' else 'csv'})"
    )


if __name__ == "__main__":
    main()
