import psycopg

def main():
    # format: ratecode_id, ratecode_desc, rate_category
    data = [
        (1, "Standard rate", "Standard"),
        (2, "JFK", "Fixed"),
        (3, "Newark", "Fixed"),
        (4, "Nassau or Westchester", "Fixed"),
        (5, "Negotiated fare", "Negotiated"),
        (6, "Group ride", "Other"),
        (99, "Null/unknown", "Unknown"),
        (None, "N/A", "Unknown")
    ]

    db_params = {
        "host": "localhost",
        "port": 5432,
        "dbname": "test_taxi_data_dw",
        "user": "postgres",
        "password": "ThisIsTheDbPassword"
    }

    table_name = "dw.dim_ratecode"
    insert_query = f"""
    INSERT INTO {table_name} (
        ratecode_id,
        ratecode_desc,
        rate_category
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
