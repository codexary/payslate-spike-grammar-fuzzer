"""Compare grammar derivation and byte mutation using a local reachability check."""

import argparse
import csv
from datetime import date
import io
import json
import random
import re

from generate import GRAMMAR, derive


BASE = (
    "employee,date,start,end,public holiday\n"
    "Liam Walsh,2026-07-01,09:00,17:00,false\n"
    "Renée Dubois,2026-07-02,23:00,01:00,no\n"
    "Mia Chen,2026-07-03,08:30,16:30,0\n"
).encode("utf-8")
ALIASES = {
    "employee": "employee", "employee name": "employee", "staff": "employee",
    "date": "date", "shift date": "date",
    "start": "start", "start time": "start",
    "end": "end", "end time": "end",
    "public holiday": "holiday", "public_holiday": "holiday", "holiday": "holiday",
}
REQUIRED = {"employee", "date", "start", "end"}
HOLIDAYS = {"true": True, "yes": True, "1": True,
            "false": False, "no": False, "0": False, "": False}


def parse_date(value):
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return date.fromisoformat(value)
    if re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", value):
        day, month, year = map(int, value.split("/"))
        return date(year, month, day)
    raise ValueError("unsupported date")


def parse_time(value):
    if re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        hour, minute = map(int, value.split(":"))
        if hour < 24 and minute < 60:
            return hour * 60 + minute
    match = re.fullmatch(r"([0-9]{1,2}):([0-9]{2}) (AM|PM)", value)
    if match:
        hour, minute = int(match[1]), int(match[2])
        if 1 <= hour <= 12 and minute < 60:
            return (hour % 12 + (12 if match[3] == "PM" else 0)) * 60 + minute
    raise ValueError("unsupported time")


def header_delimiter(line):
    candidates = []
    for delimiter in (",", ";", "\t"):
        try:
            fields = next(csv.reader([line], delimiter=delimiter, strict=True))
        except (csv.Error, StopIteration):
            continue
        if len(fields) > 1:
            score = sum(field.casefold() in ALIASES for field in fields)
            candidates.append((score, len(fields), delimiter))
    if not candidates:
        raise ValueError("no header delimiter")
    return max(candidates)[2]


def acceptance_check(data):
    """Return None when accepted, otherwise the first stable rejection category."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "utf8"
    if "\ufeff" in text:
        return "interior_bom"
    if re.search(r"\r(?!\n)", text):
        return "bare_cr"
    first = next((line.rstrip("\r") for line in text.split("\n")
                  if line.rstrip("\r")), None)
    if first is None:
        return "empty_file"
    try:
        delimiter = header_delimiter(first)
    except ValueError:
        return "header_delimiter"
    try:
        rows = [row for row in csv.reader(io.StringIO(text, newline=""),
                                         delimiter=delimiter, strict=True) if row]
    except csv.Error:
        return "invalid_csv"
    if any("\n" in field or "\r" in field for row in rows for field in row):
        return "quoted_newline"
    header, *data_rows = rows
    columns = [ALIASES.get(field.casefold()) for field in header]
    if None in columns:
        return "unknown_header"
    if not REQUIRED.issubset(columns):
        return "missing_header"
    if len(set(columns)) != len(columns):
        return "duplicate_header"
    if not data_rows:
        return "empty_data"
    for row in data_rows:
        if len(row) != len(header):
            return "row_width"
        values = dict(zip(columns, row))
        if not values["employee"].strip():
            return "empty_employee"
        try:
            parse_date(values["date"])
        except ValueError:
            return "date"
        try:
            start = parse_time(values["start"])
            end = parse_time(values["end"])
        except ValueError:
            return "time"
        if start == end:
            return "zero_duration"
        if values.get("holiday", "").casefold() not in HOLIDAYS:
            return "holiday"
    return None


def mutate(rng):
    """Apply one to three uniformly chosen byte edits to the same seed file."""
    data = bytearray(BASE)
    for _ in range(rng.randint(1, 3)):
        operation = rng.choice(("overwrite", "insert", "delete"))
        if operation == "insert":
            data.insert(rng.randrange(len(data) + 1), rng.randrange(256))
        else:
            index = rng.randrange(len(data))
            if operation == "overwrite":
                data[index] = rng.randrange(256)
            else:
                del data[index]
    return bytes(data)


def compare(budget, seed):
    if budget <= 0:
        raise ValueError("budget must be positive")
    grammar_rng = random.Random(seed)
    mutation_rng = random.Random(seed)
    covered = set()
    accepted = {"grammar": 0, "mutation": 0}
    rejected = {"grammar": set(), "mutation": set()}
    for _ in range(budget):
        candidates = {
            "grammar": derive("file", grammar_rng, 8, covered).encode("utf-8"),
            "mutation": mutate(mutation_rng),
        }
        for strategy, candidate in candidates.items():
            reason = acceptance_check(candidate)
            if reason is None:
                accepted[strategy] += 1
            else:
                rejected[strategy].add(reason)
    return {
        "seed": seed,
        "budget": budget,
        "grammar_alternatives_covered": len(covered),
        "grammar_alternatives_total": sum(len(options) for options in GRAMMAR.values()),
        "grammar_accepted": accepted["grammar"],
        "mutation_accepted": accepted["mutation"],
        "grammar_distinct_rejections": len(rejected["grammar"]),
        "mutation_distinct_rejections": len(rejected["mutation"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=120012)
    args = parser.parse_args()
    if args.budget <= 0:
        parser.error("budget must be positive")
    print(json.dumps(compare(args.budget, args.seed)))


if __name__ == "__main__":
    main()
