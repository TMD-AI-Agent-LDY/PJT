import os
import csv
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

data_dir = Path(__file__).parent
output_dir = data_dir / "output"
output_dir.mkdir(exist_ok=True)

pmids = []
with open(
    output_dir / "pmids_cancer_immunotherapy.txt", 
    "r", 
    encoding="utf-8-sig"
) as file:
    for line in file:
        pmids.append(line.strip())

api_key = os.getenv("NCBI_API_KEY")

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

params = {
    "db": "pubmed",
    "id": ",".join(pmids),
    "retmode": "xml",
    "api_key": api_key,
}

response = requests.get(url, params=params)

results = []
if response.status_code == 200:

    root = ET.fromstring(response.text)
    articles = root.findall(".//PubmedArticle")

    for article in articles:
        pmid = article.findtext(".//PMID") or ""
        title = article.findtext(".//ArticleTitle") or ""
        abstract_texts = article.findall(".//AbstractText") or ""

        abstract = ""
        for text in abstract_texts:
            if text.text:
                abstract += text.text.strip() + " "

        results.append({
            "pmid": pmid,
            "title": title.strip(),
            "abstract": abstract
        })
else:
  print("API 요청 실패:", response.status_code, response.text)

with open(
        output_dir / "abstracts_cancer_immunotherapy.csv",
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=["pmid", "title", "abstract"])
        writer.writeheader()
        writer.writerows(results)

print("파일 저장 완료")
