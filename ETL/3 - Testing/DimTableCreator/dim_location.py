import pandas as pd
import psycopg

def main():
    csv_path = "sources/taxi_zone_lookup.csv"
    df = pd.read_csv(csv_path)
    data = []
    for index, row in df.iterrows():
        location_id = row["LocationID"]
        borough = row["Borough"]
        zone = row["Zone"]
        service_zone = row["service_zone"]

        data.append((
            location_id,
            borough,
            zone,
            service_zone
        ))

    db_params = {
        "host": "localhost",
        "port": 5432,
        "dbname": "test_taxi_data_dw",
        "user": "postgres",
        "password": "ThisIsTheDbPassword"
    }

    table_name = "dw.dim_location"
    insert_query = f"""
    INSERT INTO {table_name} (
        location_id,
        borough,
        zone,
        service_zone
    )
    VALUES (%s, %s, %s, %s);
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
