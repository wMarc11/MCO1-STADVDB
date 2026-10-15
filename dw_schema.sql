-- Read data dictionary first (https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf)
-- The data we might use is Yellow Taxi Trip Records 2025 (or other years if y'all want)

DROP SCHEMA IF EXISTS dw CASCADE;
CREATE SCHEMA dw;
SET search_path TO dw, public;

-- This is a STAR SCHEMA warehouse

-- Dimension tables

-- This is the pick-up date
-- Hierarchy: year > quarter > month > day
CREATE TABLE dw.dim_date (
    full_date     DATE       NOT NULL,
    year          SMALLINT   NOT NULL,
    quarter       SMALLINT   NOT NULL,
    month         SMALLINT   NOT NULL,
    month_name    VARCHAR(9) NOT NULL,
    month_abbr    CHAR(3)    NOT NULL,
    year_month    CHAR(7)    NOT NULL,           -- 'YYYY-MM'
    week_of_year  SMALLINT   NOT NULL,           -- ISO week
    day_of_month  SMALLINT   NOT NULL,
    day_of_week   SMALLINT   NOT NULL,           -- ISO 1=Mon .. 7=Sun
    day_name      VARCHAR(9) NOT NULL,
    is_weekend    BOOLEAN    NOT NULL,
    CONSTRAINT pk_dim_date      PRIMARY KEY (full_date),
    CONSTRAINT ck_dim_date_qtr  CHECK (quarter     BETWEEN 1 AND 4),
    CONSTRAINT ck_dim_date_mth  CHECK (month       BETWEEN 1 AND 12),
    CONSTRAINT ck_dim_date_dow  CHECK (day_of_week BETWEEN 1 AND 7)
);

-- This is the pick-up hour of the day
-- Hierarchy: day time bucket (time_bucket) > hour
-- Table should have one row per hour to enable roll-up and drill-down analysis
CREATE TABLE dw.dim_time (
    time_key     SMALLINT    NOT NULL,           -- hour 0..23
    hour_24      SMALLINT    NOT NULL,
    hour_label   VARCHAR(8)  NOT NULL,           -- '12 AM', '01 AM', ...
    am_pm        CHAR(2)     NOT NULL,           -- 'AM' / 'PM'
    time_bucket  VARCHAR(10) NOT NULL,           -- Late Night/Morning/Midday/Evening/Night
    is_peak      BOOLEAN     NOT NULL,           -- AM/PM rush hours
    CONSTRAINT pk_dim_time     PRIMARY KEY (time_key),
    CONSTRAINT uq_dim_time_hr  UNIQUE (hour_24),
    CONSTRAINT ck_dim_time_hr  CHECK (hour_24 BETWEEN 0 AND 23)
);

-- This is the location where the pick-up and drop-off happened (pick-up and drop-off will use this in fact table)
-- Will get data from Taxi Zone Lookup Table CSV
-- Hierarchy: borough > zone
-- (service_zone is an independent classification, not part of this hierarchy)
CREATE TABLE dw.dim_location (
    location_key INTEGER     GENERATED ALWAYS AS IDENTITY,
    location_id  SMALLINT    NOT NULL,          -- TLC LocationID (natural key)
    borough      VARCHAR(20) NOT NULL,
    zone         VARCHAR(60) NOT NULL,
    service_zone VARCHAR(20) NOT NULL,
    CONSTRAINT pk_dim_location   PRIMARY KEY (location_key),
    CONSTRAINT uq_dim_location_id UNIQUE (location_id)
);

-- These are the providers of the taximeter
-- Info in data dictionary (1, 2, 6, 7)
CREATE TABLE dw.dim_vendor (
    vendor_key  SMALLINT	GENERATED ALWAYS AS IDENTITY,
    vendor_id   SMALLINT,                       -- natural key, NULL for unknown
    vendor_name VARCHAR(60) NOT NULL,
    vendor_abbr VARCHAR(12) NOT NULL,
    CONSTRAINT pk_dim_vendor     PRIMARY KEY (vendor_key),
    CONSTRAINT uq_dim_vendor_id  UNIQUE (vendor_id)
);

-- Ratecodes
-- Info in data dictionary (1, 2, 3, 4, 5, 6, 99)
CREATE TABLE dw.dim_ratecode (
    ratecode_key  SMALLINT    GENERATED ALWAYS AS IDENTITY,
    ratecode_id   SMALLINT,                     -- natural key, NULL for unknown
    ratecode_desc VARCHAR(40) NOT NULL,
    rate_category VARCHAR(20) NOT NULL,         -- Standard/Fixed(JFK, Newark, Nassau)/Negotiated/Other(Group ride)/Unknown
    CONSTRAINT pk_dim_ratecode     PRIMARY KEY (ratecode_key),
    CONSTRAINT uq_dim_ratecode_id  UNIQUE (ratecode_id)
);

-- How the trip was paid (card, cash, no charge, dispute, etc.)
-- Info in data dictionary (0, 1, 2, 3, 4, 5, 6)
CREATE TABLE dw.dim_payment (
    payment_key     SMALLINT     GENERATED ALWAYS AS IDENTITY,
    payment_type_id SMALLINT,                   -- natural key, NULL for unknown
    payment_desc    VARCHAR(30)  NOT NULL,
    payment_category VARCHAR(20) NOT NULL,      -- Card/Flex/Cash/Other/Unknown
    CONSTRAINT pk_dim_payment    PRIMARY KEY (payment_key),
    CONSTRAINT uq_dim_payment_id UNIQUE (payment_type_id)
);

-- The store and forward indicator, or in simpler terms, the meter connectivity
CREATE TABLE dw.dim_flag (
    flag_key  SMALLINT    GENERATED ALWAYS AS IDENTITY,
    flag_code CHAR(1),                          -- 'Y' / 'N' / NULL
    flag_desc VARCHAR(45) NOT NULL,
    CONSTRAINT pk_dim_flag      PRIMARY KEY (flag_key),
    CONSTRAINT uq_dim_flag_code UNIQUE (flag_code)
);

-- Fact table
-- Grain is one taxi per trip
-- 8 dimension foreign keys (because pickup and dropoff location uses the same dimension table)
-- Also carries the raw pickup/dropoff timestamps as "degenerate dimensions" so trip duration can be recomputed
CREATE TABLE dw.fact_trip (
    trip_key              BIGINT   GENERATED ALWAYS AS IDENTITY,
    -- Foreign Keys
    full_date             DATE  NOT NULL,     -- pickup date
    time_key              SMALLINT NOT NULL,     -- pickup hour
    pickup_location_key   INTEGER  NOT NULL,
    dropoff_location_key  INTEGER  NOT NULL,
    vendor_key            SMALLINT NOT NULL,
    ratecode_key          SMALLINT NOT NULL,
    payment_key           SMALLINT NOT NULL,
    flag_key              SMALLINT NOT NULL,
	
    -- Degenerate dimensions
    pickup_ts             TIMESTAMP    NOT NULL,
    dropoff_ts            TIMESTAMP    NOT NULL,
	
    -- Measures
    passenger_count       SMALLINT,               -- if NULL = it should not be reported
    trip_distance         NUMERIC(10,2) NOT NULL,
    trip_duration_min     NUMERIC(8,2)  NOT NULL,
    fare_amount           NUMERIC(10,2) NOT NULL DEFAULT 0,
    extra                 NUMERIC(10,2) NOT NULL DEFAULT 0,
    mta_tax               NUMERIC(10,2) NOT NULL DEFAULT 0,
    tip_amount            NUMERIC(10,2) NOT NULL DEFAULT 0,
    tolls_amount          NUMERIC(10,2) NOT NULL DEFAULT 0,
    improvement_surcharge NUMERIC(10,2) NOT NULL DEFAULT 0,
    congestion_surcharge  NUMERIC(10,2),          -- NULL = not reported (distinct from 0)
    airport_fee           NUMERIC(10,2),          -- NULL = not reported (distinct from 0)
    cbd_congestion_fee    NUMERIC(10,2) NOT NULL DEFAULT 0	,
    total_amount          NUMERIC(10,2) NOT NULL DEFAULT 0,
	
    -- Lightweight data-quality flags (set during ETL)
    is_refund             BOOLEAN NOT NULL DEFAULT FALSE,  -- total_amount < 0
    distance_valid        BOOLEAN NOT NULL DEFAULT TRUE,   -- 0 < distance <= 100 mi
    duration_valid        BOOLEAN NOT NULL DEFAULT TRUE,   -- 0 < duration < 1440 min
	
    -- Constraints
    CONSTRAINT pk_fact_trip          PRIMARY KEY (trip_key),
    CONSTRAINT fk_fact_date          FOREIGN KEY (full_date)             REFERENCES dw.dim_date (full_date),
    CONSTRAINT fk_fact_time          FOREIGN KEY (time_key)             REFERENCES dw.dim_time (time_key),
    CONSTRAINT fk_fact_pickup_loc    FOREIGN KEY (pickup_location_key)  REFERENCES dw.dim_location (location_key),
    CONSTRAINT fk_fact_dropoff_loc   FOREIGN KEY (dropoff_location_key) REFERENCES dw.dim_location (location_key),
    CONSTRAINT fk_fact_vendor        FOREIGN KEY (vendor_key)           REFERENCES dw.dim_vendor (vendor_key),
    CONSTRAINT fk_fact_ratecode      FOREIGN KEY (ratecode_key)         REFERENCES dw.dim_ratecode (ratecode_key),
    CONSTRAINT fk_fact_payment       FOREIGN KEY (payment_key)          REFERENCES dw.dim_payment (payment_key),
    CONSTRAINT fk_fact_flag          FOREIGN KEY (flag_key)             REFERENCES dw.dim_flag (flag_key),
    CONSTRAINT ck_fact_passengers    CHECK (passenger_count IS NULL OR passenger_count BETWEEN 0 AND 9),
    CONSTRAINT ck_fact_duration      CHECK (trip_duration_min >= 0)
);

-- Secondary indexes on every foreign key (hash/merge/nested-loop join support).
CREATE INDEX idx_fact_trip_date         ON dw.fact_trip (full_date);
CREATE INDEX idx_fact_trip_time         ON dw.fact_trip (time_key);
CREATE INDEX idx_fact_trip_pickup_loc   ON dw.fact_trip (pickup_location_key);
CREATE INDEX idx_fact_trip_dropoff_loc  ON dw.fact_trip (dropoff_location_key);
CREATE INDEX idx_fact_trip_vendor       ON dw.fact_trip (vendor_key);
CREATE INDEX idx_fact_trip_ratecode     ON dw.fact_trip (ratecode_key);
CREATE INDEX idx_fact_trip_payment      ON dw.fact_trip (payment_key);
CREATE INDEX idx_fact_trip_flag         ON dw.fact_trip (flag_key);
-- A composite index for the most common time-series slice that we might use mostly (report by date then hour).
CREATE INDEX idx_fact_trip_date_time    ON dw.fact_trip (full_date, time_key);