import json


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


filename = "random_data.csv"

with open(filename, "r") as file:
    lines = file.readlines()

col_names = lines[0].split(",")
num_cols = len(col_names)
for i in range(num_cols):
    col_names[i] = col_names[i].strip()
    col_names[i] = col_names[i].strip('"')
    if col_names[i] == "Airport_fee":
        col_names[i] = "airport_fee"
del lines[0]

sample_data = [
    {
        "description": "Total amount is null",
        "expected": "is_refund = FALSE"
    },
    {
        "description": "Total amount is negative",
        "expected": "is_refund = TRUE"
    },
    {
        "description": "Total amount is 0",
        "expected": "is_refund = FALSE"
    },
    {
        "description": "Total amount is greater than 0",
        "expected": "is_refund = FALSE"
    },
    {
        "description": "Trip distance is null",
        "expected": "distance_valid = FALSE"
    },
    {
        "description": "Trip distance is negative",
        "expected": "distance_valid = FALSE"
    },
    {
        "description": "Trip distance is 0",
        "expected": "distance_valid = FALSE"
    },
    {
        "description": "Trip distance is between 0 and 100 miles",
        "expected": "distance_valid = TRUE"
    },
    {
        "description": "Trip distance is exactly 100",
        "expected": "distance_valid = TRUE"
    },
    {
        "description": "Trip distance is greater than 100",
        "expected": "distance_valid = FALSE"
    },
    {
        "description": "Trip duration is negative",
        "expected": "duration_valid = FALSE"
    },
    {
        "description": "Trip duration is 0",
        "expected": "duration_valid = FALSE"
    },
    {
        "description": "Trip duration is between 0 and 1440 minutes",
        "expected": "duration_valid = TRUE"
    },
    {
        "description": "Trip duration is exactly 1440 minutes",
        "expected": "duration_valid = FALSE"
    },
    {
        "description": "Trip duration is greater than 1440 minutes",
        "expected": "duration_valid = FALSE"
    }
]
target_num_rows = len(sample_data)

count = 0
for line in lines:
    row = line.split(",")
    data = {}
    for i in range(num_cols):
        text = row[i].strip('"')
        if text == "NULL":
            text = None
        elif is_number(text):
            text = float(text)
        data[col_names[i]] = text
    sample_data[count]["data"] = data
    count += 1
    if count >= target_num_rows:
        break

with open("sample_data.json", "w") as file:
    file.write(json.dumps(sample_data, indent=4))