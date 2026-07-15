import csv
from pathlib import Path

data_dir = Path(__file__).parent
input_dir = data_dir / "output"

keywords = ["immunotherapy", "tumor", "survival", "response", "clinical trial"]

keyword_counts = {}
article_counts = {}
with open(
    input_dir / "abstracts_cancer_immunotherapy.csv", 
    "r",
    encoding="utf-8"
) as file:
    data = csv.DictReader(file)

    for row in data:
        for keyword in keywords:
            if keyword in row["title"]:
                if keyword in keyword_counts:
                    keyword_counts[keyword] += 1
                else:
                    keyword_counts[keyword] = 1
                
            if keyword in row["abstract"]:
                if keyword in keyword_counts:
                    keyword_counts[keyword] += 1
                else:
                    keyword_counts[keyword] = 1

            if keyword in row["title"] or keyword in row["abstract"]:
                if keyword in article_counts:
                    article_counts[keyword] += 1
                else:
                    article_counts[keyword] = 1

print(f"가장 자주 등장하는 키워드: {max(keyword_counts, key=keyword_counts.get)}")
print(f"등장 논문 수: {max(article_counts.values())}")
