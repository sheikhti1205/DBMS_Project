"""Publish the verified GitHub files to a non-Git Google Drive folder."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANAGED_DIRECTORIES = ("ERD", "exclusions", "normalization", "schema")
MANAGED_FILES = ("requirements.txt", "setup_windows.bat", "setup_linux.sh")
IGNORED_NAMES = {"__pycache__", "desktop.ini", "Thumbs.db"}
IGNORED_SUFFIXES = {".pyc", ".building", ".restoring"}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--drive",
        required=True,
        type=Path,
        help="existing DBMS_Project folder in Google Drive",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="copy changed files and remove stale files from managed folders",
    )
    return parser.parse_args()


def ignored(path: Path) -> bool:
    return any(part in IGNORED_NAMES for part in path.parts) or path.suffix in IGNORED_SUFFIXES


def preserved(relative: Path) -> bool:
    return len(relative.parts) >= 2 and relative.parts[:2] == ("schema", "backups")


def managed_files(root: Path, *, include_generated: bool = False) -> dict[Path, Path]:
    files: dict[Path, Path] = {}
    for directory in MANAGED_DIRECTORIES:
        base = root / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            relative = path.relative_to(root)
            if preserved(relative):
                continue
            if path.is_file() and (include_generated or not ignored(relative)):
                files[relative] = path
    for name in MANAGED_FILES:
        path = root / name
        if path.is_file():
            files[Path(name)] = path
    return files


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def same_file(source: Path, target: Path) -> bool:
    return target.is_file() and source.stat().st_size == target.stat().st_size and digest(source) == digest(target)


def database_signature(path: Path) -> tuple[object, ...] | None:
    if not path.is_file():
        return None
    try:
        uri = path.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                return None
            if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
                return None
            objects = tuple(
                connection.execute(
                    "SELECT type, name FROM sqlite_master "
                    "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
                )
            )
            tables = [name for kind, name in objects if kind == "table"]
            counts = []
            for name in tables:
                quoted = name.replace('"', '""')
                count = connection.execute(f'SELECT COUNT(*) FROM "{quoted}"').fetchone()[0]
                counts.append((name, count))
            return (
                connection.execute("PRAGMA application_id").fetchone()[0],
                connection.execute("PRAGMA user_version").fetchone()[0],
                objects,
                tuple(counts),
            )
    except (OSError, sqlite3.Error):
        return None


def same_managed_file(relative: Path, source: Path, target: Path) -> bool:
    if relative == Path("schema/environment.db"):
        source_signature = database_signature(source)
        return source_signature is not None and source_signature == database_signature(target)
    return same_file(source, target)


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + ".syncing")
    shutil.copy2(source, staging)
    os.replace(staging, target)


def remove_empty_directories(root: Path) -> None:
    directories = (item for item in root.rglob("*") if item.is_dir())
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass


def main() -> int:
    args = arguments()
    drive = args.drive.expanduser().resolve()
    source = PROJECT_ROOT.resolve()
    if not drive.is_dir():
        print(f"Publish stopped: Drive folder not found: {drive}", file=sys.stderr)
        return 2
    if drive == source or source in drive.parents or drive in source.parents:
        print("Publish stopped: source and destination must be separate project folders.", file=sys.stderr)
        return 2

    source_files = managed_files(source)
    target_files = managed_files(drive, include_generated=True)
    changed = [
        relative
        for relative, source_path in source_files.items()
        if not same_managed_file(relative, source_path, drive / relative)
    ]
    stale = sorted(set(target_files) - set(source_files))

    if not args.apply:
        print(f"Files needing update: {len(changed)}")
        print(f"Stale managed files: {len(stale)}")
        if changed or stale:
            print("Run again with --apply after reviewing the Drive folder.")
            return 1
        print("Drive matches the GitHub project files.")
        return 0

    print("Publishing the verified project files to Drive.")
    for relative in changed:
        copy_file(source_files[relative], drive / relative)
    for relative in stale:
        (drive / relative).unlink()
    for directory in MANAGED_DIRECTORIES:
        base = drive / directory
        if base.is_dir():
            remove_empty_directories(base)

    print(f"Updated files: {len(changed)}")
    print(f"Removed stale managed files: {len(stale)}")
    print("Drive publishing finished. Report and selected source files were not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
