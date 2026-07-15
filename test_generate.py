import csv
from datetime import datetime
import io
import random
import unittest

from generate import GRAMMAR, derive


class GenerationTests(unittest.TestCase):
    def test_same_seed_same_files_and_coverage(self):
        def batch():
            rng = random.Random(7)
            covered = set()
            files = [derive("file", rng, 8, covered) for _ in range(30)]
            return files, covered

        self.assertEqual(batch(), batch())

    def test_files_parse_at_header_width(self):
        rng = random.Random(120012)
        covered = set()
        delimiters = set()
        for _ in range(1000):
            candidate = derive("file", rng, 8, covered).removeprefix("\ufeff")
            header_line = candidate.splitlines()[0]
            delimiter = next(d for d in (",", ";", "\t") if d in header_line)
            delimiters.add(delimiter)
            rows = list(csv.reader(io.StringIO(candidate, newline=""),
                                   delimiter=delimiter, strict=True))
            header, *data = rows
            data = [row for row in data if row]
            self.assertIn(len(data), range(1, 6))
            for row in data:
                self.assertEqual(len(row), len(header))
                fmt = "%Y-%m-%d" if "-" in row[1] else "%d/%m/%Y"
                date = datetime.strptime(row[1], fmt).date()
                self.assertGreaterEqual(date.isoformat(), "2026-06-01")
                self.assertLess(date.isoformat(), "2026-07-13")
        self.assertEqual(delimiters, {",", ";", "\t"})
        self.assertEqual(covered, {(rule, index) for rule, choices in GRAMMAR.items()
                                   for index in range(len(choices))})

    def test_depth_limit(self):
        with self.assertRaisesRegex(ValueError, "derivation depth limit exhausted"):
            derive("file", random.Random(7), 1, set())


if __name__ == "__main__":
    unittest.main()
