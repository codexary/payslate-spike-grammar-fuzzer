English | [简体中文](README.zh-CN.md)

# Timesheet grammar spike

This standalone, local experiment generates synthetic timesheet CSV inputs for defensive robustness testing of Payslate Online. It uses Python 3.12 and the standard library only. No network services are used.

```sh
python3 generate.py --seed 7 --count 3
python3 -m unittest discover -v
```

The output marks the start and end of each file; those markers are display wrappers, not CSV content. The `derive("file", random.Random(seed), 8, covered)` API returns one file as text. Encode it as UTF-8 to retain an optional leading BOM. The same seed and settings reproduce the same files.

`grammar.json` stores each rule's alternatives in a list, with `<rule>` references. The bounded row rule emits one to five data rows (N = 5); edit its alternatives to change that bound. `--depth` defaults to 8 and an exhausted derivation raises a clear error. Coverage records each selected `(rule, alternative index)` pair, including empty alternatives; it does not measure combinations or product code coverage.

The grammar exercises comma, semicolon and tab separators, optional BOM, LF/CRLF, case variants of header aliases, optional holiday values, quoted fields, quoted separators, doubled quotes and blank rows. Dates are calendar-valid samples in June–July 2026 before 13 July. Times use both supported formats, including overnight shifts, with unequal start and end values. Separators and line endings are selected once per file and passed through the expansion context. Optional header/value slots share their selection across all rows.

ADR 0003 rejects unknown headers. Rostering exports often carry extra columns such as notes or break minutes, so the grammar adds optional `notes` and `break minutes` columns to explore that boundary: those files are structurally valid CSV but are outside the accepted header contract. Blank rows have no fields and are ignored when checking header width. Quoted newlines are excluded because the product contract leaves that decision open.

## Compare strategies

```sh
python3 compare.py --budget 1000 --seed 120012
```

Each strategy receives exactly `budget` candidates, using separate random generators initialized with the same seed. Grammar candidates are fresh derivations. Mutation always starts from one realistic comma CSV with three synthetic employees, early July 2026 dates and a holiday column. Each candidate receives one to three independently selected overwrites, inserts or deletes; operations, positions and replacement bytes are uniform. Overwrites may leave a byte unchanged, edits may cancel, and duplicate candidates still consume budget. This compares candidate counts, not runtime or byte counts.

The command prints one JSON line. `seed` and `budget` identify the run; `grammar_alternatives_covered` / `grammar_alternatives_total` count selected grammar alternatives; `grammar_accepted` and `mutation_accepted` count files accepted by the local check. The two `*_distinct_rejections` fields count different first-rejection categories seen for each strategy, not all defects in a file or product paths.

The local acceptance check is a reachability proxy, not the product oracle. It decodes UTF-8 with an optional leading BOM, infers the separator from the header, resolves aliases, checks row widths, validates dates and times, rejects equal times and validates holiday values. It also rejects unknown or duplicate headers, empty employee names, interior BOMs, bare CR and malformed CSV. Blank rows are ignored. Dates are calendar-checked without the generator's date-window restriction. Missing holiday columns mean false. Only the classification is returned; the check does not verify the product's parsed Boolean values.

For this experiment, a header without data and quoted newlines are rejected; ADR 0003 leaves the product's quoted-newline policy undecided. CSV parsing follows Python's `csv` module, and header selection is a small local heuristic. The check does not implement the product importer, HTTP handling, streaming limits or downstream payroll rules. Files with the optional extra columns are rejected as `unknown_header`. The eventual product campaign must judge inputs by the HTTP response and verify parsed values at the product boundary.

## About this repository

Elsworne, Payslate and the team are fictional.

The code and documents in this repository were written with the help of AI tools; every recorded output comes from actually running them.
