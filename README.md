# Bangladesh Environmental Data Integration Model

A relational database project for collecting, organizing, and integrating
environmental data about Bangladesh. It turns data scattered across different
organisations and file formats into a single structured, BCNF-normalized
relational database (SQLite, with a MySQL/MariaDB clone). Developed for the
Database Systems Lab course at the Department of Computer Science and
Engineering, University of Chittagong.

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
| `ERD/` | Final entity-relationship diagram; authority for the database structure. |
| `schema/sql/` | `schema.sql` (final schema), `queries.sql` (saved read-only queries), `complete_data/` (bulk inserts). |
| `schema/scripts/` | Python tooling: database build/verify, saved-query runner, competency benchmark, maintenance, tests. |
| `normalization/` | 0NF-to-BCNF workbook and CSVs; `STATISTICS.md` (load statistics), `DATA_REVIEW.md` (data-cleaning decisions), `BMD_DERIVATIVE.md` (BMD PDF/workbook check), `exclusions/` (excluded items). |
| `MySQL/` | MySQL/MariaDB clone of the database; `README.md` is its setup guide. |
| `report/` | LaTeX report sources; the compiled PDF is linked above. |
| `docs/` | `SETUP.md` (step-by-step setup for each OS) and `DEVELOPMENT.md` (queries, VS Code on WSL, backup/restore, refresh steps). |

## Verified facts

`schema/environment.db` has 21 tables, 2 query views, 730,324 rows and
28 foreign-key relationships. Integrity checks pass with zero foreign-key
violations. The views are query conveniences, not ERD entities.

## Source to SQLite pipeline

1. **Source** — originals stay in the public Drive folder
   `Selected_Source_Files/`, not in this repository; retained PDFs are
   evidence.
2. **Extraction and normalization** — `normalization/scripts/extract.py`
   reads the processing workbooks and CSV, applies the documented cleaning
   rules, and writes the 0NF-to-BCNF CSVs and quality evidence.
3. **Review outputs** — `exclusions.py` documents excluded data;
   `workbook.py` packages the normalization stages into an Excel workbook.
4. **SQLite** — `schema/scripts/setup/build_database.py` loads the final
   BCNF CSVs into `schema/environment.db`.

Regeneration needs the retained sources plus the project-formatted BMD
workbook (`Temperature Data.xlsx`); retained PDFs are not automatically
converted. Outside the Drive project folder set `DBMS_SOURCE_DIR`. Full
commands are in [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## Setup guide

The launchers need Python 3.10+, keep a private environment outside the
project folder, prepare `schema/environment.db`, verify it and print the saved
read-only `table-counts` query.

Windows:

```bat
setup_windows.bat
```

Linux, WSL or macOS:

```bash
./setup_linux.sh
```

Add `/yes` (Windows) or `--yes` (Linux/macOS) for an unattended run; add
`/replace` or `--replace` only to rebuild an existing database. A detailed,
step-by-step guide for each OS is in [`docs/SETUP.md`](docs/SETUP.md).

## Run and query

Verify the delivered database read-only (tables, relationships, views, rows
and the schema definition):

```bash
python3 -B -m schema.scripts.setup.verify_database
```

Saved queries live in [`schema/sql/queries.sql`](schema/sql/queries.sql) and
run read-only against the database with:

```bash
python3 -B -m schema.scripts.queries.query_database saved
```

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
