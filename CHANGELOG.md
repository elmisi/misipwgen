# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

Added
- Positional generator (v2) with start/middle/end weights: `MisiPwGenPositional` (aliased as public `MisiPwGen`).
- Factory constructors: `MisiPwGen.from_language('it')`, `MisiPwGen.from_csv(path)` and the legacy equivalent via `MisiPwGen.legacy(...)`.
- Phrase and sentence helpers on both generators: `phrase(*lengths, sep='_')`, `sentence(total_length, sep='_')`, plus list-returning helpers (`generate_words`, `generate_sentence_parts`).
- Reproducible generation via injected RNG (`rng=random.Random(...)`).
- Builder script enhancements: schema v2 output (`--schema v2`), gzip/bz2 input, corpus validation, Italian filtering, end-only accents.
- Python module support for v2 syllables: loader prefers importing `misipwgen/data/<lang>/syllables_v2.py` (exports `SYLLABLES_V2`) for best performance; falls back to CSV.
- New script to convert CSV→Python module without rebuilding: `scripts/csv_v2_to_py.py`.
- Builder can emit Python module directly: `--format py` writes `syllables_v2.py` module.

Changed
- Default public `MisiPwGen` now points to the positional (v2) generator. Use `MisiPwGen.legacy()` for the original behavior/API.
- Faster and fairer selection: cumulative bisect and unbiased random range.

Notes
- Legacy CSV schema (v1) remains supported and is unchanged.
- Packaged data is loaded via `importlib.resources` to support normal installs and zipimport.
- Future: CSV production/loading may be deprecated in favor of the Python module format for v2.
