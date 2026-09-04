"""Independent behavior checks for the delivered database and saved queries."""

from __future__ import annotations

import csv
import math
import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema.scripts.queries.query_database import load_queries

DATABASE = ROOT / "schema" / "environment.db"
QUERY_FILE = ROOT / "schema" / "sql" / "queries.sql"

EXPECTED_COLUMNS = {
    "climate": ["Station_Name", "Year", "Month", "Maximum_Temperature", "Minimum_Temperature", "Humidity", "Rainfall", "Thunderstorm", "Lightning"],
    "wind": ["Station_Name", "Year", "Month", "Maximum_Wind_Speed", "Maximum_Wind_Direction", "Minimum_Wind_Speed", "Minimum_Wind_Direction"],
    "rivers": ["River_Name", "WQ_Station_Name", "Year", "Parameter_Type", "Value"],
    "wastewater": ["Industry_Name", "Start_Year", "End_Year", "Quantity", "Percentage"],
    "forests": ["District_Name", "Fiscal_Start_Year", "Fiscal_End_Year", "Protected_Area", "Total_Forest_FD_Acre", "Total_Forest_Land"],
    "table-counts": ["Table_Name", "Records"],
    "relationships": ["Child_Table", "Child_Columns", "Parent_Table", "Parent_Columns"],
    "time-coverage": ["Relation", "First_Year", "Last_Year"],
    "rainfall-ranking": ["Station_Name", "Measurements", "Average_Rainfall", "Highest_Rainfall"],
    "water-quality-summary": ["River_Name", "Parameter_Type", "Measurements", "First_Year", "Last_Year", "Average_Value"],
    "missing-measurements": ["Field", "Missing", "Total"],
    "integrity": ["integrity_check"],
    "foreign-key-check": ["table", "rowid", "parent", "fkid"],
}


def queries_from_file() -> dict[str, str]:
    return load_queries(QUERY_FILE)


class DatabaseAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        uri = DATABASE.resolve().as_uri() + "?mode=ro"
        cls.connection = sqlite3.connect(uri, uri=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.connection.close()

    def test_every_named_query_has_expected_columns(self) -> None:
        queries = queries_from_file()
        self.assertEqual(set(EXPECTED_COLUMNS), set(queries))
        for name, expected in EXPECTED_COLUMNS.items():
            with self.subTest(query=name):
                cursor = self.connection.execute(queries[name])
                actual = [column[0] for column in cursor.description or ()]
                self.assertEqual(expected, actual)
                cursor.fetchmany(3)

    def test_views_do_not_multiply_monthly_rows(self) -> None:
        duplicate_climate = self.connection.execute(
            """
            SELECT COUNT(*) FROM (
              SELECT Station_Name, Year, Month, COUNT(*) AS n
              FROM Monthly_Climate_Summary
              GROUP BY Station_Name, Year, Month
              HAVING n > 1
            )
            """
        ).fetchone()[0]
        duplicate_wind = self.connection.execute(
            """
            SELECT COUNT(*) FROM (
              SELECT Station_Name, Year, Month, COUNT(*) AS n
              FROM Monthly_Wind_Summary
              GROUP BY Station_Name, Year, Month
              HAVING n > 1
            )
            """
        ).fetchone()[0]
        self.assertEqual(0, duplicate_climate)
        self.assertEqual(0, duplicate_wind)

    def test_unresolved_station_districts_are_null(self) -> None:
        count = self.connection.execute(
            "SELECT COUNT(*) FROM Station WHERE District_Name IS NULL"
        ).fetchone()[0]
        with (ROOT / "normalization" / "review" / "UNMAPPED_STATIONS.csv").open(
            encoding="utf-8"
        ) as handle:
            review_lines = sum(1 for _ in handle) - 1
        self.assertEqual(review_lines, count)

    def test_brri_monthly_values_recompute_from_retained_daily_rows(self) -> None:
        one_nf = ROOT / "normalization" / "csv" / "1NF"
        sources = {
            "Max_Temp": ("BRRI_Maximum_Temperature_Daily_1NF.csv", "maximum"),
            "Min_Temp": ("BRRI_Minimum_Temperature_Daily_1NF.csv", "minimum"),
            "Rainfall": ("BRRI_Rainfall_Daily_1NF.csv", "sum"),
            "Humidity": ("BRRI_Humidity_Daily_1NF.csv", "average"),
        }
        calculated: dict[tuple[str, str, str, int, int], tuple[int, float]] = {}
        for measure, (filename, rule) in sources.items():
            groups: dict[tuple[str, str, str, int, int], list[float]] = {}
            with (one_nf / filename).open(newline="", encoding="utf-8-sig") as handle:
                for row in csv.DictReader(handle):
                    key = (
                        row["Block"], measure, row["Station_Name"],
                        int(row["Year"]), int(row["Month"]),
                    )
                    value = float(row["Value"])
                    state = groups.get(key)
                    if state is None:
                        groups[key] = [1.0, value]
                        continue
                    state[0] += 1
                    if rule == "maximum":
                        state[1] = max(state[1], value)
                    elif rule == "minimum":
                        state[1] = min(state[1], value)
                    else:
                        state[1] += value
            for key, (count, value) in groups.items():
                monthly = value / count if rule == "average" else value
                calculated[key] = (int(count), round(monthly, 4))

        audited: dict[tuple[str, str, str, int, int], tuple[int, float]] = {}
        with (ROOT / "normalization" / "review" / "BRRI_MONTHLY_AGGREGATION.csv").open(
            newline="", encoding="utf-8-sig"
        ) as handle:
            for row in csv.DictReader(handle):
                key = (
                    row["Block"], row["Measure"], row["Station_Name"],
                    int(row["Year"]), int(row["Month"]),
                )
                audited[key] = (int(row["Daily_Readings"]), float(row["Monthly_Value"]))
        self.assertEqual(set(audited), set(calculated))
        for key, (count, value) in audited.items():
            with self.subTest(key=key):
                calculated_count, calculated_value = calculated[key]
                self.assertEqual(count, calculated_count)
                self.assertTrue(math.isclose(value, calculated_value, abs_tol=0.0001))


if __name__ == "__main__":
    unittest.main()
