# Bangladesh Environmental Data Integration

ByteForge Scrum Group 07 normalized the selected environmental records and loaded the final BCNF relations into SQLite. The final ERD in `ERD/` is the authority for the database structure.

## Project layout

- `ERD/` contains only the final ERD.
- `normalization/` contains the generated workbook, normalization CSVs, statistics, data-quality log, and its `scripts/` folder.
- `schema/environment.db` is the ready-to-query SQLite database.
- `schema/scripts/setup/` builds and verifies the database.
- `schema/scripts/queries/` contains the read-only query tool, saved SQL, and demonstration.
- `schema/scripts/maintenance/` contains separate backup and restore tools.
- `exclusions/` records source material that was reviewed but was not forced into the final ERD.
- `tools/publish_to_drive.py` updates the non-Git Google Drive copy without touching its report or selected source files.

The WSL checkout is the coding source of truth and the only Git repository. Google Drive is a non-Git project mirror containing the selected sources and the report workspace.

## Automatic setup

Python 3.10 or newer is required. SQLite support is included with normal Python installations, so a separate SQLite installation is not required.

Windows:

```bat
setup_windows.bat
```

Linux, WSL, or macOS:

```bash
./setup_linux.sh
```

Each launcher creates a private environment outside the project folder, installs the pinned packages, refreshes `schema/environment.db`, verifies the final ERD structure, and runs the sample demonstration. Running a launcher again refreshes the database cleanly.

## Query the database

Windows:

```powershell
$python = "$env:LOCALAPPDATA\ByteForge\DBMS_Project\venv\Scripts\python.exe"
& $python -m schema.scripts.queries.query_database saved
& $python -m schema.scripts.queries.query_database saved rivers
& $python -m schema.scripts.queries.query_database describe Water_Quality
& $python -m schema.scripts.queries.query_database run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

Linux, WSL, or macOS:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -m schema.scripts.queries.query_database saved
"$PYTHON" -m schema.scripts.queries.query_database saved rivers
"$PYTHON" -m schema.scripts.queries.query_database describe Water_Quality
"$PYTHON" -m schema.scripts.queries.query_database run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

Every query command opens the database read-only. Saved examples cover table counts, relationships, time coverage, climate, rainfall, rivers, water quality, forests, wastewater, missing measurements, integrity, and foreign keys.

## Backup and restore

Backups and restores remain separate from setup.

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -m schema.scripts.maintenance.backup_database
"$PYTHON" -m schema.scripts.maintenance.restore_database schema/backups/environment_YYYYMMDD_HHMMSS.db --replace
```

Backups are written under `schema/backups/` and are not committed or copied during Drive publishing.

## Refresh normalization outputs

The selected source files remain in Google Drive. In the Drive project, the scripts find `Selected_Source_Files/` automatically. In another checkout, set `DBMS_SOURCE_DIR` to that folder.

Windows PowerShell:

```powershell
$python = "$env:LOCALAPPDATA\ByteForge\DBMS_Project\venv\Scripts\python.exe"
& $python normalization\scripts\extract.py
& $python normalization\scripts\exclusions.py
& $python normalization\scripts\workbook.py
& $python -m schema.scripts.setup.build_database --replace
& $python -m schema.scripts.setup.verify_database
```

Linux, WSL, or macOS:

```bash
export DBMS_SOURCE_DIR="/path/to/DBMS_Project/Selected_Source_Files"
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" normalization/scripts/extract.py
"$PYTHON" normalization/scripts/exclusions.py
"$PYTHON" normalization/scripts/workbook.py
"$PYTHON" -m schema.scripts.setup.build_database --replace
"$PYTHON" -m schema.scripts.setup.verify_database
```

The workbook is generated as `normalization/Environmental_Normalization_0NF_to_BCNF.xlsx`. The database importer reads all final BCNF CSV files and enforces the 21 tables and 27 relationships defined by the final ERD.

## Publish the verified files to Drive

Check for differences:

```bash
python3 tools/publish_to_drive.py --drive "/path/to/DBMS_Project"
```

Apply the checked update:

```bash
python3 tools/publish_to_drive.py --drive "/path/to/DBMS_Project" --apply
```

Publishing manages only `ERD`, `exclusions`, `normalization`, `schema`, the launchers, and `requirements.txt`. It never changes `report/` or `Selected_Source_Files/` and never copies Git metadata or this README to Drive.
