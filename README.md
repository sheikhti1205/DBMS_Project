# Bangladesh Environmental Data Integration

ByteForge Scrum Group 07 normalised selected environmental records for
Bangladesh into BCNF relations and loaded them into a SQLite database. The
implemented schema follows `ERD/Final_ERD.png`; the report is written in
LaTeX under `report/`. The database is reproducible from the
retained sources together with the committed extraction, normalization and
schema code.

## Reviewer Quick Access

- **Final report (PDF):** [Group-07_Environmental_DBMS_Final_Report.pdf](https://drive.google.com/file/d/1KjoO2aXPX3MEvbx64_3Viq4KVtmV7cKm/view?usp=sharing)
- **Collected source files (public Drive folder):** [Selected_Source_Files](https://drive.google.com/drive/folders/1SSdmo-VFQ6leS7Gp8hItmksg_SxRMl3q)
- **Complete source register with original URLs:** [Team-7_BD_Environment_Data_Resources.xlsx](https://drive.google.com/file/d/1UB5vrVxfrtvFXZUDgvV4bsBDaMcvC2sw/view)
- **Final ERD:** [`ERD/Final_ERD.png`](ERD/Final_ERD.png)
- **SQLite database:** [`schema/environment.db`](schema/environment.db)
- **Normalization evidence:** [`normalization/`](normalization/)
- **Database verification:** [`schema/scripts/setup/verify_database.py`](schema/scripts/setup/verify_database.py)

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
commands: [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md). The
[BMD comparison](normalization/BMD_DERIVATIVE.md) documents the PDF-to-workbook
verification boundary.

## Verify the database (read-only)

Checks tables, relationships, views, rows and the schema definition file:

```bash
python3 -B -m schema.scripts.setup.verify_database
```

## Automatic setup

The launchers need Python 3.10+ and keep a private environment outside the
project folder. Each prepares `schema/environment.db`, verifies it and runs
the read-only saved `table-counts` query, asking before installing missing
packages or replacing an existing database.

Windows:

```bat
setup_windows.bat
```

Linux, WSL or macOS:

```bash
./setup_linux.sh
```

Add `/yes` or `--yes` for an unattended run; add `/replace` or `--replace`
only to rebuild the existing database.

## Developer documentation

Querying per OS, VS Code on WSL, backup/restore, and refreshing the
normalization or competency-benchmark outputs are in
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).
