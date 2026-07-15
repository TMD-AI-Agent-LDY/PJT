import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

data_dir = Path(__file__).parent
output_dir = data_dir / "output"
output_dir.mkdir(exist_ok=True)

api_key = os.getenv("NCBI_API_KEY")

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

params = {
    "db": "pubmed",
    "term": "artificial intelligence cancer",
    "retmode": "json",
    "api_key": api_key,
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    with open(
        output_dir / "raw_esearch_ai_cancer.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    result = data["esearchresult"]
    
    print("파일 저장 완료")
    print("전체 검색 결과 수:", result["count"])
    print("가져온 PMID  5개:", result["idlist"][:5])

else:
    print("API 요청 실패:", response.status_code, response.text)
