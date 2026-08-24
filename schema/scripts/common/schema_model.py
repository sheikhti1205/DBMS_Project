"""Canonical SQLite model derived from the final report ERD."""

from __future__ import annotations

import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = PROJECT_ROOT / "schema"
CSV_DIR = PROJECT_ROOT / "normalization" / "csv" / "BCNF"
DEFAULT_DATABASE = SCHEMA_DIR / "environment.db"
DEFAULT_SQL = SCHEMA_DIR / "scripts" / "setup" / "schema.sql"
DEFAULT_QUERY_FILE = SCHEMA_DIR / "scripts" / "queries" / "queries.sql"
DEFAULT_BACKUP_DIR = SCHEMA_DIR / "backups"


# Column order is also the required CSV header order.
TABLES: dict[str, tuple[tuple[str, str], ...]] = {
    "Year_Time": (("Year", "INTEGER"),),
    "Month_Time": (("Year", "INTEGER"), ("Month", "INTEGER")),
    "Day_Time": (("Year", "INTEGER"), ("Month", "INTEGER"), ("Day", "INTEGER")),
    "Fiscal_Year": (("Start_Year", "INTEGER"), ("End_Year", "INTEGER")),
    "Station": (("Station_Name", "TEXT"),),
    "District": (("District_Name", "TEXT"),),
    "River": (("River_Name", "TEXT"),),
    "River_Station": (("WQ_Station_Name", "TEXT"), ("River_Name", "TEXT")),
    "Size": (("Size_Name", "TEXT"),),
    "Industrial_Type": (("Industry_Name", "TEXT"),),
    "Temperature_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Type", "TEXT"), ("Temp", "REAL"),
    ),
    "Humidity_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Humidity", "REAL"),
    ),
    "Rainfall_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Rainfall", "REAL"),
    ),
    "Wind_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Type", "TEXT"), ("Wind_Speed", "REAL"), ("Direction", "TEXT"),
    ),
    "Climatic_Event_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Thunderstorm", "REAL"), ("Lightning", "REAL"),
    ),
    "Sunshine_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Day", "INTEGER"), ("Sunshine_Hours", "REAL"),
    ),
    "Radiation_Record": (
        ("Station_Name", "TEXT"), ("Year", "INTEGER"), ("Month", "INTEGER"),
        ("Day", "INTEGER"), ("Sample_No", "INTEGER"), ("Radiation", "REAL"),
    ),
    "Water_Quality": (
        ("WQ_Station_Name", "TEXT"), ("Year", "INTEGER"),
        ("Parameter_Type", "TEXT"), ("Value", "REAL"),
    ),
    "Forest_Area_Record": (
        ("District_Name", "TEXT"), ("Fiscal_Start_Year", "INTEGER"),
        ("Fiscal_End_Year", "INTEGER"), ("Protected_Area", "REAL"),
        ("Unclassed_State_Forest_FD_Acre", "REAL"),
        ("Unclassed_State_Forest_Admin_Acre", "REAL"),
        ("Reserved_Forest_Section_20_Acre", "REAL"),
        ("Reserved_Forest_Section_4_6_Acre", "REAL"),
        ("Acquired_Vested_Forest", "REAL"), ("Total_Forest_FD_Acre", "REAL"),
        ("Total_Forest_Land", "REAL"),
    ),
    "Type_Of_Establishments": (
        ("Size_Name", "TEXT"), ("Start_Year", "INTEGER"),
        ("End_Year", "INTEGER"), ("Quantity", "INTEGER"), ("Percentage", "REAL"),
    ),
    "Industry_Usage": (
        ("Industry_Name", "TEXT"), ("Start_Year", "INTEGER"),
        ("End_Year", "INTEGER"), ("Produced_Waste_Water", "REAL"),
        ("Reused_Waste_Water", "REAL"),
    ),
}

PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "Year_Time": ("Year",),
    "Month_Time": ("Year", "Month"),
    "Day_Time": ("Year", "Month", "Day"),
    "Fiscal_Year": ("Start_Year", "End_Year"),
    "Station": ("Station_Name",),
    "District": ("District_Name",),
    "River": ("River_Name",),
    "River_Station": ("WQ_Station_Name",),
    "Size": ("Size_Name",),
    "Industrial_Type": ("Industry_Name",),
    "Temperature_Record": ("Station_Name", "Year", "Month", "Type"),
    "Humidity_Record": ("Station_Name", "Year", "Month"),
    "Rainfall_Record": ("Station_Name", "Year", "Month"),
    "Wind_Record": ("Station_Name", "Year", "Month", "Type"),
    "Climatic_Event_Record": ("Station_Name", "Year", "Month"),
    "Sunshine_Record": ("Station_Name", "Year", "Month", "Day"),
    "Radiation_Record": ("Station_Name", "Year", "Month", "Day", "Sample_No"),
    "Water_Quality": ("WQ_Station_Name", "Year", "Parameter_Type"),
    "Forest_Area_Record": ("District_Name", "Fiscal_Start_Year", "Fiscal_End_Year"),
    "Type_Of_Establishments": ("Size_Name", "Start_Year", "End_Year"),
    "Industry_Usage": ("Industry_Name", "Start_Year", "End_Year"),
}

