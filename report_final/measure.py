#!/usr/bin/env python3
"""Generate report measurements from the authoritative project artifacts."""

from __future__ import annotations

import json
import hashlib
import math
import re
import sqlite3
from pathlib import Path

REPORT = Path(__file__).resolve().parent
APPROVED_ERD = REPORT / "Final_erd.png"
APPROVED_ERD_SHA256 = (
    "06e387af21aa29cc8abc75cc7baaa369eee85ff15cc9ebf050139cbb1f332672"
)


def verify_approved_erd() -> None:
    actual = hashlib.sha256(APPROVED_ERD.read_bytes()).hexdigest()
    if actual != APPROVED_ERD_SHA256:
        raise RuntimeError(
            "Final_erd.png is not the approved Group-07 final ERD: "
            f"expected {APPROVED_ERD_SHA256}, found {actual}"
        )


def find_project_root(start: Path) -> Path:
    """Locate the repository root from a live or archived report source."""
    for candidate in (start, *start.parents):
        if (candidate / "schema" / "environment.db").is_file():
            return candidate
    raise FileNotFoundError(
        f"Could not find schema/environment.db above report source {start}"
    )


ROOT = find_project_root(REPORT)
verify_approved_erd()
DATABASE = ROOT / "schema" / "environment.db"
CONTRACT = ROOT / "schema" / "erd_contract.json"
STATISTICS = ROOT / "normalization" / "STATISTICS.md"
QUALITY_LOG = ROOT / "normalization" / "DATA_QUALITY_LOG.md"
BENCHMARK = ROOT / "schema" / "validation" / "competency" / "benchmark.json"
EXCLUSION_SUMMARY = ROOT / "normalization" / "exclusions" / "summary.json"
SOURCE_INVENTORY = REPORT / "source_inventory.json"
OUT = REPORT / "generated"
OUT.mkdir(parents=True, exist_ok=True)


def grouped(value: int) -> str:
    return f"{value:,}".replace(",", "{,}")


