import psycopg

def main():
    # format: vendor_id, vendor_name, vendor_abbr
    data = [
        (1, "Creative Mobile Technologies, LLC", "CMT"),
        (2, "Curb Mobility, LLC", "CM"),
        (6, "Myle Technologies Inc", "MT"),
        (7, "Helix", "H"),
        (None, "N/A", "N/A")
    ]

    db_params = {
        "host": "localhost",
        "port": 5432,
        "dbname": "test_taxi_data_dw",
        "user": "postgres",
        "password": "ThisIsTheDbPassword"
    }

    table_name = "dw.dim_vendor"
    insert_query = f"""
    INSERT INTO {table_name} (
        vendor_id,
        vendor_name,
        vendor_abbr
    )
    VALUES (%s, %s, %s);
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
