import psycopg
from datetime import date, timedelta

data = []
year = 2025
start_date = date(year, 1, 1)
end_date = date(year, 12, 31)

current_date = start_date
while current_date <= end_date:
    full_date = current_date
    year = current_date.year
    quarter = (current_date.month - 1) // 3 + 1
    month = current_date.month
    month_name = current_date.strftime("%B")
    month_abbr = current_date.strftime("%b")
    year_month = current_date.strftime("%Y-%m")
    week_of_year = current_date.isocalendar().week
    day_of_month = current_date.day
    day_of_week = current_date.isoweekday()
    day_name = current_date.strftime("%A")
    is_weekend = (day_of_week == 6 or day_of_week == 7)

    data.append((
        full_date,
        year,
        quarter,
        month,
        month_name,
        month_abbr,
        year_month,
        week_of_year,
        day_of_month,
        day_of_week,
        day_name,
        is_weekend
    ))

    current_date += timedelta(days=1)

db_params = {
    "host": "localhost",
    "port": 5432,
    "dbname": "taxi_data_dw",
    "user": "postgres",
    "password": "ThisIsTheDbPassword"
}

table_name = "dw.dim_date"
insert_query = f"""
INSERT INTO {table_name} (
    full_date,
    year,
    quarter,
    month,
    month_name,
    month_abbr,
    year_month,
    week_of_year,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

with psycopg.connect(**db_params) as conn:
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
        exists = len(cur.fetchall()) == 1
        if exists:
            cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        cur.executemany(insert_query, data)
