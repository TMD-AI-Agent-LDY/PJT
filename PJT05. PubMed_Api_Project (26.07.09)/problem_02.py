import os
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

data_dir = Path(__file__).parent
output_dir = data_dir / "output"
output_dir.mkdir(exist_ok=True)

api_key = os.getenv("NCBI_API_KEY")

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

terms = [
    "machine learning diabetes",
    "deep learning radiology",
    "Alzheimer biomarker",
    "COVID-19 vaccine",
    "cancer immunotherapy",
]

results = []
for term in terms:
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "api_key": api_key,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        count = int(data["esearchresult"]["count"])

        results.append({
            "topic": term,
            "count": count
        })
    else:
        print("API 요청 실패:", response.status_code, response.text)

with open(
    output_dir / "topic_counts.csv",
    "w",
    encoding="utf-8",
    newline=""
) as file:
    writer = csv.DictWriter(file, fieldnames=["topic", "count"])
    writer.writeheader()
    writer.writerows(results)

print("파일 저장 완료")

max_topic = max(results, key=lambda x: x["count"])
min_topic = min(results, key=lambda x: x["count"])
print(f"검색 결과가 가장 많은 주제어: {max_topic['topic']} {max_topic['count']}개")
print(f"검색 결과가 가장 적은 주제어: {min_topic['topic']} {min_topic['count']}개")
