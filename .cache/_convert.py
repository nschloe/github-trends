import json
import sys

filename = sys.argv[1]

with open(filename) as f:
    data = json.load(f)

if "data" in data:
    data = data["data"]


with open(filename, "w") as f:
    json.dump(data, f, indent=2)
