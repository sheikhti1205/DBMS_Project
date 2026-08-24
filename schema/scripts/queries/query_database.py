"""Browse and query the delivered database without changing it."""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.dont_write_bytecode = True

# Allow VS Code to run this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.scripts.common.schema_model import DEFAULT_DATABASE, DEFAULT_QUERY_FILE, quote


QUERY_FILE = DEFAULT_QUERY_FILE
QUERY_MARKER = re.compile(r"^-- name: ([a-z][a-z0-9_-]*)\s*$", re.MULTILINE)


def load_queries(path: Path = QUERY_FILE) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    markers = list(QUERY_MARKER.finditer(text))
    queries: dict[str, str] = {}
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        body = text[marker.end():end].strip()
        lines = [line for line in body.splitlines() if not line.lstrip().startswith("--")]
        queries[marker.group(1)] = "\n".join(lines).strip()
    return queries


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("tables", help="list available tables and views")
    describe = commands.add_parser("describe", help="show the columns in one table or view")
    describe.add_argument("name")
    saved = commands.add_parser("saved", help="run a saved query from queries.sql")
    saved.add_argument("name", nargs="?", default="list")
    run = commands.add_parser("run", help="run one read-only SQL statement")
    run.add_argument("sql")
    return parser.parse_args()


def print_rows(headers: list[str], rows: list[tuple[object, ...]], truncated: bool = False) -> None:
    values = [["" if value is None else str(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in values:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in values:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
    print(f"\n{len(rows):,} row(s) shown" + ("; more rows are available." if truncated else "."))


def execute(connection: sqlite3.Connection, sql: str) -> None:
    cursor = connection.execute(sql)
    if cursor.description is None:
        print("The statement returned no columns.")
        return
    fetched = cursor.fetchmany(201)
    print_rows([column[0] for column in cursor.description], fetched[:200], len(fetched) > 200)


def main() -> int:
    args = arguments()
    if not args.database.is_file():
        print(f"Query stopped: database not found: {args.database}", file=sys.stderr)
        return 2
    try:
        uri = args.database.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            if args.command == "tables":
                execute(
                    connection,
                    "SELECT type AS Type, name AS Name FROM sqlite_master "
                    "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name",
                )
            elif args.command == "describe":
                found = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE name = ? AND type IN ('table', 'view')",
                    (args.name,),
                ).fetchone()
                if not found:
                    raise RuntimeError(f"table or view not found: {args.name}")
                execute(connection, f"PRAGMA table_info({quote(args.name)})")
            elif args.command == "saved":
                queries = load_queries()
                if args.name == "list":
                    print("Saved queries: " + ", ".join(sorted(queries)))
                elif args.name not in queries:
                    raise RuntimeError(
                        f"saved query not found: {args.name}. Available: {', '.join(sorted(queries))}"
                    )
                else:
                    execute(connection, queries[args.name])
            else:
                execute(connection, args.sql)
    except (OSError, RuntimeError, sqlite3.Error) as error:
        print(f"Query stopped: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
