"""Verify SQLite independently against the report ERD contract and BCNF files."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections import defaultdict
from contextlib import closing
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.scripts.common.schema_model import (
    APPLICATION_ID,
    CSV_DIR,
    DEFAULT_DATABASE,
    DEFAULT_SQL,
    fingerprint_version,
    quote,
    schema_sql,
    source_fingerprint,
)

CONTRACT_PATH = PROJECT_ROOT / "schema" / "erd_contract.json"
DEFAULT_REVIEW_DIR = PROJECT_ROOT / "normalization" / "review"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--csv-dir", type=Path, default=CSV_DIR)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--schema-sql", type=Path, default=DEFAULT_SQL)
    parser.add_argument("--review-dir", type=Path, default=DEFAULT_REVIEW_DIR)
    return parser.parse_args()


def load_contract(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        contract = json.load(handle)
    if contract.get("version") != 1:
        raise ValueError(f"Unsupported ERD contract version in {path}")
    return contract


def csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def expected_version(csv_dir: Path) -> int:
    return fingerprint_version(source_fingerprint(csv_dir))


def actual_relationships(
    connection: sqlite3.Connection, tables: list[str]
) -> set[tuple[str, tuple[str, ...], str, tuple[str, ...]]]:
    relationships: set[tuple[str, tuple[str, ...], str, tuple[str, ...]]] = set()
    for child in tables:
        groups: dict[int, list[tuple[int, str, str, str]]] = defaultdict(list)
        for row in connection.execute(f"PRAGMA foreign_key_list({quote(child)})"):
            groups[row[0]].append((row[1], row[2], row[3], row[4]))
        for rows in groups.values():
            ordered = sorted(rows)
            relationships.add(
                (child, tuple(row[2] for row in ordered), ordered[0][1], tuple(row[3] for row in ordered))
            )
    return relationships


def scalar(connection: sqlite3.Connection, statement: str) -> int:
    return int(connection.execute(statement).fetchone()[0])


def verify_review_files(problems: list[str], review_dir: Path) -> None:
    required = {
        "VALUE_CONFLICTS.csv",
        "QUARANTINED_ROWS.csv",
        "UNMAPPED_STATIONS.csv",
        "BRRI_MONTHLY_AGGREGATION.csv",
        "BLOCK_ACCOUNTING.csv",
        "ROW_ACCOUNTING.csv",
    }
    missing = sorted(name for name in required if not (review_dir / name).is_file())
    if missing:
        problems.append(f"review files missing: {missing}")
        return
    with (review_dir / "ROW_ACCOUNTING.csv").open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    unbalanced = []
    for row in rows:
        calculated = (
            int(row["Rows_Accepted"])
            + int(row["Identical_Duplicates"])
            + int(row["Displaced_Conflicts"])
            + int(row["Quarantined_Rows"])
        )
        if row.get("Balances") != "yes" or int(row["Rows_Input_To_Resolution"]) != calculated:
            unbalanced.append(row.get("Relation", "?"))
    if not rows or unbalanced:
        problems.append(f"row accounting does not balance: {unbalanced or 'no rows'}")
    with (review_dir / "BLOCK_ACCOUNTING.csv").open(newline="", encoding="utf-8-sig") as handle:
        blocks = list(csv.DictReader(handle))
    expected_blocks = [f"B{number:02d}" for number in range(1, 63)]
    found_blocks = [row.get("Block") for row in blocks]
    bad_blocks = [
        row.get("Block", "?")
        for row in blocks
        if row.get("Balances") != "yes"
        or int(row["Cells_Read"])
        != int(row["Values_Parsed"]) + int(row["Missing_Or_Unusable"])
    ]
    block_mismatch = set(found_blocks) != set(expected_blocks) or len(found_blocks) != len(expected_blocks)
    if block_mismatch or bad_blocks:
        problems.append(
            f"source block accounting differs: block mismatch={block_mismatch}, "
            f"unbalanced={bad_blocks}"
        )
    with (review_dir / "QUARANTINED_ROWS.csv").open(newline="", encoding="utf-8-sig") as handle:
        quarantine_reasons = {row["Reason"] for row in csv.DictReader(handle)}
    required_reasons = {
        "header or note text parsed as a station",
        "Chemical Oxygen Demand cannot be negative",
        "pH outside 0-14",
    }
    if not required_reasons.issubset(quarantine_reasons):
        problems.append(
            f"known malformed water-quality rows are missing from quarantine: "
            f"{sorted(required_reasons - quarantine_reasons)}"
        )
    with (review_dir / "VALUE_CONFLICTS.csv").open(newline="", encoding="utf-8-sig") as handle:
        conflicts = sum(1 for _ in csv.DictReader(handle))
    if conflicts == 0:
        problems.append("source conflict register is empty")


def verify(
    connection: sqlite3.Connection,
    csv_dir: Path,
    contract: dict[str, object],
    schema_path: Path,
    review_dir: Path,
) -> tuple[list[str], int]:
    problems: list[str] = []
    tables = list(contract["tables"])
    views = list(contract["views"])
    objects = {
        (row[0], row[1])
        for row in connection.execute(
            "SELECT type, name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )
    }
    expected_objects = {("table", table) for table in tables} | {("view", view) for view in views}
    if objects != expected_objects:
        problems.append(
            f"database objects differ: missing={sorted(expected_objects - objects)}, "
            f"extra={sorted(objects - expected_objects)}"
        )

    total = 0
    for table, expected_columns in contract["tables"].items():
        info = connection.execute(f"PRAGMA table_info({quote(table)})").fetchall()
        actual_columns = [(row[1], row[2].upper(), bool(row[3])) for row in info]
        wanted_columns = [(name, kind, required) for name, kind, required in expected_columns]
        if actual_columns != wanted_columns:
            problems.append(f"{table} columns, types, or nullability differ")
        actual_key = tuple(row[1] for row in sorted(info, key=lambda row: row[5]) if row[5])
        wanted_key = tuple(contract["primary_keys"][table])
        if actual_key != wanted_key:
            problems.append(f"{table} primary key differs: expected {wanted_key}, found {actual_key}")
        path = csv_dir / f"{table}.csv"
        if not path.is_file():
            problems.append(f"missing BCNF file: {path.name}")
            continue
        with path.open(newline="", encoding="utf-8-sig") as handle:
            header = next(csv.reader(handle), [])
        if header != [column[0] for column in expected_columns]:
            problems.append(f"{path.name} header differs from the ERD contract")
        database_rows = scalar(connection, f"SELECT COUNT(*) FROM {quote(table)}")
        source_rows = csv_row_count(path)
        total += database_rows
        if database_rows != source_rows:
            problems.append(f"{table} has {database_rows:,} rows; CSV has {source_rows:,}")

    for view, expected_columns in contract["view_columns"].items():
        actual = [row[1] for row in connection.execute(f"PRAGMA table_info({quote(view)})")]
        if actual != expected_columns:
            problems.append(f"{view} columns differ: expected {expected_columns}, found {actual}")

    expected_relationships = {
        (child, tuple(child_columns), parent, tuple(parent_columns))
        for child, child_columns, parent, parent_columns in contract["foreign_keys"]
    }
    relationships = actual_relationships(connection, tables)
    if relationships != expected_relationships:
        problems.append(
            f"foreign keys differ: missing={sorted(expected_relationships - relationships)}, "
            f"extra={sorted(relationships - expected_relationships)}"
        )

    for table, fragments in contract["required_checks"].items():
        row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        normalized = (row[0] if row else "").upper().replace('"', "")
        for fragment in fragments:
            if fragment not in normalized:
                problems.append(f"{table} is missing required check fragment: {fragment}")

    version = expected_version(csv_dir)
    actual_version = (scalar(connection, "PRAGMA application_id"), scalar(connection, "PRAGMA user_version"))
    if actual_version != (APPLICATION_ID, version):
        problems.append("database fingerprint does not match the current schema and CSV files")

    committed_schema = (
        schema_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    )
    if committed_schema != schema_sql():
        problems.append(
            "schema.sql is out of sync with the canonical model; "
            "run build_database --replace to regenerate it"
        )

    quality_checks = {
        "invalid calendar dates": """
            SELECT COUNT(*) FROM Day_Time WHERE
            strftime('%Y-%m-%d', printf('%04d-%02d-%02d', Year, Month, Day))
            <> printf('%04d-%02d-%02d', Year, Month, Day)
        """,
        "invalid fiscal spans": "SELECT COUNT(*) FROM Fiscal_Year WHERE End_Year <> Start_Year + 1",
        "invalid temperature types": "SELECT COUNT(*) FROM Temperature_Record WHERE Type NOT IN ('Maximum','Minimum')",
        "invalid wind types": "SELECT COUNT(*) FROM Wind_Record WHERE Type NOT IN ('Maximum','Minimum')",
        "minimum temperature above maximum": """
            SELECT COUNT(*) FROM (
              SELECT Station_Name, Year, Month
              FROM Temperature_Record
              GROUP BY Station_Name, Year, Month
              HAVING MAX(CASE WHEN Type='Minimum' THEN Temp END) >
                     MAX(CASE WHEN Type='Maximum' THEN Temp END)
            )
        """,
        "invalid humidity": "SELECT COUNT(*) FROM Humidity_Record WHERE Humidity NOT BETWEEN 0 AND 100",
        "invalid water quality": "SELECT COUNT(*) FROM Water_Quality WHERE (Parameter_Type='pH' AND Value NOT BETWEEN 0 AND 14) OR (Parameter_Type<>'pH' AND Value < 0)",
        "invalid establishment percentages": "SELECT COUNT(*) FROM Type_Of_Establishments WHERE Percentage NOT BETWEEN 0 AND 100",
        "invalid industry calculations": "SELECT COUNT(*) FROM Industry_Usage WHERE Quantity < 0 OR Percentage NOT BETWEEN 0 AND 100",
    }
    for label, statement in quality_checks.items():
        count = scalar(connection, statement)
        if count:
            problems.append(f"{label}: {count} row(s)")

    bad_percentage_groups = scalar(
        connection,
        """
        SELECT COUNT(*) FROM (
          SELECT Start_Year, End_Year
          FROM Type_Of_Establishments
          WHERE Percentage IS NOT NULL
          GROUP BY Start_Year, End_Year
          HAVING ABS(SUM(Percentage) - 100.0) > 1.0
        )
        """,
    )
    if bad_percentage_groups:
        problems.append(f"establishment percentage totals differ from 100: {bad_percentage_groups} group(s)")

    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        problems.append(f"foreign-key check found {len(violations)} violation(s)")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        problems.append(f"integrity check returned: {integrity}")
    verify_review_files(problems, review_dir)
    return problems, total


def main() -> int:
    args = arguments()
    if not args.database.is_file():
        print(f"Verification stopped: database not found: {args.database}")
        return 2
    try:
        contract = load_contract(args.contract)
        uri = args.database.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            problems, total = verify(
                connection, args.csv_dir, contract, args.schema_sql, args.review_dir
            )
    except (OSError, sqlite3.Error, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Verification stopped: {error}")
        return 2
    if problems:
        print("Database check failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Database check passed.")
    print(
        f"Checked {len(contract['tables'])} tables, {len(contract['foreign_keys'])} "
        f"relationships, {len(contract['views'])} views, and {total:,} rows."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
