# Development notes

Developer-oriented instructions for the ByteForge DBMS project. Reviewer-facing
material, verified facts and setup commands live in the
[`README.md`](../README.md).

The launchers (`setup_windows.bat`, `setup_linux.sh`) look for Python 3.10 or
newer and build a private environment outside the project folder: on
Linux/macOS `~/.cache/byteforge-dbms`, on Windows
`%USERPROFILE%\.byteforge\dbms_project` (override with `BYTEFORGE_ENV`). All
queries below use that environment and run read-only against
[`schema/environment.db`](../schema/environment.db).

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

Every query opens the database in `mode=ro`; nothing is written. The saved
examples in [`schema/sql/queries.sql`](../schema/sql/queries.sql) cover table
counts, relationships, time coverage, climate, rainfall, rivers, water
quality, forests, wastewater, missing measurements, integrity and foreign
keys. `saved table-counts` is what the setup launchers print after setup.

## VS Code on WSL

Open the project folder through your WSL distribution. The workspace
recommends Code Runner, SQLTools, the SQLite driver and ShellCheck. To run a
`.sql` file without changing the database use **Terminal > Run Task >
ByteForge: Run current SQL file read-only**; to check the committed schema use
**ByteForge: Validate schema SQL**. Both tasks need the `sqlite3` command-line
tool. SQLTools provides a ready connection named `ByteForge SQLite`.

## Backup and restore

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.maintenance.backup_database
"$PYTHON" -B -m schema.scripts.maintenance.restore_database schema/backups/environment_YYYYMMDD_HHMMSS.db --replace
```

Backups land under [`schema/backups/`](../schema/backups/) and are not
committed. The maintenance modules are
[`schema/scripts/maintenance/`](../schema/scripts/maintenance/).

## Refresh normalization outputs

The original source files stay on Google Drive under the public
`Selected_Source_Files` folder; the scripts find them automatically when run
inside that Drive project folder. In any other checkout set `DBMS_SOURCE_DIR`
to the folder containing the retained sources.

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
[`normalization/Environmental_Normalization_0NF_to_BCNF.xlsx`](../normalization/Environmental_Normalization_0NF_to_BCNF.xlsx).
Review decisions are recorded in
[`normalization/DATA_REVIEW.md`](../normalization/DATA_REVIEW.md) with
supporting files under [`normalization/review/`](../normalization/review/).
The importer reads the final BCNF CSVs and enforces the 21 tables and 28
relationships of the final ERD. Retained PDF publications are evidence; they
are not automatically converted. For BMD temperature, use the retained
`Temperature Data.xlsx` derivative. Its original conversion method was not
recorded; the [comparison check](../normalization/BMD_DERIVATIVE.md) documents
representative values checked against the PDF.

## Refresh the competency benchmark evidence

Refresh only after an intentional change to the database:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.competency.benchmark_database
```

The result is written to
[`schema/scripts/competency/benchmark.json`](../schema/scripts/competency/benchmark.json).

## Rebuild the report

From `report/`, run `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
This requires LaTeX and latexmk. The local output is `report/main.pdf`.

To refresh the retained-file access dates, run these from the repository root:

```bash
python3 -B report/scripts/check_source_links.py
python3 -B report/scripts/gen_register.py
```

Review failures before rebuilding. These checks use anonymous Drive previews,
match filenames, and record UTC timestamps; the printed dates use UTC+6.
They do not establish access to the original publisher websites or validate
all file contents. The BMD derivative has its own access check.
