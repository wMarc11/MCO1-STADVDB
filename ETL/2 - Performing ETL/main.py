import psycopg
from jinja2.lexer import describe_token_expr
from psycopg.rows import dict_row

from dim_keys import (
    get_date_key,
    get_time_key,
    get_pickup_location_key,
    get_dropoff_location_key,
    get_vendor_key,
    get_ratecode_key,
    get_payment_key,
    get_flag_key
)
from helpers import *

dest_table_name = "dw.fact_trip"

src_db_params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "taxi_data_raw",
    "user": "postgres",
    "password": "ThisIsTheDbPassword"
}
src_conn = psycopg.connect(**src_db_params)
src_cursor = src_conn.cursor(name="large_query_cursor", row_factory=dict_row)

dest_db_params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "taxi_data_dw",
    "user": "postgres",
    "password": "ThisIsTheDbPassword"
}
dest_conn = psycopg.connect(**dest_db_params)
dest_cursor = dest_conn.cursor()

insert_query = f"""
INSERT INTO {dest_table_name} (
    full_date,
    time_key,
    pickup_location_key,
    dropoff_location_key,
    vendor_key,
    ratecode_key,
    payment_key,
    flag_key,
    pickup_ts,
    dropoff_ts,
    passenger_count,
    trip_distance,
    trip_duration_min,
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    congestion_surcharge,
    airport_fee,
    cbd_congestion_fee,
    total_amount,
    is_refund,
    distance_valid
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s);
"""

dest_cursor.execute(f"SELECT 1 FROM {dest_table_name} LIMIT 1;")
exists = len(dest_cursor.fetchall()) == 1
if exists:
    dest_cursor.execute(f"TRUNCATE TABLE {dest_table_name} RESTART IDENTITY;")

src_cursor.execute("SELECT * FROM taxi_data")

count = 0
step = 5000
while True:
    rows = src_cursor.fetchmany(step)

    new_rows = []
    for row in rows:
        full_date = get_date_key(row)
        if full_date.year != 2025: # there was some data from 12/31/2024 which caused an FK violation
            continue
        time_key = get_time_key(row)
        pickup_location_key = get_pickup_location_key(row)
        dropoff_location_key = get_dropoff_location_key(row)
        vendor_key = get_vendor_key(row)
        ratecode_key = get_ratecode_key(row)
        payment_key = get_payment_key(row)
        flag_key = get_flag_key(row)
        pickup_ts = row["tpep_pickup_datetime"]
        dropoff_ts = row["tpep_dropoff_datetime"]
        passenger_count = row["passenger_count"]
        trip_distance = get_decimal(row["trip_distance"])
        minutes_elapsed = (dropoff_ts - pickup_ts).total_seconds() / 60
        trip_duration_min = get_decimal(minutes_elapsed)
        fare_amount = get_decimal(row["fare_amount"])
        extra = get_decimal(row["extra"])
        mta_tax = get_decimal(row["mta_tax"])
        tip_amount = get_decimal(row["tip_amount"])
        tolls_amount = get_decimal(row["tolls_amount"])
        improvement_surcharge = get_decimal(row["improvement_surcharge"])
        congestion_surcharge = get_decimal(row["congestion_surcharge"])
        airport_fee = get_decimal(row["Airport_fee"])
        cbd_congestion_fee = get_decimal(row["cbd_congestion_fee"])
        total_amount = get_decimal(row["total_amount"])
        if total_amount is None:
            is_refund = False
        else:
            is_refund = (total_amount < 0)
        if trip_distance is None:
            distance_valid = False
        else:
            distance_valid = (0 < trip_distance < 100)

        new_rows.append((
            full_date,
            time_key,
            pickup_location_key,
            dropoff_location_key,
            vendor_key,
            ratecode_key,
            payment_key,
            flag_key,
            pickup_ts,
            dropoff_ts,
            passenger_count,
            trip_distance,
            trip_duration_min,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            improvement_surcharge,
            congestion_surcharge,
            airport_fee,
            cbd_congestion_fee,
            total_amount,
            is_refund,
            distance_valid
        ))

    dest_cursor.executemany(insert_query, new_rows)

    if not rows:
        break

    count += step
    print(f"{count} rows outputted")

dest_conn.commit() # needed without "with" statement

src_cursor.close()
src_conn.close()
dest_cursor.close()
dest_conn.close()