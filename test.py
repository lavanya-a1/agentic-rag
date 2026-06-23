import json

with open("master_dataset_enriched.json") as f:
    data = json.load(f)

for row in data:
    if row.get("player") == "Ruturaj Gaikwad":
        print(row)
        break