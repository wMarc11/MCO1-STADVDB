from decimal import Decimal

# Gets Decimal rounded off to 2 decimal points,
# or 0 if the input is None.
# We do this because the number needs to be Decimal
# to work with PostgreSQL's NUMERIC data type.
def get_decimal(num):
    if num is None:
        return 0 # 0 is the default
    return Decimal(f"{num:.2f}")