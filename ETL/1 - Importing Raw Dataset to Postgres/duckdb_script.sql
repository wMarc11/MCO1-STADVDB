INSTALL postgres;
LOAD postgres;

CREATE TABLE taxi_data AS SELECT * FROM read_parquet([
    'yellow_tripdata_2025-01.parquet',
    'yellow_tripdata_2025-02.parquet',
    'yellow_tripdata_2025-03.parquet',
    'yellow_tripdata_2025-04.parquet',
    'yellow_tripdata_2025-05.parquet',
    'yellow_tripdata_2025-06.parquet',
    'yellow_tripdata_2025-07.parquet',
    'yellow_tripdata_2025-08.parquet',
    'yellow_tripdata_2025-09.parquet',
    'yellow_tripdata_2025-10.parquet',
    'yellow_tripdata_2025-11.parquet',
    'yellow_tripdata_2025-12.parquet',
]);


ATTACH 'host=localhost port=5432 dbname=taxi_data_raw user=postgres password=ThisIsTheDbPassword' AS pg_db (TYPE postgres);

DROP TABLE IF EXISTS pg_db.public.taxi_data;

CREATE TABLE pg_db.public.taxi_data AS
SELECT
    VendorID,
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    passenger_count,
    trip_distance,
    RatecodeID,
    store_and_fwd_flag,
    PULocationID,
    DOLocationID,
    payment_type,
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    total_amount,
    congestion_surcharge,
    Airport_fee AS airport_fee,
    cbd_congestion_fee
FROM taxi_data;
