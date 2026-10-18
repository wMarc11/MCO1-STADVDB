import psycopg
from datetime import time

def main():
    data = []
    for hour in range(24):
        current_time = time(hour, 0, 0)
        time_key = hour
        hour_24 = hour
        hour_label = current_time.strftime("%I %p")
        am_pm = current_time.strftime("%p")
        # time_bucket
        if current_time < time(6, 0):
            time_bucket = "Late Night"
        elif current_time < time(12, 0):
            time_bucket = "Morning"
        elif current_time < time(18, 0):
            time_bucket = "Midday"
        elif current_time < time(21, 0):
            time_bucket = "Evening"
        else:
            time_bucket = "Night"
        # is_peak
        if (
                time(6, 0) <= current_time < time(10, 0) or
                time(16, 0) <= current_time < time(20, 0)
        ):
            is_peak = True
        else:
            is_peak = False

        data.append((
            time_key,
            hour_24,
            hour_label,
            am_pm,
            time_bucket,
            is_peak
        ))

    db_params = {
        "host": "localhost",
        "port": 5432,
        "dbname": "test_taxi_data_dw",
        "user": "postgres",
        "password": "ThisIsTheDbPassword"
    }

    table_name = "dw.dim_time"
    insert_query = f"""
    INSERT INTO {table_name} (
        time_key,
        hour_24,
        hour_label,
        am_pm,
        time_bucket,
        is_peak
    )
    VALUES (%s, %s, %s, %s, %s, %s);
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
