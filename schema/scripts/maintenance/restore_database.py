"""Restore an SQLite database from a backup file."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.dont_write_bytecode = True

# Allow VS Code to run this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.scripts.common.schema_model import DEFAULT_DATABASE


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backup", type=Path)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def replacement_allowed(path: Path, replace: bool) -> bool:
    if not path.exists() or replace:
        return True
    if not sys.stdin.isatty():
        print("Restore stopped: the destination exists. Use --replace after checking it.", file=sys.stderr)
        return False
    try:
        answer = input("The destination database exists. Replace it? [y/N] ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def main() -> int:
    args = arguments()
    if not args.backup.is_file():
        print(f"Restore stopped: backup not found: {args.backup}", file=sys.stderr)
        return 2
    if not replacement_allowed(args.database, args.replace):
        return 2

    args.database.parent.mkdir(parents=True, exist_ok=True)
    staging = args.database.with_name(args.database.name + ".restoring")
    if staging.exists():
        staging.unlink()
    try:
        backup_uri = args.backup.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(backup_uri, uri=True)) as source:
            integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise RuntimeError(f"backup integrity check returned: {integrity}")
            with closing(sqlite3.connect(staging)) as target:
                source.backup(target)
        os.replace(staging, args.database)
    except (OSError, RuntimeError, sqlite3.Error) as error:
        if staging.exists():
            staging.unlink()
        print(f"Restore stopped: {error}", file=sys.stderr)
        return 2

    print(f"Database restored: {args.database}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
