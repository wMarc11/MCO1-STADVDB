from decimal import Decimal

# Gets Decimal rounded off to 2 decimal points,
# or 0 if the input is None.
# We do this because the number needs to be Decimal
# to work with PostgreSQL's NUMERIC data type.
def get_decimal(num):
    if num is None:
        return 0 # 0 is the default
    return Decimal(f"{num:.2f}")

# Same as get_decimal but preserves None.
# Used for measures where "unknown / not reported" must stay distinguishable
# from a real 0 (e.g. congestion_surcharge, airport_fee).
def get_decimal_nullable(num):
    if num is None:
        return None
    return Decimal(f"{num:.2f}")