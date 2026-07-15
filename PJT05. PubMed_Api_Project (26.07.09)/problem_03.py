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

params = {
    "db": "pubmed",
    "term": "cancer immunotherapy",
    "retmode": "json",
    "retmax": 50,
    "api_key": api_key,
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    result = data["esearchresult"]["idlist"]
    
else:
    print("API 요청 실패:", response.status_code, response.text)

with open (
        output_dir / "pmids_cancer_immunotherapy.txt", 
        "w", 
        encoding="UTF-8-sig"
    ) as file:
        file.write("\n".join(result))
    
print("파일 저장 완료")
print("저장된 PMID 수:", len(result))
print("첫 번째 PMID:", result[0])
print("마지막 PMID:", result[-1])