def latex_text(value: object) -> str:
    text = str(value)
    for old, new in (("_", r"\_"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#")):
        text = text.replace(old, new)
    return text


def markdown_rows(section: str) -> list[list[str]]:
    text = STATISTICS.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(section)}\..*?(?=^## |\Z)", text, re.M | re.S)
    if not match:
        raise RuntimeError(f"statistics section {section} not found")
    result: list[list[str]] = []
    for line in match.group(0).splitlines():
        if not line.startswith("|") or set(line) <= {"|", "-", " ", ":"}:
            continue
        cells = [cell.strip().strip("*") for cell in line.strip("|").split("|")]
        headers = {"Organisation", "Block", "Stage", "Relation", "Reference set"}
        if cells and cells[0] not in headers:
            result.append(cells)
    return result


contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
connection = sqlite3.connect(DATABASE)
tables = list(contract["tables"])
table_rows = {
    table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    for table in tables
}
views = [row[0] for row in connection.execute(
    "SELECT name FROM sqlite_schema WHERE type='view' ORDER BY name"
)]
column_count = sum(len(columns) for columns in contract["tables"].values())
integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
fk_violations = len(connection.execute("PRAGMA foreign_key_check").fetchall())

macros: dict[str, str] = {
    "DbTables": str(len(tables)),
    "DbViews": str(len(views)),
    "DbColumns": str(column_count),
    "DbRows": grouped(sum(table_rows.values())),
    "DbPk": str(len(contract["primary_keys"])),
    "DbFk": str(len(contract["foreign_keys"])),
    "DbIntegrity": integrity,
    "DbFkViolations": str(fk_violations),
    "DbMiB": f"{DATABASE.stat().st_size / 1024 / 1024:.1f}",
}

first_year, last_year = connection.execute(
    "SELECT MIN(Year), MAX(Year) FROM Year_Time"
).fetchone()
macros.update({"YearMin": str(first_year), "YearMax": str(last_year)})

source_rows = [
    ("BBS", 36, 181_600, 176_442),
    ("BMD", 20, 14_688, 14_688),
    ("BRRI", 5, 3_252_182, 600_166),
    ("BWDB", 1, None, 405),
]
macros.update({
    "SourceOrganisations": "4",
    "SourceFiles": "9",
    "SourceBlocks": grouped(sum(row[1] for row in source_rows)),
    "ZeroColumns": grouped(2_308),
    "RawValues": grouped(3_448_470),
    "RowsOffered": grouped(sum(row[3] for row in source_rows)),
    "CellsRead": grouped(3_717_305),
    "CellsMissing": grouped(268_835),
    "CellsMissingPct": "7.2",
})
exclusions = json.loads(EXCLUSION_SUMMARY.read_text(encoding="utf-8"))
inventory = json.loads(SOURCE_INVENTORY.read_text(encoding="utf-8"))
if sum(item["collected"] for item in inventory["sources"]) != inventory["source_data_files"]:
    raise RuntimeError("source inventory collected-file total does not balance")
if sum(item["loaded"] for item in inventory["sources"]) != inventory["loaded_files"]:
    raise RuntimeError("source inventory loaded-file total does not balance")
if inventory["source_blocks"] != sum(row[1] for row in source_rows):
    raise RuntimeError("source inventory source-block total does not balance")
if (
    inventory["derived_artifacts"]
    + inventory["support_files"]
    + inventory["source_data_files"]
    != inventory["all_files"]
):
    raise RuntimeError("Drive inventory classification does not balance")
if sum(inventory["file_types"].values()) != inventory["all_files"]:
    raise RuntimeError("Drive inventory file-type total does not balance")
macros.update({
    "AllDriveFiles": grouped(inventory["all_files"]),
    "DerivedArtifacts": grouped(inventory["derived_artifacts"]),
    "SupportFiles": grouped(inventory["support_files"]),
    "SourceDataFiles": grouped(inventory["source_data_files"]),
    "SourceFiles": grouped(inventory["loaded_files"]),
    "SourceBlocks": grouped(inventory["source_blocks"]),
    "CandidateFiles": grouped(inventory["source_data_files"] + inventory["support_files"]),
    "SheetsTotal": grouped(exclusions["sheets_total"]),
    "SheetsUsed": grouped(exclusions["sheets_used"]),
    "SheetsExcluded": grouped(exclusions["sheets_excluded"]),
})

with (OUT / "source_inventory.dat").open("w", encoding="utf-8") as handle:
    handle.write("source collected loaded excluded\n")
    for item in inventory["sources"]:
        handle.write(
            f"{item['name']} {item['collected']} {item['loaded']} "
            f"{item['collected'] - item['loaded']}\n"
        )

with (OUT / "source_file_types.tex").open("w", encoding="utf-8") as handle:
    for file_type, count in inventory["file_types"].items():
        handle.write(f"{latex_text(file_type)} & {grouped(count)} " + r"\\" + "\n")
quality_text = QUALITY_LOG.read_text(encoding="utf-8")
quality_total = re.search(
    r"Total problem occurrences recorded: \*\*(\d+)\*\* across \*\*(\d+)\*\*",
    quality_text,
)
if not quality_total:
    raise RuntimeError("data-quality total not found")
macros["ProblemTotal"] = grouped(int(quality_total.group(1)))
macros["ProblemClasses"] = quality_total.group(2)
for source, blocks, _values, offered in source_rows:
    macros[f"Blocks{source}"] = str(blocks)
    macros[f"Offered{source}"] = grouped(offered)

with (OUT / "sources.dat").open("w", encoding="utf-8") as handle:
    handle.write("source blocks offered\n")
    for source, blocks, _values, offered in source_rows:
        handle.write(f"{source} {blocks} {offered}\n")

stage_totals: dict[str, tuple[int, int]] = {}
for row in markdown_rows("3"):
    if len(row) < 3 or not row[2].replace(",", "").isdigit():
        continue
    stage, _relation, count = row[:3]
    relation_count, total = stage_totals.get(stage, (0, 0))
    stage_totals[stage] = (relation_count + 1, total + int(count.replace(",", "")))
stage_totals["BCNF"] = (len(tables), sum(table_rows.values()))
stage_macro = {"1NF": "OneNF", "2NF": "TwoNF", "3NF": "ThreeNF", "BCNF": "BCNF"}
for stage, (relations, rows) in stage_totals.items():
    if stage in stage_macro:
        macros[f"{stage_macro[stage]}Rels"] = str(relations)
        macros[f"{stage_macro[stage]}Rows"] = grouped(rows)

with (OUT / "stages.dat").open("w", encoding="utf-8") as handle:
    handle.write("stage relations rows\n")
    handle.write(f"0NF {sum(row[1] for row in source_rows)} 6559\n")
    for stage in ("1NF", "2NF", "3NF", "BCNF"):
        relations, rows = stage_totals[stage]
        handle.write(f"{stage} {relations} {rows}\n")

with (OUT / "stage_profile.dat").open("w", encoding="utf-8") as handle:
    handle.write("stage relations rows millions\n")
    handle.write(
        f"Offered {sum(row[1] for row in source_rows)} "
        f"{sum(row[3] for row in source_rows)} "
        f"{sum(row[3] for row in source_rows) / 1_000_000:.6f}\n"
    )
    for stage in ("1NF", "2NF", "3NF", "BCNF"):
        relations, rows = stage_totals[stage]
        handle.write(f"{stage} {relations} {rows} {rows / 1_000_000:.6f}\n")

coverage_sql = """
SELECT 'Temperature' AS relation, MIN(Year), MAX(Year) FROM Temperature_Record
UNION ALL SELECT 'Humidity', MIN(Year), MAX(Year) FROM Humidity_Record
UNION ALL SELECT 'Rainfall', MIN(Year), MAX(Year) FROM Rainfall_Record
UNION ALL SELECT 'Wind', MIN(Year), MAX(Year) FROM Wind_Record
UNION ALL SELECT 'Events', MIN(Year), MAX(Year) FROM Climatic_Event_Record
UNION ALL SELECT 'Sunshine', MIN(Year), MAX(Year) FROM Sunshine_Record
UNION ALL SELECT 'Radiation', MIN(Year), MAX(Year) FROM Radiation_Record
UNION ALL SELECT 'Water quality', MIN(Year), MAX(Year) FROM Water_Quality
UNION ALL SELECT 'Forest area', MIN(Fiscal_Start_Year), MAX(Fiscal_End_Year) FROM Forest_Area_Record
UNION ALL SELECT 'Industry use', MIN(Start_Year), MAX(End_Year) FROM Industry_Usage
ORDER BY 2, 1
"""
with (OUT / "time_coverage.dat").open("w", encoding="utf-8") as handle:
    handle.write("relation start end\n")
    for relation, start, end in connection.execute(coverage_sql):
        handle.write(f"{{{relation}}} {start} {end}\n")

annual_temperature = connection.execute(
    """SELECT Year, AVG(Temp), COUNT(*) FROM Temperature_Record
       WHERE Type='Maximum' AND Temp IS NOT NULL
       GROUP BY Year HAVING COUNT(*) >= 100 ORDER BY Year"""
).fetchall()
with (OUT / "annual_temperature.dat").open("w", encoding="utf-8") as handle:
    handle.write("year value records\n")
    for year, value, records in annual_temperature:
        handle.write(f"{year} {value:.4f} {records}\n")

annual_rainfall = connection.execute(
    """SELECT Year, AVG(Rainfall), COUNT(*) FROM Rainfall_Record
       WHERE Rainfall IS NOT NULL GROUP BY Year ORDER BY Year"""
).fetchall()
with (OUT / "annual_rainfall.dat").open("w", encoding="utf-8") as handle:
    handle.write("year value records\n")
    for year, value, records in annual_rainfall:
        handle.write(f"{year} {value:.4f} {records}\n")

water_quality_labels = {
    "Dissolved Oxygen": "DO",
    "pH": "pH",
    "Biochemical Oxygen Demand": "BOD",
    "Chemical Oxygen Demand": "COD",
    "Salinity": "Salinity",
    "Plastic and Marine Debris": "MarineDebris",
}
water_quality_counts = connection.execute(
    """SELECT Parameter_Type, COUNT(*) FROM Water_Quality
       GROUP BY Parameter_Type ORDER BY COUNT(*) DESC, Parameter_Type"""
).fetchall()
with (OUT / "water_quality_parameters.dat").open("w", encoding="utf-8") as handle:
    handle.write("parameter records\n")
    for parameter, count in water_quality_counts:
        handle.write(f"{water_quality_labels[parameter]} {count}\n")

early = [row[1] for row in annual_temperature[:5]]
recent = [row[1] for row in annual_temperature[-5:]]
macros["TempEarlyMean"] = f"{sum(early) / len(early):.2f}"
macros["TempRecentMean"] = f"{sum(recent) / len(recent):.2f}"
macros["TempDifference"] = f"{sum(recent) / len(recent) - sum(early) / len(early):.2f}"

complete = connection.execute(
    """SELECT Maximum_Temperature, Humidity, Rainfall FROM Monthly_Climate_Summary
       WHERE Maximum_Temperature IS NOT NULL
         AND Humidity IS NOT NULL AND Rainfall IS NOT NULL"""
).fetchall()


def correlation(left: list[float], right: list[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((a - left_mean) ** 2 for a in left)
        * sum((b - right_mean) ** 2 for b in right)
    )
    return numerator / denominator


temperatures = [float(row[0]) for row in complete]
humidities = [float(row[1]) for row in complete]
rainfalls = [float(row[2]) for row in complete]
macros["CompleteClimateRows"] = grouped(len(complete))
macros["TempHumidityCorrelation"] = f"{correlation(temperatures, humidities):.3f}"
macros["HumidityRainfallCorrelation"] = f"{correlation(humidities, rainfalls):.3f}"

macros["UnmappedStations"] = grouped(
    connection.execute("SELECT COUNT(*) FROM Station WHERE District_Name IS NULL").fetchone()[0]
)
macros["TemperatureRowsTwentyTwenty"] = grouped(
    connection.execute("SELECT COUNT(*) FROM Temperature_Record WHERE Year=2020").fetchone()[0]
)
macros["WaterQualityConnected"] = grouped(
    connection.execute(
        """SELECT COUNT(*) FROM Water_Quality w JOIN River_Station rs
           ON rs.WQ_Station_Name=w.WQ_Station_Name"""
    ).fetchone()[0]
)
macros["IndustryRows"] = grouped(table_rows["Industry_Usage"])

ranking = connection.execute(
    """SELECT Station_Name, COUNT(*), ROUND(AVG(Rainfall),2), ROUND(MAX(Rainfall),2)
       FROM Rainfall_Record WHERE Rainfall IS NOT NULL
       GROUP BY Station_Name HAVING COUNT(*) >= 100
       ORDER BY AVG(Rainfall) DESC, Station_Name LIMIT 5"""
).fetchall()
macros["WettestStation"] = latex_text(ranking[0][0])
macros["WettestMeasurements"] = grouped(ranking[0][1])
macros["WettestAverage"] = f"{ranking[0][2]:.2f}"
macros["WettestMaximum"] = f"{ranking[0][3]:.2f}"
with (OUT / "rainfall_ranking.tex").open("w", encoding="utf-8") as handle:
    for station, count, average, maximum in ranking:
        handle.write(
            f"{latex_text(station)} & {grouped(count)} & {average:.2f} & {maximum:.2f} "
            + r"\\"
            + "\n"
        )

missing_rows = connection.execute(
    """SELECT 'Temperature.Temp', SUM(Temp IS NULL), COUNT(*) FROM Temperature_Record
       UNION ALL SELECT 'Humidity.Humidity', SUM(Humidity IS NULL), COUNT(*) FROM Humidity_Record
       UNION ALL SELECT 'Rainfall.Rainfall', SUM(Rainfall IS NULL), COUNT(*) FROM Rainfall_Record
       UNION ALL SELECT 'Wind.Speed', SUM(Wind_Speed IS NULL), COUNT(*) FROM Wind_Record
       UNION ALL SELECT 'Water_Quality.Value', SUM(Value IS NULL), COUNT(*) FROM Water_Quality
       UNION ALL SELECT 'Station.District_Name', SUM(District_Name IS NULL), COUNT(*) FROM Station
       UNION ALL SELECT 'Forest.Reserved_Section_4_6', SUM(Reserved_Forest_Section_4_6_Acre IS NULL), COUNT(*) FROM Forest_Area_Record"""
).fetchall()
with (OUT / "missing_measurements.tex").open("w", encoding="utf-8") as handle:
    for field, missing, total in missing_rows:
        handle.write(
            f"{latex_text(field)} & {grouped(missing)} & {grouped(total)} & "
            f"{100 * missing / total:.2f}\\%" + r" \\" + "\n"
        )

with (OUT / "relations.tex").open("w", encoding="utf-8") as handle:
    for table in sorted(tables):
        primary_key = ", ".join(contract["primary_keys"][table])
        handle.write(
            f"{latex_text(table)} & {latex_text(primary_key)} & "
            f"{len(contract['tables'][table])} & {grouped(table_rows[table])} "
            + r"\\"
            + "\n"
        )

benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
macros["BenchmarkRuns"] = str(benchmark["runs_per_query"])
macros["SQLiteVersion"] = latex_text(benchmark["sqlite_version"])
with (OUT / "competency_results.tex").open("w", encoding="utf-8") as handle:
    labels = {
        "climate": "Monthly climate retrieval",
        "rivers": "Water quality--river join",
        "rainfall-ranking": "Rainfall ranking",
        "missing-measurements": "Missing-value audit",
        "integrity": "Full integrity check",
        "foreign-key-check": "Foreign-key check",
    }
    for key, label in labels.items():
        result = benchmark["queries"][key]
        timing = result["timing_ms"]
        handle.write(
            f"{label} & {result['row_count']} & {timing['median']:.4f} & "
            f"{timing['p95']:.4f} " + r"\\" + "\n"
        )

with (OUT / "measured.tex").open("w", encoding="utf-8") as handle:
    handle.write("% Generated by report/measure.py; do not edit manually.\n")
    for name in sorted(macros):
        handle.write(f"\\newcommand{{\\m{name}}}{{{macros[name]}}}\n")

connection.close()
print(f"Generated report measurements from {DATABASE}")
