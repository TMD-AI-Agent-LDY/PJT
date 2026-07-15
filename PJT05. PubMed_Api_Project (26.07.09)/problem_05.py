import csv
from pathlib import Path

data_dir = Path(__file__).parent
input_dir = data_dir / "data"

counts = {}
with open(input_dir / "summary_cancer_immunotherapy.csv", encoding="utf-8") as file:
    data = csv.DictReader(file)

    for row in data:
        if row["source"] in counts:
            counts[row["source"]] += 1
        else:
            counts[row["source"]] = 1

print(f"가장 많이 등장한 저널명: {max(counts, key=counts.get)}")
print(f"논문 수: {max(counts.values())}개")
