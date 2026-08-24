"""Create a separate, consistent backup of the SQLite database."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from contextlib import closing
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True

# Allow VS Code to run this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.scripts.common.schema_model import DEFAULT_BACKUP_DIR, DEFAULT_DATABASE


def arguments() -> argparse.Namespace:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default = DEFAULT_BACKUP_DIR / f"environment_{stamp}.db"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=default)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = arguments()
    if not args.database.is_file():
        print(f"Backup stopped: database not found: {args.database}", file=sys.stderr)
        return 2
    if args.output.exists() and not args.replace:
        print(f"Backup stopped: output already exists: {args.output}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    staging = args.output.with_name(args.output.name + ".building")
    if staging.exists():
        staging.unlink()
    try:
        source_uri = args.database.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(source_uri, uri=True)) as source, closing(sqlite3.connect(staging)) as target:
            source.backup(target)
        with closing(sqlite3.connect(staging)) as check:
            integrity = check.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"backup integrity check returned: {integrity}")
        staging.replace(args.output)
    except (OSError, RuntimeError, sqlite3.Error) as error:
        if staging.exists():
            staging.unlink()
        print(f"Backup stopped: {error}", file=sys.stderr)
        return 2

    print(f"Backup saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
