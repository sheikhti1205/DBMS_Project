# Setup guide

This page explains how to install and run the ByteForge DBMS project on a
fresh machine, step by step. The [`README.md`](../README.md) has the quick
version; read this page when you want the details behind the launcher
scripts, what each step does, what output to expect, and what to do when
something goes wrong.

*ByteForge* is the Scrum group that built the project (ByteForge Scrum Group
07). The launchers print `ByteForge is ready.` when setup succeeds.

## Before you start

- You have the repository on your machine (for example a `git clone`) and a
  terminal open **in the repository root** — the folder that contains
  `README.md`, `setup_linux.sh` and `setup_windows.bat`. All commands on this
  page assume that location.
- **Internet access is needed on the first run** so the launcher can download
  packages (and, if missing, a Python interpreter).
- The launcher needs **administrator or `sudo` rights only** when it installs
  a system package, and only after you approve the prompt.

You do not need to install Python yourself: if none is found, the launcher
offers to install it. You also do not need the original Google Drive sources —
the database and the processed data are already in the repository.

## What the launchers do

There are two identical launchers because the setup steps differ between
Windows and Unix systems: `setup_windows.bat` runs in a Windows Command
Prompt or PowerShell, and `setup_linux.sh` runs in a Linux, WSL or macOS
terminal. Both perform the same six steps:

1. **Find Python.** A Python 3.10 (or newer) interpreter with SQLite support
   is located. If none exists, the launcher asks for permission to install
   one and stops if you decline.
