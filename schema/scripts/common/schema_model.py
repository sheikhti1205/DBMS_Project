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
DEFAULT_COMPETENCY_BENCHMARK = (
    SCHEMA_DIR / "validation" / "competency" / "benchmark.json"
)

APPLICATION_ID = 0x42464F52  # "BFOR" used as the SQLite application_id marker


# Column order is also the required CSV header order.
TABLES: dict[str, tuple[tuple[str, str], ...]] = {
    "Year_Time": (("Year", "INTEGER"),),
    "Month_Time": (("Year", "INTEGER"), ("Month", "INTEGER")),
    "Day_Time": (("Year", "INTEGER"), ("Month", "INTEGER"), ("Day", "INTEGER")),
    "Fiscal_Year": (("Start_Year", "INTEGER"), ("End_Year", "INTEGER")),
    "District": (("District_Name", "TEXT"),),
    "Station": (("Station_Name", "TEXT"), ("District_Name", "TEXT")),
    "River": (("River_Name", "TEXT"),),
    "River_Station": (("WQ_Station_Name", "TEXT"), ("River_Name", "TEXT")),
    "Size": (("Size_Name", "TEXT"),),
    "Industry_Type": (("Industry_Name", "TEXT"),),
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
        ("End_Year", "INTEGER"), ("Quantity", "REAL"),
        ("Percentage", "REAL"),
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
    "Industry_Type": ("Industry_Name",),
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
    ("Station", ("District_Name",), "District", ("District_Name",)),
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
    ("Industry_Usage", ("Industry_Name",), "Industry_Type", ("Industry_Name",)),
    ("Industry_Usage", ("Start_Year", "End_Year"), "Fiscal_Year", ("Start_Year", "End_Year")),
)


# Only this foreign key may be unknown because the selected sources do not
# publish a complete station-to-district crosswalk.
NULLABLE_FOREIGN_KEYS = {("Station", "District_Name")}


CHECKS: dict[str, tuple[str, ...]] = {
    "Year_Time": ('"Year" BETWEEN 1900 AND 2100',),
    "Month_Time": ('"Month" BETWEEN 1 AND 12',),
    "Day_Time": (
        '"Month" BETWEEN 1 AND 12',
        '"Day" BETWEEN 1 AND 31',
        "strftime('%Y-%m-%d', printf('%04d-%02d-%02d', \"Year\", \"Month\", \"Day\")) = printf('%04d-%02d-%02d', \"Year\", \"Month\", \"Day\")",
    ),
    "Fiscal_Year": ('"End_Year" = "Start_Year" + 1',),
    "Temperature_Record": (
        '"Type" IN (\'Maximum\', \'Minimum\')',
        '"Temp" IS NULL OR "Temp" BETWEEN -5 AND 50',
    ),
    "Humidity_Record": ('"Humidity" IS NULL OR "Humidity" BETWEEN 0 AND 100',),
    "Rainfall_Record": ('"Rainfall" IS NULL OR "Rainfall" BETWEEN 0 AND 3000',),
    "Wind_Record": (
        '"Type" IN (\'Maximum\', \'Minimum\')',
        '"Wind_Speed" IS NULL OR "Wind_Speed" BETWEEN 0 AND 250',
    ),
    "Climatic_Event_Record": (
        '"Thunderstorm" IS NULL OR "Thunderstorm" >= 0',
        '"Lightning" IS NULL OR "Lightning" >= 0',
    ),
    "Sunshine_Record": ('"Sunshine_Hours" IS NULL OR "Sunshine_Hours" BETWEEN 0 AND 14',),
    "Radiation_Record": (
        '"Sample_No" >= 0',
        '"Radiation" IS NULL OR "Radiation" >= 0',
    ),
    "Water_Quality": (
        '"Value" IS NULL OR CASE WHEN "Parameter_Type" = \'pH\' THEN "Value" BETWEEN 0 AND 14 ELSE "Value" >= 0 END',
    ),
    "Forest_Area_Record": (
        '"Protected_Area" IS NULL OR "Protected_Area" >= 0',
        '"Unclassed_State_Forest_FD_Acre" IS NULL OR "Unclassed_State_Forest_FD_Acre" >= 0',
        '"Unclassed_State_Forest_Admin_Acre" IS NULL OR "Unclassed_State_Forest_Admin_Acre" >= 0',
        '"Reserved_Forest_Section_20_Acre" IS NULL OR "Reserved_Forest_Section_20_Acre" >= 0',
        '"Reserved_Forest_Section_4_6_Acre" IS NULL OR "Reserved_Forest_Section_4_6_Acre" >= 0',
        '"Acquired_Vested_Forest" IS NULL OR "Acquired_Vested_Forest" >= 0',
        '"Total_Forest_FD_Acre" IS NULL OR "Total_Forest_FD_Acre" >= 0',
        '"Total_Forest_Land" IS NULL OR "Total_Forest_Land" >= 0',
    ),
    "Type_Of_Establishments": (
        '"Quantity" IS NULL OR "Quantity" >= 0',
        '"Percentage" IS NULL OR "Percentage" BETWEEN 0 AND 100',
    ),
    "Industry_Usage": (
        '"Quantity" IS NULL OR "Quantity" >= 0',
        '"Percentage" IS NULL OR "Percentage" BETWEEN 0 AND 100',
    ),
}


