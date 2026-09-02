# MySQL / MariaDB clone of the environment database

A MySQL-compatible snapshot of the ByteForge Group 07 environment database that
lives as `schema/environment.db` (SQLite) at the project root. The clone keeps
the exact BCNF structure: 21 tables, 28 relationships, 2 views, and all
730,324 rows of data.

## Files

- `environment.sql` — self-contained MySQL/MariaDB dump snapshot:
  creates the `environment` database, its schema (tables, primary keys,
  foreign keys, check constraints, the two summary views), and loads all data.

## Restore / load

The dump is idempotent: it drops and recreates the known tables and views, then
reloads the data.

```bash
sudo mysql < MySQL/environment.sql
```

As the current Linux user (authenticated through the MariaDB `unix_socket`
plugin, no password stored in the repository):

```bash
mariadb environment
```

## Query

```bash
# list tables (21 tables + 2 views)
mariadb -e 'SHOW TABLES;' environment

# row counts
mariadb -e 'SELECT COUNT(*) FROM Sunshine_Record;' environment

# climate summary view
mariadb -e 'SELECT Station_Name, Year, Month, Maximum_Temperature, Humidity
            FROM Monthly_Climate_Summary WHERE Year = 2020 ORDER BY Station_Name, Month LIMIT 5;' environment
```

Admin access uses `sudo mariadb` (Debian's default `root@localhost` unix_socket
account).

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
