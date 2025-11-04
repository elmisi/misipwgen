#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime, timezone
from typing import List


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert schema v2 CSV to a Python module (SYLLABLES_V2)")
    p.add_argument("--csv", required=True, help="Path to syllables_v2.csv")
    p.add_argument(
        "--output",
        help=(
            "Output .py path (default: replace final '.csv' with '.py' in the same directory). "
            "Use misipwgen/data/{lang}/syllables_v2.py for nested module import."
        ),
    )
    return p.parse_args()


def read_v2_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";", quotechar="|")
        for row in reader:
            if not row or (row[0] and row[0].startswith("#")):
                continue
            if len(row) < 4:
                continue
            try:
                ws = int(row[0])
                wm = int(row[1])
                we = int(row[2])
            except ValueError:
                continue
            seq = row[3:]
            yield ws, wm, we, seq


def write_py(path: str, items) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: List[str] = []
    lines.append("# Generated from CSV (schema v2)\n")
    lines.append(f"# generated: {ts}\n\n")
    lines.append("SYLLABLES_V2 = [\n")
    for ws, wm, we, seq in items:
        seq_repr = ", ".join(repr(x) for x in seq)
        lines.append(f"    ({int(ws)}, {int(wm)}, {int(we)}, [{seq_repr}]),\n")
    lines.append("]\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(lines))


def main() -> None:
    args = parse_args()
    out = args.output or os.path.splitext(args.csv)[0] + ".py"
    items = list(read_v2_csv(args.csv))
    if not items:
        raise SystemExit("No rows found in input CSV or invalid format.")
    write_py(out, items)
    print(f"Wrote Python module to {out} with {len(items)} entries")


if __name__ == "__main__":
    main()

