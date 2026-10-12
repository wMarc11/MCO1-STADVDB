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

ATTACH 'host=localhost port=5432 dbname=taxi_data_raw user=_____ password=_____' AS pg_db (TYPE postgres);
CREATE TABLE pg_db.public.taxi_data AS SELECT * FROM taxi_data;
