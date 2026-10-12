import psycopg

# Makes Python dictionaries that map values to the correct
# foreign key
def make_fk_dict(cur, key_col, value_col, table_name):
    fk_dict = {}
    cur.execute(f"SELECT * FROM {table_name};")
    values = cur.fetchall()
    for value in values:
        fk_dict[value[key_col]] = value[value_col]
    return fk_dict

def make_dim_time_dict(cur):
    key_col = 1  # hour_24
    value_col = 0  # time_key
    table_name = "dw.dim_time"
    return make_fk_dict(cur, key_col, value_col, table_name)

def make_dim_location_dict(cur):
    key_col = 1  # location_id
    value_col = 0  # location_key
    table_name = "dw.dim_location"
    return make_fk_dict(cur, key_col, value_col, table_name)

def make_dim_vendor_dict(cur):
    key_col = 1  # vendor_id
    value_col = 0  # vendor_key
    table_name = "dw.dim_vendor"
    return make_fk_dict(cur, key_col, value_col, table_name)

def make_dim_ratecode_dict(cur):
    key_col = 1  # ratecode_id
    value_col = 0  # ratecode_key
    table_name = "dw.dim_ratecode"
    return make_fk_dict(cur, key_col, value_col, table_name)

def make_dim_payment_dict(cur):
    key_col = 1  # payment_type_id
    value_col = 0  # payment_key
    table_name = "dw.dim_payment"
    return make_fk_dict(cur, key_col, value_col, table_name)

def make_dim_flag_dict(cur):
    key_col = 1  # flag_code
    value_col = 0  # flag_key
    table_name = "dw.dim_flag"
    return make_fk_dict(cur, key_col, value_col, table_name)

db_params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "taxi_data_dw",
    "user": "postgres",
    "password": "ThisIsTheDbPassword"
}

with psycopg.connect(**db_params) as conn:
    with conn.cursor() as cur:
        dim_time_dict = make_dim_time_dict(cur)
        dim_location_dict = make_dim_location_dict(cur)
        dim_vendor_dict = make_dim_vendor_dict(cur)
        dim_ratecode_dict = make_dim_ratecode_dict(cur)
        dim_payment_dict = make_dim_payment_dict(cur)
        dim_flag_dict = make_dim_flag_dict(cur)

def get_date_key(row):
    pickup_datetime = row["tpep_pickup_datetime"]
    return pickup_datetime.date()

def get_time_key(row):
    pickup_datetime = row["tpep_pickup_datetime"]
    hour = pickup_datetime.hour
    return dim_time_dict[hour]

def get_pickup_location_key(row):
    pickup_location_id = row["PULocationID"]
    return dim_location_dict[pickup_location_id]

def get_dropoff_location_key(row):
    dropoff_location_id = row["DOLocationID"]
    return dim_location_dict[dropoff_location_id]

def get_vendor_key(row):
    vendor_id = row["VendorID"]
    return dim_vendor_dict[vendor_id]

def get_ratecode_key(row):
    ratecode_id = row["RatecodeID"]
    return dim_ratecode_dict[ratecode_id]

def get_payment_key(row):
    payment_type = row["payment_type"]
    return dim_payment_dict[payment_type]

def get_flag_key(row):
    store_and_fwd_flag = row["store_and_fwd_flag"]
    return dim_flag_dict[store_and_fwd_flag]
