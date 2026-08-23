"""Build the SQLite database from the final BCNF CSV files."""

from __future__ import annotations

import argparse
import csv
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from schema_model import (
    CSV_DIR,
    DEFAULT_DATABASE,
    DEFAULT_SQL,
    FOREIGN_KEYS,
    TABLES,
    fingerprint_version,
    quote,
    schema_sql,
    source_fingerprint,
)


APPLICATION_ID = 0x42464F52  # BFOR


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--sql", type=Path, default=DEFAULT_SQL)
    parser.add_argument("--csv-dir", type=Path, default=CSV_DIR)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="replace a database whose data or schema fingerprint is different",
    )
    return parser.parse_args()


def read_rows(csv_dir: Path) -> dict[str, list[tuple[object, ...]]]:
    loaded: dict[str, list[tuple[object, ...]]] = {}
    for table, columns in TABLES.items():
        path = csv_dir / f"{table}.csv"
        expected = [name for name, _ in columns]
        try:
            handle = path.open(newline="", encoding="utf-8-sig")
        except OSError as error:
            raise RuntimeError(f"Cannot read {path}: {error}") from error

        with handle:
            reader = csv.reader(handle)
            actual = next(reader, None)
            if actual != expected:
                raise RuntimeError(
                    f"Unexpected header in {path.name}.\n"
                    f"Expected: {','.join(expected)}\n"
                    f"Found:    {','.join(actual or [])}"
                )
            rows: list[tuple[object, ...]] = []
            for line_number, raw in enumerate(reader, start=2):
                if len(raw) != len(columns):
                    raise RuntimeError(
                        f"{path.name}:{line_number} has {len(raw)} fields; "
                        f"expected {len(columns)}."
                    )
                try:
                    rows.append(tuple(convert(value, kind) for value, (_, kind) in zip(raw, columns)))
                except ValueError as error:
                    raise RuntimeError(f"{path.name}:{line_number}: {error}") from error
        loaded[table] = rows
    return loaded


def convert(value: str, kind: str) -> object:
    value = value.strip()
    if not value:
        return None
    if kind == "INTEGER":
        return int(value)
    if kind == "REAL":
        return float(value)
    return value


def database_version(path: Path) -> tuple[int, int] | None:
    if not path.exists():
        return None
    try:
        uri = path.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            application_id = connection.execute("PRAGMA application_id").fetchone()[0]
            user_version = connection.execute("PRAGMA user_version").fetchone()[0]
            return application_id, user_version
    except sqlite3.Error:
        return (-1, -1)


def replacement_allowed(path: Path, expected_version: int, replace: bool) -> bool:
    current = database_version(path)
    if current is None:
        return True
    if current == (APPLICATION_ID, expected_version):
        print("Found the current database. Keeping it.")
        return False
    if replace:
        print("Cleaning old data.")
        return True
    if not sys.stdin.isatty():
        raise RuntimeError(
            "Found a different database. Run again with --replace after checking it, "
            "or create a backup first."
        )
    try:
        answer = input("Found a different database. Replace it? [y/N] ").strip().lower()
    except EOFError as error:
        raise RuntimeError(
            "Found a different database. Run again with --replace after checking it, "
            "or create a backup first."
        ) from error
    if answer not in {"y", "yes"}:
        print("Keeping the existing database.")
        return False
    print("Cleaning old data.")
    return True


def build_database(path: Path, ddl: str, rows: dict[str, list[tuple[object, ...]]], version: int) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + ".building")
    if staging.exists():
        staging.unlink()

    total = 0
    try:
        with closing(sqlite3.connect(staging)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(f"PRAGMA application_id = {APPLICATION_ID}")
            connection.execute(f"PRAGMA user_version = {version}")
            connection.executescript(ddl)
            for table, values in rows.items():
                columns = [name for name, _ in TABLES[table]]
                placeholders = ", ".join("?" for _ in columns)
                statement = (
                    f"INSERT INTO {quote(table)} ("
                    + ", ".join(map(quote, columns))
                    + f") VALUES ({placeholders})"
                )
                connection.executemany(statement, values)
                total += len(values)
            violations = connection.execute("PRAGMA foreign_key_check").fetchall()
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            if violations:
                raise RuntimeError(f"Foreign-key check found {len(violations)} violation(s).")
            if integrity != "ok":
                raise RuntimeError(f"SQLite integrity check returned: {integrity}")
            connection.commit()
        os.replace(staging, path)
    except Exception:
        if staging.exists():
            staging.unlink()
        raise
    return total


def write_sql(path: Path, ddl: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(path.name + ".building")
    staging.write_text(ddl, encoding="utf-8", newline="\n")
    os.replace(staging, path)


def main() -> int:
    args = arguments()
    try:
        fingerprint = source_fingerprint(args.csv_dir)
        version = fingerprint_version(fingerprint)
        if not replacement_allowed(args.database, version, args.replace):
            return 0
        print("Importing BCNF data.")
        rows = read_rows(args.csv_dir)
        ddl = schema_sql()
        total = build_database(args.database, ddl, rows, version)
        write_sql(args.sql, ddl)
    except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
        print(f"Import stopped: {error}", file=sys.stderr)
        return 2

    print(f"Database ready: {args.database}")
    print(f"Loaded {total:,} rows into {len(TABLES)} tables with {len(FOREIGN_KEYS)} relationships.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
