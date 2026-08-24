"""Run a short, read-only demonstration of the environmental database."""

from __future__ import annotations

import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.dont_write_bytecode = True

# Allow VS Code to run this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.scripts.queries.query_database import load_queries
from schema.scripts.common.schema_model import DEFAULT_DATABASE


DATABASE = DEFAULT_DATABASE
DEMO_QUERIES = (
    ("table-counts", 30),
    ("time-coverage", 20),
    ("water-quality-summary", 8),
    ("rainfall-ranking", 8),
    ("wastewater", 8),
    ("missing-measurements", 10),
)


def show_rows(connection: sqlite3.Connection, title: str, sql: str, limit: int) -> None:
    print(f"\n{title.replace('-', ' ').title()}")
    cursor = connection.execute(sql)
    rows = cursor.fetchmany(limit)
    headers = [column[0] for column in cursor.description or ()]
    if not headers:
        print("No columns returned.")
        return
    widths = [len(header) for header in headers]
    values = [["" if value is None else str(value) for value in row] for row in rows]
    for row in values:
        for index, value in enumerate(row):
            widths[index] = min(40, max(widths[index], len(value)))
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in values:
        print("  ".join(value[: widths[index]].ljust(widths[index]) for index, value in enumerate(row)))
    print(f"Shown: {len(values)} row(s)")


def main() -> int:
    if not DATABASE.is_file():
        print(f"Database not found: {DATABASE}", file=sys.stderr)
        return 2
    print("Opening the ByteForge database in read-only mode.")
    try:
        queries = load_queries()
        uri = DATABASE.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            violations = connection.execute("PRAGMA foreign_key_check").fetchall()
            print(f"Integrity check: {integrity}")
            print(f"Foreign-key violations: {len(violations)}")
            for name, limit in DEMO_QUERIES:
                show_rows(connection, name, queries[name], limit)
    except (OSError, KeyError, sqlite3.Error) as error:
        print(f"Demo stopped: {error}", file=sys.stderr)
        return 2
    print("\nDemo finished. The database was not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
