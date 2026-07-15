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

## About this repository

Elsworne, Payslate and the team are fictional.

The code and documents in this repository were written with the help of AI tools; every recorded output comes from actually running them.
