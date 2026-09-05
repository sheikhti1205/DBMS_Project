# Setup guide

How to install and run the ByteForge DBMS project on a clean checkout. The
[`README.md`](../README.md) carries the short version; this page is the
detailed reference for `setup_windows.bat` and `setup_linux.sh`.

## What setup does

Both launchers run the same steps in order:

1. Locate a usable Python (3.10 or newer). If none exists, they offer to
   install one and stop if the install is not approved.
2. Create a private virtual environment outside the project folder and make
   sure `pip` is available inside it.
3. Install the project packages listed in [`requirements.txt`](../requirements.txt)
   at their pinned versions, asking before installing.
4. Prepare the database at [`schema/environment.db`](../schema/environment.db).
5. Verify the database read-only.
6. Print the saved `table-counts` query and exit with "ByteForge is ready."

The launchers only touch the system Python installation when you approve the
prompt. Re-running them is safe: an existing, valid database is left alone
unless you pass the replace flag.

## Prerequisites

- Windows 10/11, or Linux / WSL / macOS.
- An internet connection on the first run.
- Administrator or `sudo` rights are needed only when a system package must be
  installed, and only after you approve the prompt.

## Linux, WSL or macOS

```bash
./setup_linux.sh
```

Options:

- `--yes` — approve required installations without prompting. This is also
  required when setup runs in a non-interactive terminal.
- `--replace` — rebuild the existing database.

The private environment is created at
`${XDG_CACHE_HOME:-$HOME/.cache}/byteforge-dbms/venv`. To place it elsewhere,
set `BYTEFORGE_ENV`:

```bash
BYTEFORGE_ENV=/path/to/venv ./setup_linux.sh --yes
```

If Python is missing, the launcher installs it through the distribution
package manager (`apt`, `dnf`, `pacman`, `brew`, etc.). It also offers to
install the `sqlite3` command-line tool, which is only needed to run `.sql`
files directly (for example the VS Code tasks).

## Windows

```bat
setup_windows.bat
```

Options:

- `/yes` — approve required installations without prompting.
- `/replace` — rebuild the existing database.

If no usable Python is found, the launcher offers to install Python 3.12 for
the current user, first with `winget` and then with the signed python.org
installer. The private environment is created at
`%USERPROFILE%\.byteforge\dbms_project\venv`; override it with the
`BYTEFORGE_ENV` environment variable.

## After setup

The launcher prints the saved read-only `table-counts` query and reports that
ByteForge is ready. From here you can:

- Browse or run saved queries against the database — see "Run and query" in
  the [`README.md`](../README.md).
- Use the MySQL/MariaDB clone instead of SQLite — follow
  [`MySQL/README.md`](../MySQL/README.md).
- Query on each OS, work in VS Code on WSL, back up or restore the database,
  or refresh outputs — see [`DEVELOPMENT.md`](DEVELOPMENT.md).

## Verifying manually

The read-only verifier checks tables, relationships, views, rows and the
schema definition file:

```bash
python3 -B -m schema.scripts.setup.verify_database
```

## Rebuilding the database

Pass `/replace` (Windows) or `--replace` (Linux/macOS) only when the existing
database should be rebuilt. Refreshing the normalization outputs from the
original sources (which live in the public Drive `Selected_Source_Files`
folder) is a separate step documented in [`DEVELOPMENT.md`](DEVELOPMENT.md).

## Troubleshooting

- **"Setup cannot ask for approval in this terminal."** Run the launcher
  interactively or add `/yes` / `--yes`.
- **A confirmation prompt is declined.** Setup stops before changing anything
  on the system.
- **The private environment was created somewhere unexpected.** Set
  `BYTEFORGE_ENV` to a normal user folder and run setup again.
- **The `sqlite3` command-line tool is missing.** Only the VS Code SQL tasks
  need it; the Python queries still work. Let the launcher install it or
  install it through your package manager.
- **"Required project packages are already available."** Setup skipped the
  package install because every package in `requirements.txt` is already at
  its pinned version in the private environment.
