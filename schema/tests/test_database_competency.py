"""End-to-end competency and operational tests for the delivered database."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "schema" / "environment.db"
CONTRACT = ROOT / "schema" / "erd_contract.json"


def quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def run_module(*arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, "-B", "-m", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
    )
    if completed.returncode != expected:
        raise AssertionError(
            f"command returned {completed.returncode}, expected {expected}: "
            f"{' '.join(arguments)}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def open_read_only(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA query_only = ON")
    return connection


def logical_digest(path: Path, tables: list[str]) -> str:
    digest = hashlib.sha256()
    with closing(open_read_only(path)) as connection:
        for table in sorted(tables):
            columns = [row[1] for row in connection.execute(f"PRAGMA table_info({quote(table)})")]
            primary_key = [
                row[1]
                for row in sorted(
                    connection.execute(f"PRAGMA table_info({quote(table)})"),
                    key=lambda row: row[5],
                )
                if row[5]
            ]
            order = primary_key or columns
            statement = (
                f"SELECT {', '.join(map(quote, columns))} FROM {quote(table)} "
                f"ORDER BY {', '.join(map(quote, order))}"
            )
            digest.update(table.encode("utf-8"))
            for row in connection.execute(statement):
                digest.update(
                    json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                )
                digest.update(b"\n")
    return digest.hexdigest()


class DatabaseCompetencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.tables = list(cls.contract["tables"])
        cls.temporary = tempfile.TemporaryDirectory(prefix="dbms-competency-")
        cls.temp_dir = Path(cls.temporary.name)
        cls.rebuilt = cls.temp_dir / "rebuilt.db"
        cls.generated_sql = cls.temp_dir / "schema.sql"
        cls.backup = cls.temp_dir / "backup.db"
        cls.restored = cls.temp_dir / "restored.db"

        run_module(
            "schema.scripts.setup.build_database",
            "--database",
            str(cls.rebuilt),
            "--sql",
            str(cls.generated_sql),
        )
        run_module(
            "schema.scripts.setup.verify_database", "--database", str(cls.rebuilt)
        )
        run_module(
            "schema.scripts.maintenance.backup_database",
            "--database",
            str(DATABASE),
            "--output",
            str(cls.backup),
        )
        run_module(
            "schema.scripts.maintenance.restore_database",
            str(cls.backup),
            "--database",
            str(cls.restored),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_integrity_and_foreign_keys_pass(self) -> None:
        with closing(open_read_only(DATABASE)) as connection:
            self.assertEqual("ok", connection.execute("PRAGMA integrity_check").fetchone()[0])
            self.assertEqual([], connection.execute("PRAGMA foreign_key_check").fetchall())

    def test_all_primary_keys_are_unique(self) -> None:
        with closing(open_read_only(DATABASE)) as connection:
            for table, key in self.contract["primary_keys"].items():
                columns = ", ".join(map(quote, key))
                statement = (
                    f"SELECT COUNT(*) FROM (SELECT {columns}, COUNT(*) AS copies "
                    f"FROM {quote(table)} GROUP BY {columns} HAVING copies > 1)"
                )
                with self.subTest(table=table):
                    self.assertEqual(0, connection.execute(statement).fetchone()[0])

    def test_required_contract_columns_have_no_nulls(self) -> None:
        with closing(open_read_only(DATABASE)) as connection:
            for table, columns in self.contract["tables"].items():
                for column, _kind, required in columns:
                    if not required:
                        continue
                    with self.subTest(table=table, column=column):
                        self.assertEqual(
                            0,
                            connection.execute(
                                f"SELECT COUNT(*) FROM {quote(table)} "
                                f"WHERE {quote(column)} IS NULL"
                            ).fetchone()[0],
                        )

    def test_database_is_safe_to_distribute_read_only(self) -> None:
        with closing(open_read_only(DATABASE)) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("CREATE TABLE Competency_Write_Should_Fail (id INTEGER)")

    def test_constraints_reject_bad_mutations(self) -> None:
        with closing(sqlite3.connect(self.rebuilt)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            station = connection.execute(
                "SELECT Station_Name, District_Name FROM Station ORDER BY Station_Name LIMIT 1"
            ).fetchone()
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO Station (Station_Name, District_Name) VALUES (?, ?)", station
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO Station (Station_Name, District_Name) VALUES (?, ?)",
                    ("__competency_orphan_station__", "__missing_district__"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO Day_Time (Year, Month, Day) VALUES (2024, 2, 30)"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE Water_Quality SET Value = 99 "
                    "WHERE rowid = (SELECT rowid FROM Water_Quality WHERE Parameter_Type = 'pH' LIMIT 1)"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE Rainfall_Record SET Rainfall = -1 "
                    "WHERE rowid = (SELECT rowid FROM Rainfall_Record LIMIT 1)"
                )
            connection.rollback()

    def test_competency_questions_return_meaningful_results(self) -> None:
        questions = {
            "temperature_records_2020": (
                "SELECT COUNT(*) FROM Temperature_Record WHERE Year = 2020",
                lambda rows: rows == [(882,)],
            ),
            "forest_district_coverage": (
                "SELECT District_Name, COUNT(*) FROM Forest_Area_Record "
                "GROUP BY District_Name ORDER BY District_Name",
                lambda rows: len(rows) == 35 and all(row[1] > 0 for row in rows),
            ),
            "water_quality_connected_to_rivers": (
                "SELECT rs.River_Name, COUNT(*) FROM Water_Quality w "
                "JOIN River_Station rs ON rs.WQ_Station_Name = w.WQ_Station_Name "
                "GROUP BY rs.River_Name ORDER BY rs.River_Name",
                lambda rows: len(rows) > 20 and sum(row[1] for row in rows) == 2327,
            ),
            "wettest_station_ranking": (
                "SELECT Station_Name, MAX(Rainfall) FROM Rainfall_Record "
                "WHERE Rainfall IS NOT NULL GROUP BY Station_Name "
                "ORDER BY MAX(Rainfall) DESC LIMIT 5",
                lambda rows: len(rows) == 5 and rows[0][1] >= rows[-1][1],
            ),
            "industry_wastewater": (
                "SELECT Industry_Name, Start_Year, End_Year, Quantity, Percentage "
                "FROM Industry_Usage ORDER BY Start_Year",
                lambda rows: len(rows) == 3,
            ),
            "time_coverage": (
                "SELECT MIN(Year), MAX(Year) FROM Year_Time",
                lambda rows: rows == [(1948, 2024)],
            ),
            "controlled_missing_station_districts": (
                "SELECT COUNT(*) FROM Station WHERE District_Name IS NULL",
                lambda rows: rows == [(40,)],
            ),
        }
        with closing(open_read_only(DATABASE)) as connection:
            for name, (statement, predicate) in questions.items():
                rows = connection.execute(statement).fetchall()
                with self.subTest(question=name):
                    self.assertTrue(predicate(rows), rows[:5])

    def test_monthly_views_preserve_declared_grain(self) -> None:
        with closing(open_read_only(DATABASE)) as connection:
            for view in ("Monthly_Climate_Summary", "Monthly_Wind_Summary"):
                duplicates = connection.execute(
                    f"SELECT COUNT(*) FROM ("
                    f"SELECT Station_Name, Year, Month, COUNT(*) AS copies FROM {quote(view)} "
                    f"GROUP BY Station_Name, Year, Month HAVING copies > 1)"
                ).fetchone()[0]
                with self.subTest(view=view):
                    self.assertEqual(0, duplicates)

    def test_clean_rebuild_and_restore_are_logically_identical(self) -> None:
        expected = logical_digest(DATABASE, self.tables)
        self.assertEqual(expected, logical_digest(self.rebuilt, self.tables))
        self.assertEqual(expected, logical_digest(self.restored, self.tables))

    def test_builder_protects_an_unrelated_existing_database(self) -> None:
        destination = self.temp_dir / "unrelated.db"
        with closing(sqlite3.connect(destination)) as connection:
            connection.execute("CREATE TABLE Keep_Me (value TEXT)")
            connection.execute("INSERT INTO Keep_Me VALUES ('preserved')")
            connection.commit()
        completed = run_module(
            "schema.scripts.setup.build_database",
            "--database",
            str(destination),
            "--sql",
            str(self.temp_dir / "unrelated.sql"),
            expected=2,
        )
        self.assertIn("Found a different database", completed.stderr)
        with closing(sqlite3.connect(destination)) as connection:
            self.assertEqual(
                "preserved", connection.execute("SELECT value FROM Keep_Me").fetchone()[0]
            )

    def test_corrupt_backup_is_rejected_without_destination(self) -> None:
        corrupt = self.temp_dir / "corrupt.db"
        destination = self.temp_dir / "corrupt-restored.db"
        corrupt.write_bytes(b"not a SQLite database")
        completed = run_module(
            "schema.scripts.maintenance.restore_database",
            str(corrupt),
            "--database",
            str(destination),
            expected=2,
        )
        self.assertIn("Restore stopped", completed.stderr)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
