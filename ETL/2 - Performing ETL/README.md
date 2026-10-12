## How to Use

1. In all the Python files, make sure to change the PostgreSQL password to your actual password.
2. Run `_dim_main.py` in the DimTableCreator folder. This creates the dimension tables in the database.
3. Run `main.py`. This creates the fact table in the database. Note that you have to import the raw data to PostgreSQL first before doing this (see the folder titled "1 - Importing Raw Dataset to Postgres").