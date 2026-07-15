English | [简体中文](FINDINGS.zh-CN.md)

# Grammar and mutation findings

Recorded for the 16 July 2026 experiment. All inputs are synthetic and all checks run locally. These commands each allocate 1,000 candidates to each strategy:

```sh
python3 compare.py --budget 1000 --seed 120012
python3 compare.py --budget 1000 --seed 1
python3 compare.py --budget 1000 --seed 2
```

The commands were run with Python 3.12.13. All eight unit tests passed.

| Seed | Budget per strategy | Grammar alternatives | Grammar accepted | Mutation accepted | Grammar rejection categories | Mutation rejection categories |
| --- | --- | --- | --- | --- | --- | --- |
| 120012 | 1,000 | 89 / 89 | 506 | 64 | 1 | 8 |
| 1 | 1,000 | 89 / 89 | 502 | 51 | 1 | 7 |
| 2 | 1,000 | 89 / 89 | 466 | 47 | 1 | 6 |

Exact output, in command order:

```json
{"seed": 120012, "budget": 1000, "grammar_alternatives_covered": 89, "grammar_alternatives_total": 89, "grammar_accepted": 506, "mutation_accepted": 64, "grammar_distinct_rejections": 1, "mutation_distinct_rejections": 8}
{"seed": 1, "budget": 1000, "grammar_alternatives_covered": 89, "grammar_alternatives_total": 89, "grammar_accepted": 502, "mutation_accepted": 51, "grammar_distinct_rejections": 1, "mutation_distinct_rejections": 7}
{"seed": 2, "budget": 1000, "grammar_alternatives_covered": 89, "grammar_alternatives_total": 89, "grammar_accepted": 466, "mutation_accepted": 47, "grammar_distinct_rejections": 1, "mutation_distinct_rejections": 6}
```

Grammar reached inputs that passed the full local parsing and field-validation check in 46.6–50.6% of candidates. Mutation rarely reached that point in these runs: 4.7–6.4% passed. This supports using the bounded grammar to supply inputs for deeper accepted-input testing. It does not establish how far either strategy would execute inside the product.

All 89 grammar alternatives were selected in each run, but this is neither complete combination coverage nor product coverage. Grammar's only rejection category was `unknown_header`, caused by the optional extra columns. ADR 0003 rejects those columns; this explains why structurally valid grammar output was not always accepted. Since real exports often carry such columns, the team should check whether the product follows this rule and whether the rule should stay.

Mutation reached more rejection categories than the grammar was written to produce. Replaying the same mutation streams showed UTF-8, unknown-header, row-width, date, time and holiday failures in all three runs; bare-CR failures appeared for seeds 120012 and 1, and a header-delimiter failure appeared for seed 120012. Mutating an accepted file can break individual fields while leaving surrounding structure intact, although one to three byte edits can also affect multiple fields. The seed here is a realistic accepted synthetic file, not a sample of real payroll data. These counts record only the first reported reason per file; they do not measure separate internal execution paths.

The product campaign should keep both grammar generation and mutation of accepted files. Grammar supplies varied supported forms that often survive validation; mutation adds malformed inputs outside those rules. Judge the campaign by the product's HTTP response, and check parsed values such as holiday flags at the product boundary. This local check is a reachability proxy, not the product oracle; no HTTP requests were made in this experiment.

Three seeds and one mutation seed file are a limited comparison. Candidate budgets are equal, but input lengths, execution time and numbers of unique files are not controlled. No conclusion about defect discovery, throughput or production acceptance follows from these measurements. Quoted-newline policy and other differences from the product are described in the [README](README.md).
