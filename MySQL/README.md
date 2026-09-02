# MySQL / MariaDB clone of the environment database

A MySQL-compatible snapshot of the ByteForge Group 07 environment database that
lives as `schema/environment.db` (SQLite) at the project root. The clone keeps
the exact BCNF structure: 21 tables, 28 relationships, 2 views, and all
730,324 rows of data.

Requires **MariaDB 10.2 or newer, or MySQL 8.0 or newer** (the summary views
use a `WITH` clause, and `CHECK` constraints are only enforced from
MariaDB 10.2.1 / MySQL 8.0.16). It was developed and verified on MariaDB
11.8.6.

## Files

- `environment.sql` — self-contained MySQL/MariaDB dump snapshot:
  creates the `environment` database, its schema (tables, primary keys,
  foreign keys, check constraints, the two summary views), and loads all data.

## Restore / load

The dump is idempotent: it drops and recreates the known tables and views, then
reloads the data. Re-running it after an interruption is safe. Loading ~730k
rows takes under a minute on a normal machine.

Run the restore command **from inside this `MySQL/` directory**:

```bash
cd MySQL
sudo mysql < environment.sql
```

or from the repository root with the explicit path:

```bash
sudo mysql < MySQL/environment.sql
```

`mysql` and `mariadb` are the same client binary on Debian/Ubuntu
(`/usr/bin/mysql` is a symlink to `mariadb`), so either name works there.

## Query

As your own Linux user, no password is needed:

```bash
mariadb environment
```

that works because the initial server setup created an account for you,
authenticated with MariaDB's `unix_socket` plugin (the OS login is the
credential; nothing is stored in this repository). To recreate it on another
machine, run once as an admin:

```sql
CREATE USER IF NOT EXISTS '<your-linux-username>'@'localhost'
  IDENTIFIED VIA unix_socket;
GRANT ALL PRIVILEGES ON `environment`.* TO '<your-linux-username>'@'localhost';
```

Admin access uses `sudo mariadb` (Debian's `root@localhost` account is bound to
`unix_socket`, so it only works when run through sudo).

Example queries:

```bash
# list objects; SHOW FULL TABLES labels VIEWs so you can tell the 2 views apart
mariadb -e 'SHOW FULL TABLES;' environment

# row counts
mariadb -e 'SELECT COUNT(*) FROM Sunshine_Record;' environment

# climate summary view
mariadb -e 'SELECT Station_Name, Year, Month, Maximum_Temperature, Humidity
            FROM Monthly_Climate_Summary WHERE Year = 2020 ORDER BY Station_Name, Month LIMIT 5;' environment
```

## Parity with the SQLite original

Verified after load against `schema/environment.db`:

- 21 base tables and 2 views present.
- Row count identical for every table (730,324 rows total).
- 28 foreign-key relationships reported by `information_schema`.
- `Monthly_Climate_Summary` = 25,772 rows and `Monthly_Wind_Summary` = 5,619
  rows, matching SQLite; sampled query output is identical.

Notes on dialect differences: `INTEGER`→`INT`, `REAL`→`DOUBLE`, `TEXT`→`VARCHAR(255)`;
identifiers use backticks; the SQLite `strftime`/`printf` calendar validity check on
`Day_Time` is expressed as `Day <= DAY(LAST_DAY(...))`. The database uses
`utf8mb4` with the binary (`utf8mb4_bin`) collation so string primary keys behave
case-sensitively, as in SQLite.
