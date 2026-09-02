# Bangladesh Environmental Data Integration

ByteForge Scrum Group 07 normalized the selected environmental records and loaded the final BCNF relations into SQLite. The final ERD in `ERD/` is the authority for the database structure.

## Project layout

- `ERD/Final_ERD.png` is the report ERD used by the active database. Old diagrams are isolated in `ERD/discarded_do_not_use/`.
- `normalization/` contains the generated workbook, normalization CSVs, statistics, data-quality log, exclusion evidence, and its `scripts/` folder.
- `schema/environment.db` is the ready-to-query SQLite database.
- `schema/scripts/setup/` builds and verifies the database.
- `schema/scripts/queries/` contains the read-only query tool, saved SQL, and demonstration.
- `schema/validation/competency/` preserves the machine-readable competency benchmark evidence.
- `schema/scripts/maintenance/` contains backup, restore, and Drive-publishing tools.
- `schema/tests/` contains the database, ERD, setup, and competency acceptance tests.

The WSL checkout is the coding source of truth and the only Git repository. Google Drive is a non-Git project mirror containing the selected sources and the report workspace.

## Automatic setup

The launchers look for Python 3.10 or newer and confirm that its built-in SQLite support works. If Python, venv, pip, or the pinned project packages are missing, setup explains what it needs and asks before installing system or project packages. The private Python environment stays outside the project folder, under `~/.cache/byteforge-dbms` on Linux/macOS or `%USERPROFILE%\.byteforge\dbms_project` on Windows. Setting the `BYTEFORGE_ENV` environment variable moves it; every command example below assumes the default location. The pipeline needs only Python's built-in SQLite module — no separate SQLite installation is required. On Linux, when the `sqlite3` command-line tool is missing, setup also asks whether to install it, because the VS Code tasks that run `.sql` files directly use that tool.

Windows:

```bat
setup_windows.bat
```

Linux, WSL, or macOS:

```bash
./setup_linux.sh
```

For an unattended installation, use `setup_windows.bat /yes` or `./setup_linux.sh --yes`. Add `/replace` on Windows or `--replace` on Linux only when the existing database should be replaced. Linux supports apt, dnf, microdnf, yum, pacman, zypper, and apk; Homebrew is also recognized on macOS. System package installation may ask for the computer's administrator password. Declining an installation stops setup without rebuilding the database.

Each launcher creates a private environment outside the project folder, installs the pinned packages, prepares `schema/environment.db`, verifies the final ERD structure, and runs the sample demonstration. A current database is kept on later runs. A different database asks before replacement unless the explicit replacement option is used.

## VS Code on WSL

Open the GitHub project folder through **WSL: Fedora**. The workspace recommends and configures Code Runner, SQLTools, the SQLite driver, and ShellCheck. The **Run Code** button executes `.sh` files with Bash. To run SQL without changing the database, use **Terminal > Run Task > ByteForge: Run current SQL file read-only** (runs the active `.sql` file against `schema/environment.db`) or **ByteForge: Validate schema SQL** (checks `schema.sql` in an in-memory database); both tasks need the `sqlite3` command-line tool. SQLTools includes a ready connection named `ByteForge SQLite`.

## Query the database

Windows:

```powershell
$python = "$env:USERPROFILE\.byteforge\dbms_project\venv\Scripts\python.exe"
& $python -B -m schema.scripts.queries.query_database saved
& $python -B -m schema.scripts.queries.query_database saved rivers
& $python -B -m schema.scripts.queries.query_database describe Water_Quality
& $python -B -m schema.scripts.queries.query_database run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

Linux, WSL, or macOS:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.queries.query_database saved
"$PYTHON" -B -m schema.scripts.queries.query_database saved rivers
"$PYTHON" -B -m schema.scripts.queries.query_database describe Water_Quality
"$PYTHON" -B -m schema.scripts.queries.query_database run "SELECT COUNT(*) AS Records FROM Water_Quality"
```

Every query command opens the database read-only. Saved examples cover table counts, relationships, time coverage, climate, rainfall, rivers, water quality, forests, wastewater, missing measurements, integrity, and foreign keys.

Refresh the canonical competency evidence after an intentional database or query change:

Linux, WSL, or macOS:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.queries.benchmark_database
```

Windows PowerShell:

```powershell
$python = "$env:USERPROFILE\.byteforge\dbms_project\venv\Scripts\python.exe"
& $python -B -m schema.scripts.queries.benchmark_database
```

The benchmark is written to `schema/validation/competency/benchmark.json` by default.

## Backup and restore

Backups and restores remain separate from setup.

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B -m schema.scripts.maintenance.backup_database
"$PYTHON" -B -m schema.scripts.maintenance.restore_database schema/backups/environment_YYYYMMDD_HHMMSS.db --replace
```

Backups are written under `schema/backups/` and are not committed or copied during Drive publishing.

## Refresh normalization outputs

The selected source files remain in Google Drive. In the Drive project, the scripts find `Selected_Source_Files/` automatically. In another checkout, set `DBMS_SOURCE_DIR` to that folder.

Windows PowerShell:

```powershell
$python = "$env:USERPROFILE\.byteforge\dbms_project\venv\Scripts\python.exe"
& $python -B normalization\scripts\extract.py
& $python -B normalization\scripts\exclusions.py
& $python -B normalization\scripts\workbook.py
& $python -B -m schema.scripts.setup.build_database --replace
& $python -B -m schema.scripts.setup.verify_database
```

Linux, WSL, or macOS:

```bash
export DBMS_SOURCE_DIR="/path/to/DBMS_Project/Selected_Source_Files"
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B normalization/scripts/extract.py
"$PYTHON" -B normalization/scripts/exclusions.py
"$PYTHON" -B normalization/scripts/workbook.py
"$PYTHON" -B -m schema.scripts.setup.build_database --replace
"$PYTHON" -B -m schema.scripts.setup.verify_database
```

The workbook is generated as `normalization/Environmental_Normalization_0NF_to_BCNF.xlsx`. Human review decisions are summarized in `normalization/DATA_REVIEW.md`, with supporting CSV files in `normalization/review/`. The database importer reads all final BCNF CSV files and enforces the 21 tables and 28 relationships defined by the final ERD.

## Publish the verified files to Drive

Check for differences:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B schema/scripts/maintenance/publish_to_drive.py --drive "/path/to/Drive/DBMS_Project"
```

Apply the checked update:

```bash
PYTHON="${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv/bin/python"
"$PYTHON" -B schema/scripts/maintenance/publish_to_drive.py --drive "/path/to/Drive/DBMS_Project" --apply
```

Publishing manages only `ERD`, `normalization`, `schema`, the launchers, and `requirements.txt`; it also removes the retired root-level `exclusions/` copy from an older Drive mirror. It never changes `report/` or `Selected_Source_Files/` and never copies Git metadata or this README to Drive.
