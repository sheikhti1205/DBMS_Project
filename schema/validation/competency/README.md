# Competency benchmark evidence

`benchmark.json` is the canonical machine-readable record produced by the
saved competency queries against `schema/environment.db`. It records result
columns, row counts, small result samples, query plans, median and p95 timings,
SQLite integrity status and foreign-key violations.

Regenerate it from the repository root after an intentional database or query
change:

```bash
python3 -B -m schema.scripts.queries.benchmark_database
```

The currently retained evidence contains 13 saved queries with 9 measured runs
per query. It reports `PRAGMA integrity_check = ok` and zero foreign-key
violations. At the time this evidence was moved into its permanent location,
the database SHA-256 was
`b9ad6707b5296cc517034d9c4675433b0416dac4993768646a17eeac0da9bfc9`.

The JSON is authoritative evidence. The LaTeX table under
`report_final/generated/competency_results.tex` is a report-specific rendering
generated from it.