2. **Create a virtual environment.** A *virtual environment* is an isolated
   Python installation in its own folder. The launcher creates one outside
   the project folder so installing packages here never changes your system
   Python. See [Where the environment lives](#where-the-environment-lives).
3. **Install project packages.** The packages pinned in
   [`requirements.txt`](../requirements.txt) (`openpyxl` and `xlrd`, both
   used to read Excel workbooks during builds) are installed into that
   environment at their exact versions. The launcher asks before installing.
4. **Prepare the database.** The SQLite database
   [`schema/environment.db`](../schema/environment.db) is built from the
   committed schema and processed data. If a valid database already exists it
   is left alone; pass the replace flag to rebuild it (see
   [Flags](#flags-and-unattended-runs)).
5. **Verify the database.** The database is checked read-only against the
   final ERD (tables, relationships, views, rows and the schema file).
6. **Print a sample query.** The launcher runs the saved read-only
   `table-counts` query so you can see real output immediately.

The final lines of a successful run look approximately like this:

```text
Running the saved read-only table-counts query.
Table_Name              Records
...
TOTAL                   730324

ByteForge is ready.
```

(The `TOTAL` row is the sum of the per-table counts. Python prints it as
`730324` without a thousands separator — that is the same 730,324 rows the
verifier reports.)

## Linux, WSL or macOS

```bash
./setup_linux.sh
```

If you get `Permission denied`, the script is not executable; fix it with
`chmod +x setup_linux.sh` and run it again.

What you will see:

- If Python or the `sqlite3` command-line tool is missing, the launcher names
  the packages it wants to install and asks `[y/N]`. Answer `y` to install or
  `N` to skip that part (skipping the `sqlite3` tool is fine — it is only
  needed for the optional VS Code SQL tasks, not for Python queries).
- Package installs may prompt for your password through `sudo`.
- A successful run ends with `ByteForge is ready.`

### Flags and unattended runs

| Flag | Meaning |
|---|---|
| `--yes` | Approve every installation prompt automatically. Use this when the terminal cannot ask questions, for example a CI pipeline or a scripted run. |
| `--replace` | Rebuild `schema/environment.db` even if one already exists. Only use it when you intend to rebuild. |

The two flags do different things and can be combined: `./setup_linux.sh
--yes --replace` approves all prompts and rebuilds the database in one
unattended run.

### Where the environment lives

The virtual environment is created at
`${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv`. In plain terms that is
`~/.cache/byteforge-dbms/venv` on most machines. To place it somewhere else,
set the `BYTEFORGE_ENV` variable before running:

```bash
BYTEFORGE_ENV=/path/to/your/venv ./setup_linux.sh --yes
```

## Windows

Open a Command Prompt or PowerShell window in the repository folder and run:

```bat
setup_windows.bat
```

What you will see:

- If Python is missing, the launcher offers to install Python 3.12 for the
  current user (first with `winget`, then with the signed installer from
  python.org). The installer runs silently; no system-wide changes are made.
- Package installation may take a minute on the first run.
- A successful run ends with `ByteForge is ready.`

### Flags and unattended runs

Windows uses `/` instead of `--` for flags:

| Flag | Meaning |
|---|---|
| `/yes` | Approve every installation prompt automatically (for CI or scripted runs). |
| `/replace` | Rebuild `schema/environment.db` even if one already exists. |

They combine the same way: `setup_windows.bat /yes /replace`.

### Where the environment lives

The virtual environment is created at
`%USERPROFILE%\.byteforge\dbms_project\venv`. To place it elsewhere, set the
`BYTEFORGE_ENV` environment variable before running the script.

## After setup

You can now query the database. See the "Run and query" section of the
[`README.md`](../README.md), or [`DEVELOPMENT.md`](DEVELOPMENT.md) for the
full query recipes per operating system. To use the MySQL/MariaDB clone
instead of SQLite, follow [`MySQL/README.md`](../MySQL/README.md).

A quick check that everything works, run from the repository root:

```bash
python3 -B -m schema.scripts.setup.verify_database
```

On Windows use `python` instead of `python3`:

```powershell
python -B -m schema.scripts.setup.verify_database
```

These check commands need only a Python 3.10+ interpreter with its standard
library — they do **not** require activating the virtual environment or the
`openpyxl`/`xlrd` packages. Success prints:

```text
Database check passed.
Checked 21 tables, 28 relationships, 2 views, and 730,324 rows.
```

If instead you prefer to use the launcher's own interpreter for consistency,
call it by its full path: on Linux/macOS
`~/.cache/byteforge-dbms/venv/bin/python`, on Windows
`%USERPROFILE%\.byteforge\dbms_project\venv\Scripts\python.exe` (or wherever
`BYTEFORGE_ENV` points).

## Rebuilding the database

`/replace` / `--replace` rebuilds `schema/environment.db` from the committed
schema and processed data. Refreshing the normalization outputs from the
original sources (which live in the public Drive `Selected_Source_Files`
folder) is a separate step — see
[`DEVELOPMENT.md`](DEVELOPMENT.md#refresh-normalization-outputs).

## Troubleshooting

| Symptom | What it means and what to do |
|---|---|
| `Permission denied` when running `./setup_linux.sh` | The script is not executable. Run `chmod +x setup_linux.sh`, then try again. |
| "Setup cannot ask for approval in this terminal." | The launcher needs interactive prompts. Run it in a real terminal, or add `/yes` (Windows) / `--yes` (Linux/macOS) to approve everything automatically. |
| You decline an installation prompt | Setup stops immediately without changing anything on your system. Re-run and approve the parts you want. |
| "The private environment could not be created." / "The Python environment could not be created." | The system Python could not create a virtual environment. Check that `python3 -m venv` works, or install a newer Python and re-run. |
| The environment was created in an unexpected folder | `BYTEFORGE_ENV` (or `XDG_CACHE_HOME`) is set to a non-standard location. Point it at a normal user folder and re-run. |
| "Required Python packages could not be installed." | Usually a network problem. Check the connection and re-run; existing files are not damaged. |
| The `sqlite3` command-line tool is missing | Only the optional VS Code SQL tasks use it. The Python-based queries and checks work without it. Let the launcher install it or install it via your package manager. |
| You see "Required project packages are already available." | Not an error — the pinned packages are already installed at the right versions, so the launcher skipped that step. |
| You are unsure whether setup worked | The last lines should show record counts ending in a `TOTAL` row followed by `ByteForge is ready.` |
