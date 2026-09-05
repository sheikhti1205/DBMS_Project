# Bangladesh Environmental Data Integration Model

A relational database project for collecting, cleaning, normalizing, and
integrating environmental data about Bangladesh into a single relational
database. Built by ByteForge Scrum Group 07 for the Database Systems Lab
course at the Department of Computer Science and Engineering, University of
Chittagong.

The finished database is committed to this repository as
[`schema/environment.db`](schema/environment.db) (SQLite, with a
MySQL/MariaDB clone under `MySQL/`). It is ready to query immediately — you do
not need the original sources or a build step to use it. Setup is only needed
to create a working Python environment and to confirm the database on your
machine.

## Quick Access

- **Final report (PDF):** [Group-07_Environmental_DBMS_Final_Report.pdf](https://drive.google.com/file/d/1KjoO2aXPX3MEvbx64_3Viq4KVtmV7cKm/view?usp=sharing)
- **Collected source files (public Drive folder):** [Selected_Source_Files](https://drive.google.com/drive/folders/1SSdmo-VFQ6leS7Gp8hItmksg_SxRMl3q)
- **Complete source register with original URLs:** [Team-7_BD_Environment_Data_Resources.xlsx](https://drive.google.com/file/d/1UB5vrVxfrtvFXZUDgvV4bsBDaMcvC2sw/view)
- **Final ERD:** [`ERD/Final_ERD.png`](ERD/Final_ERD.png)
- **SQLite database:** [`schema/environment.db`](schema/environment.db)
- **MySQL / MariaDB setup:** [`MySQL/README.md`](MySQL/README.md)
- **Database verification:** [`schema/scripts/setup/verify_database.py`](schema/scripts/setup/verify_database.py)

## Repository map

| Path | What it is |
|---|---|
| `ERD/` | Final entity-relationship diagram; the authority for the database structure. |
| `schema/sql/` | `schema.sql` (the final schema), `queries.sql` (saved read-only queries), `complete_data/` (bulk inserts). |
| `schema/scripts/` | Python tooling: database build/verify, the saved-query runner, maintenance, and tests. |
| `normalization/` | 0NF-to-BCNF workbook and CSVs; `STATISTICS.md` (load statistics), `DATA_REVIEW.md` (data-cleaning decisions), `BMD_DERIVATIVE.md` (BMD PDF/workbook check), `exclusions/` (excluded items). |
| `MySQL/` | MySQL/MariaDB clone of the database; `README.md` is its setup guide. |
| `report/` | LaTeX report sources; the compiled PDF is linked above. |
| `docs/` | `SETUP.md` (step-by-step setup) and `DEVELOPMENT.md` (querying, VS Code on WSL, backup/restore, refresh steps). |
| `setup_linux.sh`, `setup_windows.bat` | The setup launchers described in [Setup guide](#setup-guide). |
| `requirements.txt` | The Python packages the launchers install. |

## Verified facts

`schema/environment.db` has 21 tables, 2 query views, 730,324 rows and
28 foreign-key relationships. Integrity checks pass with zero foreign-key
violations. The views are query conveniences, not ERD entities.

## Source to SQLite pipeline

The database that ships in this repository is already built and verified. The
steps below describe how it is reproduced from the original sources — you only
need them if you want to rebuild from scratch.

1. **Source** — the original files are collected and kept in the public Drive
   folder `Selected_Source_Files/`, not in this repository. Retained PDFs are
   evidence.
2. **Extraction and normalization** — `normalization/scripts/extract.py`
   reads the processing workbooks and CSV, applies the documented cleaning
   rules, and writes the 0NF-to-BCNF CSVs and quality evidence.
3. **Review outputs** — `exclusions.py` documents excluded data; `workbook.py`
   packages the normalization stages into an Excel workbook.
4. **SQLite** — `schema/scripts/setup/build_database.py` loads the final BCNF
   CSVs into `schema/environment.db`.

Regeneration needs the retained sources plus the project-formatted BMD
workbook (`Temperature Data.xlsx`; BMD = Bangladesh Meteorological
Department); retained PDFs are not automatically converted. Outside the Drive
project folder, point the scripts at the sources with `DBMS_SOURCE_DIR`. Full
commands are in [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## Setup guide

Setup prepares a private Python environment and confirms the database builds
and verifies on your machine. It does not install anything globally without
asking first.

The two launcher scripts do exactly the same job — one per operating system.
Open a terminal **in the folder where you cloned this repository** and run the
matching command:

Windows (Command Prompt or PowerShell):

```bat
setup_windows.bat
```

Linux, WSL or macOS:

```bash
./setup_linux.sh
```

During the run the launcher:

1. Finds a Python 3.10+ interpreter (it offers to install one if missing, and
   stops if you decline).
2. Creates an isolated virtual environment in a folder outside the project —
   your system Python is not modified.
3. Installs the pinned packages from `requirements.txt` into that environment.
4. Prepares `schema/environment.db` (an existing database is left untouched).
5. Checks the database read-only against the final ERD.
6. Prints the saved read-only `table-counts` query as a finishing touch, so
   the last lines of output are record counts ending with a `TOTAL` row.

The run ends with `ByteForge is ready.` You can now follow
[Run and query](#run-and-query). Options:

- `/yes` (Windows) or `--yes` (Linux/macOS) — auto-approve every prompt.
  Needed when the terminal cannot ask questions (for example in CI).
- `/replace` or `--replace` — rebuild the database even if one already
  exists. Leave it out unless you intend to rebuild.

A step-by-step walkthrough with expected output, Windows/Linux details, and
troubleshooting is in [`docs/SETUP.md`](docs/SETUP.md).

## Run and query

Run these from the repository root. They need only a Python 3.10+ interpreter
and open the database **read-only** (nothing is ever written by these
commands). No setup environment activation is required.

Check that the delivered database matches the final ERD and its schema
definition file (`schema/sql/schema.sql`) — tables, relationships, views,
rows:

```bash
python3 -B -m schema.scripts.setup.verify_database
```

On Windows replace `python3` with `python` above. `-B` simply stops Python
from writing bytecode-cache files. Success looks like:

```
Database check passed.
Checked 21 tables, 28 relationships, 2 views, and 730,324 rows.
```

The saved queries live in
[`schema/sql/queries.sql`](schema/sql/queries.sql). List them, then run one by
name:

```bash
python3 -B -m schema.scripts.queries.query_database saved
python3 -B -m schema.scripts.queries.query_database saved table-counts
```

The second command above is the same read-only query the setup launchers
print. Other examples (with names such as `rivers`, `rainfall-ranking`,
`water-quality-summary`) are documented in
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

For a MySQL/MariaDB deployment instead of SQLite, follow
[`MySQL/README.md`](MySQL/README.md); the SQLite route above is the default.

## Documentation

The problem statement, objectives, data pipeline and normalization
methodology, schema design, example queries and conclusion are documented in
the [final report](https://drive.google.com/file/d/1KjoO2aXPX3MEvbx64_3Viq4KVtmV7cKm/view?usp=sharing).
Everything else is kept close to the artifacts it describes:

- `docs/SETUP.md` — step-by-step install and rebuild guide for each OS.
- `docs/DEVELOPMENT.md` — query recipes per OS, VS Code on WSL, backup and
  restore, and refreshing the normalization and benchmark outputs.
- `normalization/STATISTICS.md` — how much each source contributes.
- `normalization/DATA_REVIEW.md` — decisions that change which values load.
- `normalization/BMD_DERIVATIVE.md` — PDF-to-workbook verification boundary.
- `normalization/exclusions/` — every excluded item, with its reason.
