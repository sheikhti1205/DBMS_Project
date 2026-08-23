# Bangladesh Environmental Data Integration

Group 07 reviewed the selected environmental source files, normalized the records, and loaded the final relations into SQLite. The final ERD in the report is the authority for the database structure.

## Project files

- `normalization/` contains the source extraction code, 0NF-to-BCNF CSV files, exclusions, traceability records, and workbook.
- `schema/` contains the canonical ERD model, generated SQL, SQLite database, query tool, verifier, and separate backup and restore tools.
- `ERD/` contains only the final ERD used as the schema authority.
- `exclusions/` records reviewed source blocks that do not fit the final ERD.

This GitHub repository is the clean coding environment. Original publications, report sources,
and submission copies remain in the project Google Drive and are not duplicated here.

## Build the database

Python 3 is the only requirement when the bundled BCNF files are already present.

Windows PowerShell:

```powershell
py schema\build_db.py
py schema\verify_database.py
```

Linux, WSL, or macOS:

```bash
python3 schema/build_db.py
python3 schema/verify_database.py
```

The first command creates `schema/environment.db` and refreshes `schema/schema.sql`. Running it again keeps the database when its schema and source fingerprint still match. If the existing database differs, the script asks before replacing it in an interactive terminal. Use `--replace` only when replacement is intentional.

## Query the data

```bash
python3 schema/query_database.py tables
python3 schema/query_database.py describe Water_Quality
python3 schema/query_database.py saved rivers
python3 schema/query_database.py saved wastewater
python3 schema/query_database.py run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

The query tool opens the database read-only. Saved examples are kept in `schema/queries.sql` and include climate, rivers, wastewater, and forest data.

## Back up and restore

Backups and restores are deliberately separate from the importer.

```bash
python3 schema/backup_database.py
python3 schema/restore_database.py schema/backups/environment_YYYYMMDD_HHMMSS.db --replace
```

Use `--output` with the backup command or `--database` with either command when a different path is needed.

## Refresh from the selected sources

The source refresh reads all 68 selected raw blocks so that every reviewed block remains traceable. Records that fit the final report ERD continue through BCNF and into the 21 SQLite tables. BMD sunshine blocks B55-B56 cannot be assigned to an ERD station, and groundwater blocks B63-B68 have no groundwater entity in the final ERD, so they remain recorded in the earlier normalization and exclusion material instead of being forced into an unrelated table.

The original selected source files are kept in Google Drive rather than GitHub. Download them beside `normalization/` as `Selected_Source_Files/`, or set `DBMS_SOURCE_DIR`. A full refresh also needs `openpyxl` and `xlrd`.

Windows PowerShell:

```powershell
$env:DBMS_SOURCE_DIR = "C:\path\to\Selected_Source_Files"
py -m pip install openpyxl xlrd
py normalization\extract.py
py normalization\exclusions.py
py normalization\workbook.py
py schema\build_db.py --replace
py schema\verify_database.py
```

Linux, WSL, or macOS:

```bash
export DBMS_SOURCE_DIR="/path/to/Selected_Source_Files"
python3 -m pip install openpyxl xlrd
python3 normalization/extract.py
python3 normalization/exclusions.py
python3 normalization/workbook.py
python3 schema/build_db.py --replace
python3 schema/verify_database.py
```

When the repository is inside a Windows cloud-drive mount, let WSL write the large generated files to its native filesystem:

```bash
export DBMS_NORMALIZATION_DIR="/tmp/dbms-normalization"
export DBMS_EXCLUSIONS_DIR="/tmp/dbms-exclusions"
python3 normalization/extract.py
python3 normalization/exclusions.py
python3 schema/build_db.py --csv-dir "$DBMS_NORMALIZATION_DIR/csv/BCNF" \
  --database /tmp/dbms-environment.db --sql /tmp/dbms-schema.sql --replace
```

Selected source folder: [Google Drive](https://drive.google.com/drive/folders/1SSdmo-VFQ6leS7Gp8hItmksg_SxRMl3q)
