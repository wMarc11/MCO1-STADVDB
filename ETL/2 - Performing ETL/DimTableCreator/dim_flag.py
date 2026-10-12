import psycopg

def main():
    # format: flag_code, flag_desc
    data = [
        ("Y", "store and forward trip"),
        ("N", "not a store and forward trip"),
        (None, "N/A")
    ]

    db_params = {
        "host": "localhost",
        "port": 5432,
        "dbname": "taxi_data_dw",
        "user": "postgres",
        "password": "ThisIsTheDbPassword"
    }

    table_name = "dw.dim_flag"
    insert_query = f"""
    INSERT INTO {table_name} (
        flag_code,
        flag_desc
    )
    VALUES (%s, %s);
    """

    with psycopg.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
            exists = len(cur.fetchall()) == 1
            if exists:
                cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
            cur.executemany(insert_query, data)

if __name__ == "__main__":
    main()
