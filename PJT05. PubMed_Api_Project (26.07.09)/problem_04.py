import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

data_dir = Path(__file__).parent
output_dir = data_dir / "output"
output_dir.mkdir(exist_ok=True)

api_key = os.getenv("NCBI_API_KEY")

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

years = [2021, 2022, 2023, 2024, 2025]

results = []
for year in years:
    params = {
        "db": "pubmed",
        "term": "CRISPR gene therapy",
        "retmode": "json",
        "pdat": year,
        "api_key": api_key,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        count = int(data["esearchresult"]["count"])

        results.append({
            "year": year,
            "count": count
        })
       
    else:
        print("API 요청 실패:", response.status_code, response.text)

max_value = max(results, key=lambda x: x["count"])
print(f"검색 결과가 가장 많은 연도: {max_value['year']}")
print(f"논문 수: {max_value['count']}개")
