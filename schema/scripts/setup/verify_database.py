"""Verify that an SQLite database matches the final ERD and BCNF files."""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import defaultdict
from contextlib import closing
from pathlib import Path

sys.dont_write_bytecode = True

# Allow VS Code to run this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.scripts.setup.build_database import APPLICATION_ID
from schema.scripts.common.schema_model import (
    CSV_DIR,
    DEFAULT_DATABASE,
    FOREIGN_KEYS,
    PRIMARY_KEYS,
    TABLES,
    fingerprint_version,
    quote,
    source_fingerprint,
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--csv-dir", type=Path, default=CSV_DIR)
    return parser.parse_args()


def csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def actual_relationships(connection: sqlite3.Connection) -> set[tuple[str, tuple[str, ...], str, tuple[str, ...]]]:
    relationships: set[tuple[str, tuple[str, ...], str, tuple[str, ...]]] = set()
    for child in TABLES:
        groups: dict[int, list[tuple[int, str, str, str]]] = defaultdict(list)
        for row in connection.execute(f"PRAGMA foreign_key_list({quote(child)})"):
            groups[row[0]].append((row[1], row[2], row[3], row[4]))
        for rows in groups.values():
            ordered = sorted(rows)
            relationships.add(
                (
                    child,
                    tuple(row[2] for row in ordered),
                    ordered[0][1],
                    tuple(row[3] for row in ordered),
                )
            )
    return relationships


def verify(connection: sqlite3.Connection, csv_dir: Path) -> tuple[list[str], int]:
    problems: list[str] = []
    objects = {
        (row[0], row[1])
        for row in connection.execute(
            "SELECT type, name FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )
    }
    expected_objects = {("table", table) for table in TABLES} | {
        ("view", "Industry_Usage_With_Rate")
    }
    if objects != expected_objects:
        problems.append(f"database objects differ: expected {sorted(expected_objects)}, found {sorted(objects)}")

    total = 0
    for table, expected_columns in TABLES.items():
        info = connection.execute(f"PRAGMA table_info({quote(table)})").fetchall()
        actual_columns = [(row[1], row[2].upper()) for row in info]
        if actual_columns != list(expected_columns):
            problems.append(f"{table} columns or types differ")
        actual_key = tuple(row[1] for row in sorted(info, key=lambda row: row[5]) if row[5])
        if actual_key != PRIMARY_KEYS[table]:
            problems.append(f"{table} primary key differs: {actual_key}")

        database_rows = connection.execute(f"SELECT COUNT(*) FROM {quote(table)}").fetchone()[0]
        source_rows = csv_row_count(csv_dir / f"{table}.csv")
        total += database_rows
        if database_rows != source_rows:
            problems.append(f"{table} has {database_rows:,} rows; CSV has {source_rows:,}")

    relationships = actual_relationships(connection)
    if relationships != set(FOREIGN_KEYS):
        missing = set(FOREIGN_KEYS) - relationships
        extra = relationships - set(FOREIGN_KEYS)
        problems.append(f"foreign keys differ: missing={sorted(missing)}, extra={sorted(extra)}")

    expected_version = fingerprint_version(source_fingerprint(csv_dir))
    application_id = connection.execute("PRAGMA application_id").fetchone()[0]
    user_version = connection.execute("PRAGMA user_version").fetchone()[0]
    if (application_id, user_version) != (APPLICATION_ID, expected_version):
        problems.append("database fingerprint does not match the current schema and CSV files")

    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        problems.append(f"foreign-key check found {len(violations)} violation(s)")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        problems.append(f"integrity check returned: {integrity}")
    return problems, total


def main() -> int:
    args = arguments()
    if not args.database.is_file():
        print(f"Verification stopped: database not found: {args.database}", file=sys.stderr)
        return 2
    try:
        uri = args.database.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            problems, total = verify(connection, args.csv_dir)
    except (OSError, sqlite3.Error, ValueError) as error:
        print(f"Verification stopped: {error}", file=sys.stderr)
        return 2

    if problems:
        print("Database check failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Database check passed.")
    print(f"Checked {len(TABLES)} tables, {len(FOREIGN_KEYS)} relationships, and {total:,} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
