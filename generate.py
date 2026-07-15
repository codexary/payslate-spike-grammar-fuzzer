"""Derive bounded CSV files with file-scoped separator and column choices."""

import argparse
import json
from pathlib import Path
import random
import re
import sys


GRAMMAR = json.loads(Path(__file__).with_name("grammar.json").read_text(encoding="utf-8"))
REFERENCE = re.compile(r"<([a-z0-9_]+)>")
SHARED = {
    "delimiter": "delimiter",
    "newline": "newline",
    "holiday_header_slot": "holiday",
    "holiday_value_slot": "holiday",
    "extra_header_slot": "extra",
    "extra_value_slot": "extra",
}


def derive(rule, rng, depth=8, covered=None):
    """Expand a rule; record (rule, alternative index) pairs in covered.

    Separator choices are cached once per file. Paired header/value slots
    share an alternative index so every data row has the same schema.
    """
    if covered is None:
        covered = set()
    choices = {}

    def expand(symbol, remaining):
        if remaining <= 0:
            raise ValueError(f"derivation depth limit exhausted at <{symbol}>")
        alternatives = GRAMMAR[symbol]
        key = SHARED.get(symbol)
        if key is not None and key in choices:
            index = choices[key]
        else:
            index = rng.randrange(len(alternatives))
            if key is not None:
                choices[key] = index
        covered.add((symbol, index))
        return REFERENCE.sub(
            lambda match: expand(match.group(1), remaining - 1),
            alternatives[index],
        )

    return expand(rule, depth)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--depth", type=int, default=8)
    args = parser.parse_args()
    if args.count <= 0 or args.depth <= 0:
        parser.error("count and depth must be positive")
    rng = random.Random(args.seed)
    try:
        for number in range(1, args.count + 1):
            candidate = derive("file", rng, args.depth)
            sys.stdout.buffer.write(f"--- file {number} ---\n".encode("ascii"))
            sys.stdout.buffer.write(candidate.encode("utf-8"))
            sys.stdout.buffer.write(f"--- end file {number} ---\n".encode("ascii"))
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
