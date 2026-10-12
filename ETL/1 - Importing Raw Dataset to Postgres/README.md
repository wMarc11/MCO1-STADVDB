## How to Import Raw Dataset to Postgres

1. Download the data from the [website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) (download all 12 months from 2025 for yellow taxi trip data).
2. Download [DuckDB](https://duckdb.org/install/?platform=windows&environment=cli). I used the command line version (specifically 1.5.6). The next steps will assume you also downloaded the command line version, but if you are familiar with DuckDB, you can use a different version.
3. Move the yellow taxi .parquet files and the DuckDB .exe file into this folder.
4. In pgAdmin 4, create a database called "taxi-data-raw" on your local PostgreSQL.
5. In `duckdb_script.sql`, fill in the blanks for "user" and "password" in line 19 with your actual PostgreSQL user and password. (Note: It's probably user=postgres, unless you changed it from the default.)
6. Use DuckDB to execute `duckdb_script.sql`. One way to do this is opening the command line in this folder and running `duckdb < duckdb_script.sql`. (If this doesn't work, try just running `duckdb` and then copy and pasting the script into the command line.)
7. After a few minutes, hopefully, the database will be successfully imported into Postgres.