def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def schema_sql() -> str:
    statements = ["PRAGMA foreign_keys = ON;", ""]
    for table, columns in TABLES.items():
        required_columns = set(PRIMARY_KEYS[table])
        for child, child_columns, _parent, _parent_columns in FOREIGN_KEYS:
            if child == table:
                required_columns.update(
                    column
                    for column in child_columns
                    if (table, column) not in NULLABLE_FOREIGN_KEYS
                )
        lines = [
            f"  {quote(name)} {kind}{' NOT NULL' if name in required_columns else ''}"
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
        for expression in CHECKS.get(table, ()):
            lines.append(f"  CHECK ({expression})")
        statements.append(f"CREATE TABLE {quote(table)} (\n" + ",\n".join(lines) + "\n);\n")

    statements.append(
        "CREATE VIEW \"Monthly_Climate_Summary\" AS\n"
        "WITH \"Monthly_Keys\" AS (\n"
        "  SELECT \"Station_Name\", \"Year\", \"Month\" FROM \"Temperature_Record\"\n"
        "  UNION SELECT \"Station_Name\", \"Year\", \"Month\" FROM \"Humidity_Record\"\n"
        "  UNION SELECT \"Station_Name\", \"Year\", \"Month\" FROM \"Rainfall_Record\"\n"
        "  UNION SELECT \"Station_Name\", \"Year\", \"Month\" FROM \"Climatic_Event_Record\"\n"
        ")\n"
        "SELECT k.\"Station_Name\", k.\"Year\", k.\"Month\",\n"
        "       MAX(CASE WHEN t.\"Type\" = 'Maximum' THEN t.\"Temp\" END) AS \"Maximum_Temperature\",\n"
        "       MAX(CASE WHEN t.\"Type\" = 'Minimum' THEN t.\"Temp\" END) AS \"Minimum_Temperature\",\n"
        "       h.\"Humidity\", r.\"Rainfall\", e.\"Thunderstorm\", e.\"Lightning\"\n"
        "FROM \"Monthly_Keys\" AS k\n"
        "LEFT JOIN \"Temperature_Record\" AS t ON t.\"Station_Name\" = k.\"Station_Name\" AND t.\"Year\" = k.\"Year\" AND t.\"Month\" = k.\"Month\"\n"
        "LEFT JOIN \"Humidity_Record\" AS h ON h.\"Station_Name\" = k.\"Station_Name\" AND h.\"Year\" = k.\"Year\" AND h.\"Month\" = k.\"Month\"\n"
        "LEFT JOIN \"Rainfall_Record\" AS r ON r.\"Station_Name\" = k.\"Station_Name\" AND r.\"Year\" = k.\"Year\" AND r.\"Month\" = k.\"Month\"\n"
        "LEFT JOIN \"Climatic_Event_Record\" AS e ON e.\"Station_Name\" = k.\"Station_Name\" AND e.\"Year\" = k.\"Year\" AND e.\"Month\" = k.\"Month\"\n"
        "GROUP BY k.\"Station_Name\", k.\"Year\", k.\"Month\", h.\"Humidity\", r.\"Rainfall\", e.\"Thunderstorm\", e.\"Lightning\";\n\n"
        "CREATE VIEW \"Monthly_Wind_Summary\" AS\n"
        "SELECT \"Station_Name\", \"Year\", \"Month\",\n"
        "       MAX(CASE WHEN \"Type\" = 'Maximum' THEN \"Wind_Speed\" END) AS \"Maximum_Wind_Speed\",\n"
        "       MAX(CASE WHEN \"Type\" = 'Maximum' THEN \"Direction\" END) AS \"Maximum_Wind_Direction\",\n"
        "       MAX(CASE WHEN \"Type\" = 'Minimum' THEN \"Wind_Speed\" END) AS \"Minimum_Wind_Speed\",\n"
        "       MAX(CASE WHEN \"Type\" = 'Minimum' THEN \"Direction\" END) AS \"Minimum_Wind_Direction\"\n"
        "FROM \"Wind_Record\"\n"
        "GROUP BY \"Station_Name\", \"Year\", \"Month\";\n"
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
