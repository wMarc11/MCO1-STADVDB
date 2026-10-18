import psycopg

def main(db_name):
    # format: payment_type_id, payment_desc, payment_category
    data = [
        (0, "Flex Fare trip", "Flex"),
        (1, "Credit card", "Card"),
        (2, "Cash", "Cash"),
        (3, "No charge", "Other"),
        (4, "Dispute", "Other"),
        (5, "Unknown", "Unknown"),
        (6, "Voided trip", "Other"),
        (None, "N/A", "Unknown")
    ]

    db_params = {
        "host": "localhost",
        "port": 5432,
        "dbname": db_name,
        "user": "postgres",
        "password": "ThisIsTheDbPassword"
    }

    table_name = "dw.dim_payment"
    insert_query = f"""
    INSERT INTO {table_name} (
        payment_type_id,
        payment_desc,
        payment_category
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
