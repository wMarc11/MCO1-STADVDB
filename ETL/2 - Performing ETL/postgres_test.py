import psycopg

db_params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "taxi_data_raw",
    "user": "postgres",
    "password": "ThisIsTheDbPassword"
}

with psycopg.connect(**db_params) as conn:
    with conn.cursor(name="large_query_cursor") as cur:
        cur.execute("SELECT * FROM taxi_data")

        count = 0
        while True:
            rows = cur.fetchmany(1000)
            count += 1000
            if not rows:
                break
            print(f"{count} rows processed")