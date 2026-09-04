# Bangladesh Environmental Data Integration

ByteForge Scrum Group 07 normalised selected environmental records for
Bangladesh into BCNF relations and loaded them into a SQLite database. The
final ERD in `ERD/` is the authority for the database structure. The report is
written in LaTeX under `report/` and the database is reproducible from the
committed sources.

## Reviewer Quick Access

- **Final report (PDF):** [`Group-07_Environmental_DBMS_Final_Report.pdf`](
  https://drive.google.com/drive/folders/1SSdmo-VFQ6leS7Gp8hItmksg_SxRMl3q
  ) in the public source folder
- **Collected source files (public Drive folder):**
  [Selected_Source_Files](https://drive.google.com/drive/folders/1SSdmo-VFQ6leS7Gp8hItmksg_SxRMl3q)
- **Complete source register with original URLs:**
  [Team-7_BD_Environment_Data_Resources.xlsx](https://drive.google.com/file/d/1UB5vrVxfrtvFXZUDgvV4bsBDaMcvC2sw/view)
- **Final ERD:** [`ERD/Final_ERD.png`](ERD/Final_ERD.png)
- **SQLite database:** [`schema/environment.db`](schema/environment.db)
- **Normalization evidence:** [`normalization/`](normalization/)
- **Database verification:**
  [`schema/scripts/setup/verify_database.py`](schema/scripts/setup/verify_database.py)

Verify the delivered database (read-only; checks tables, relationships, views,
rows and the ERD contract):

```bash
python3 -B -m schema.scripts.setup.verify_database
```

## Project layout

- `ERD/Final_ERD.png` — final ERD used by the active database. Discarded
  designs are under `ERD/discarded_do_not_use/`.
- `normalization/` — generated workbook, normalization CSVs, statistics,
  data-quality log, exclusion evidence and its scripts.
- `schema/environment.db` — the ready-to-query SQLite database.
- `schema/sql/` — committed SQL: `schema.sql`, saved `queries.sql`, and
  `complete_data/`.
- `schema/scripts/` — Python tooling: `setup/` builds and verifies the
  database, `queries/` runs the saved queries, `competency/` regenerates the
  benchmark evidence, `maintenance/` backs up and restores, `tests/` holds the
  acceptance tests.
- `report/` — LaTeX report sources and build; compiled PDFs are not committed.
- `MySQL/` — a MariaDB/MySQL clone of the database with parity checks.
- `Selected_Source_Files/` and the source workbooks live on Google Drive, not
  in this repository.

The Git repository is the source of truth. Google Drive keeps a synced copy of
the project and the original collected files for the reviewers.

## Automatic setup

The launchers look for Python 3.10 or newer and use only its built-in SQLite
module. The private Python environment lives outside the project folder: on
Linux/macOS `~/.cache/byteforge-dbms`, on Windows
`%USERPROFILE%\.byteforge\dbms_project` (override with `BYTEFORGE_ENV`). Setup
asks before installing missing system or project packages and before replacing
an existing database.

Windows:

```bat
setup_windows.bat
```

Linux, WSL or macOS:

```bash
./setup_linux.sh
```

For an unattended run add `/yes` (Windows) or `--yes` (Linux/macOS). Add
`/replace` or `--replace` only when the existing database should be rebuilt.
Each launcher prepares `schema/environment.db`, verifies the ERD structure and
runs the sample demonstration.

## VS Code on WSL

Open the project folder through your WSL distribution. The workspace
recommends Code Runner, SQLTools, the SQLite driver and ShellCheck. To run a
`.sql` file without changing the database use **Terminal > Run Task >
ByteForge: Run current SQL file read-only**; to check the committed schema use
**ByteForge: Validate schema SQL**. Both tasks need the `sqlite3` command-line
tool. SQLTools provides a ready connection named `ByteForge SQLite`.

## Query the database

Windows PowerShell:

```powershell
$python = "$env:USERPROFILE\.byteforge\dbms_project\venv\Scripts\python.exe"
& $python -B -m schema.scripts.queries.query_database saved
& $python -B -m schema.scripts.queries.query_database saved rivers
& $python -B -m schema.scripts.queries.query_database describe Water_Quality
& $python -B -m schema.scripts.queries.query_database run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

Linux, WSL or macOS:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.queries.query_database saved
"$PYTHON" -B -m schema.scripts.queries.query_database saved rivers
"$PYTHON" -B -m schema.scripts.queries.query_database describe Water_Quality
"$PYTHON" -B -m schema.scripts.queries.query_database run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

Every query runs read-only. Saved examples cover counts, relationships, time
coverage, climate, rainfall, rivers, water quality, forests, wastewater,
missing measurements, integrity and foreign keys.

Refresh the competency benchmark evidence only after an intentional change:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.competency.benchmark_database
```

The result is written to `schema/scripts/competency/benchmark.json`.

## Backup and restore

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.maintenance.backup_database
"$PYTHON" -B -m schema.scripts.maintenance.restore_database schema/backups/environment_YYYYMMDD_HHMMSS.db --replace
```

Backups land under `schema/backups/` and are not committed.

## Refresh normalization outputs

The original source files stay on Google Drive under `Selected_Source_Files/`;
the scripts find them automatically when run inside the Drive project folder.
In any other checkout set `DBMS_SOURCE_DIR` to that folder.

Windows PowerShell:

```powershell
$python = "$env:USERPROFILE\.byteforge\dbms_project\venv\Scripts\python.exe"
& $python -B normalization\scripts\extract.py
& $python -B normalization\scripts\exclusions.py
& $python -B normalization\scripts\workbook.py
& $python -B -m schema.scripts.setup.build_database --replace
& $python -B -m schema.scripts.setup.verify_database
```

Linux, WSL or macOS:

```bash
export DBMS_SOURCE_DIR="/path/to/DBMS_Project/Selected_Source_Files"
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B normalization/scripts/extract.py
"$PYTHON" -B normalization/scripts/exclusions.py
"$PYTHON" -B normalization/scripts/workbook.py
"$PYTHON" -B -m schema.scripts.setup.build_database --replace
"$PYTHON" -B -m schema.scripts.setup.verify_database
```

The workbook is generated as
`normalization/Environmental_Normalization_0NF_to_BCNF.xlsx`. Review decisions
are recorded in `normalization/DATA_REVIEW.md` with supporting files under
`normalization/review/`. The importer reads the final BCNF CSVs and enforces
the 21 tables and 28 relationships of the final ERD.
