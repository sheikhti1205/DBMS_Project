"""Benchmark every saved competency query against one read-only database."""

from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
import time
from contextlib import closing
from pathlib import Path

from schema.scripts.common.schema_model import (
    DEFAULT_COMPETENCY_BENCHMARK,
    DEFAULT_DATABASE,
    DEFAULT_QUERY_FILE,
)
from schema.scripts.queries.query_database import load_queries


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERY_FILE)
    parser.add_argument("--runs", type=int, default=9)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_COMPETENCY_BENCHMARK,
        help="machine-readable evidence path (default: schema/scripts/competency/benchmark.json)",
    )
    return parser.parse_args()


def percentile_95(values: list[float]) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def _repo_relative(path: Path) -> Path:
    """Return path relative to the repository root when it lives inside it."""
    resolved = path.resolve()
    for parent in resolved.parents:
        if (parent / ".git").is_dir():
            try:
                return resolved.relative_to(parent)
            except ValueError:
                break
    return resolved


def main() -> int:
    args = arguments()
    if not args.database.is_file():
        raise SystemExit(f"database not found: {args.database}")
    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")

    queries = load_queries(args.queries)
    uri = args.database.resolve().as_uri() + "?mode=ro"
    report: dict[str, object] = {
        "database": str(_repo_relative(args.database)),
        "sqlite_version": sqlite3.sqlite_version,
        "runs_per_query": args.runs,
        "queries": {},
    }
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA query_only = ON")
        for name, statement in queries.items():
            # One unmeasured warm-up keeps connection setup out of the timings.
            warmup = connection.execute(statement)
            warmup.fetchall()
            timings = []
            rows: list[tuple[object, ...]] = []
            columns: list[str] = []
            for _ in range(args.runs):
                started = time.perf_counter_ns()
                cursor = connection.execute(statement)
                rows = cursor.fetchall()
                timings.append((time.perf_counter_ns() - started) / 1_000_000)
                columns = [column[0] for column in cursor.description or ()]
            plan = [
                {"id": row[0], "parent": row[1], "detail": row[3]}
                for row in connection.execute("EXPLAIN QUERY PLAN " + statement)
            ] if not statement.lstrip().upper().startswith("PRAGMA") else []
            report["queries"][name] = {
                "columns": columns,
                "row_count": len(rows),
                "sample": rows[:3],
                "timing_ms": {
                    "minimum": round(min(timings), 4),
                    "median": round(statistics.median(timings), 4),
                    "p95": round(percentile_95(timings), 4),
                    "maximum": round(max(timings), 4),
                },
                "query_plan": plan,
            }
        report["integrity_check"] = connection.execute("PRAGMA integrity_check").fetchone()[0]
        report["foreign_key_violations"] = len(
            connection.execute("PRAGMA foreign_key_check").fetchall()
        )

    rendered = json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Benchmark saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