# Each tuple represents one relationship in the report ERD.
FOREIGN_KEYS: tuple[tuple[str, tuple[str, ...], str, tuple[str, ...]], ...] = (
    ("Month_Time", ("Year",), "Year_Time", ("Year",)),
    ("Day_Time", ("Year", "Month"), "Month_Time", ("Year", "Month")),
    ("Fiscal_Year", ("Start_Year",), "Year_Time", ("Year",)),
    ("Fiscal_Year", ("End_Year",), "Year_Time", ("Year",)),
    ("River_Station", ("River_Name",), "River", ("River_Name",)),
    ("Temperature_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Temperature_Record", ("Year", "Month"), "Month_Time", ("Year", "Month")),
    ("Humidity_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Humidity_Record", ("Year", "Month"), "Month_Time", ("Year", "Month")),
    ("Rainfall_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Rainfall_Record", ("Year", "Month"), "Month_Time", ("Year", "Month")),
    ("Wind_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Wind_Record", ("Year", "Month"), "Month_Time", ("Year", "Month")),
    ("Climatic_Event_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Climatic_Event_Record", ("Year", "Month"), "Month_Time", ("Year", "Month")),
    ("Sunshine_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Sunshine_Record", ("Year", "Month", "Day"), "Day_Time", ("Year", "Month", "Day")),
    ("Radiation_Record", ("Station_Name",), "Station", ("Station_Name",)),
    ("Radiation_Record", ("Year", "Month", "Day"), "Day_Time", ("Year", "Month", "Day")),
    ("Water_Quality", ("WQ_Station_Name",), "River_Station", ("WQ_Station_Name",)),
    ("Water_Quality", ("Year",), "Year_Time", ("Year",)),
    ("Forest_Area_Record", ("District_Name",), "District", ("District_Name",)),
    ("Forest_Area_Record", ("Fiscal_Start_Year", "Fiscal_End_Year"), "Fiscal_Year", ("Start_Year", "End_Year")),
    ("Type_Of_Establishments", ("Size_Name",), "Size", ("Size_Name",)),
    ("Type_Of_Establishments", ("Start_Year", "End_Year"), "Fiscal_Year", ("Start_Year", "End_Year")),
    ("Industry_Usage", ("Industry_Name",), "Industrial_Type", ("Industry_Name",)),
    ("Industry_Usage", ("Start_Year", "End_Year"), "Fiscal_Year", ("Start_Year", "End_Year")),
)


def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def schema_sql() -> str:
    statements = ["PRAGMA foreign_keys = ON;", ""]
    for table, columns in TABLES.items():
        key_columns = set(PRIMARY_KEYS[table])
        lines = [
            f"  {quote(name)} {kind}{' NOT NULL' if name in key_columns else ''}"
            for name, kind in columns
        ]
        lines.append("  PRIMARY KEY (" + ", ".join(map(quote, PRIMARY_KEYS[table])) + ")")
        for child, child_columns, parent, parent_columns in FOREIGN_KEYS:
            if child == table:
                lines.append(
                    "  FOREIGN KEY ("
                    + ", ".join(map(quote, child_columns))
                    + f") REFERENCES {quote(parent)} ("
                    + ", ".join(map(quote, parent_columns))
                    + ")"
                )
        statements.append(f"CREATE TABLE {quote(table)} (\n" + ",\n".join(lines) + "\n);\n")

    statements.append(
        "CREATE VIEW \"Industry_Usage_With_Rate\" AS\n"
        "SELECT \"Industry_Name\", \"Start_Year\", \"End_Year\",\n"
        "       \"Produced_Waste_Water\", \"Reused_Waste_Water\",\n"
        "       CASE WHEN \"Produced_Waste_Water\" IS NULL OR \"Produced_Waste_Water\" = 0\n"
        "            THEN NULL\n"
        "            ELSE 100.0 * \"Reused_Waste_Water\" / \"Produced_Waste_Water\"\n"
        "       END AS \"Reuse_Percentage\"\n"
        "FROM \"Industry_Usage\";\n"
    )
    return "\n".join(statements)


def source_fingerprint(csv_dir: Path = CSV_DIR) -> str:
    digest = hashlib.sha256(schema_sql().encode("utf-8"))
    for table in TABLES:
        path = csv_dir / f"{table}.csv"
        digest.update(table.encode("utf-8"))
        data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        digest.update(data)
    return digest.hexdigest()


def fingerprint_version(fingerprint: str) -> int:
    return int(fingerprint[:8], 16) & 0x7FFFFFFF
