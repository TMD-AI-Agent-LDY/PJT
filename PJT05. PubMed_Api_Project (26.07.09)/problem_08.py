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

api_key = os.getenv("NCBI_API_KEY")

esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

topics = [
    "precision medicine oncology",
    "wearable device hypertension",
    "microbiome obesity",
]

results = []
topic_counts = {}
patient_counts = {}

for topic in topics:
    params = {
        "db": "pubmed",
        "term": topic,
        "retmode": "json",
        "retmax": 20,
        "sort": "pub date",
        "api_key": api_key,
    }

    response = requests.get(esearch_url, params=params)

    if response.status_code == 200:
        data = response.json()

        topic_counts[topic] = int(data["esearchresult"]["count"])
        pmids = data["esearchresult"]["idlist"]

        if not pmids:
            patient_counts[topic] = 0
            continue

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "api_key": api_key,
        }
    else:
        print("API 요청 실패:", response.status_code, response.text)

    response = requests.get(efetch_url, params=params)
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        articles = root.findall(".//PubmedArticle")

        patient_counts[topic] = 0

        for article in articles:
            pmid = article.findtext(".//PMID") or ""
            title = article.findtext(".//ArticleTitle") or ""
            journal = article.findtext(".//Journal/Title") or ""

            year = article.findtext(".//PubDate/Year")
            month = article.findtext(".//PubDate/Month")
            day = article.findtext(".//PubDate/Day")
            pubdate = " ".join(
                part for part in [year, month, day] if part
            )

            if "patient" in title.lower():
                patient_counts[topic] += 1

            results.append({
                "topic": topic,
                "total_count": topic_counts[topic],
                "pmid": pmid,
                "title": title.strip(),
                "source": journal.strip(),
                "pubdate": pubdate,
            })

    else:
        print("API 요청 실패:", response.status_code, response.text)

with open(
    output_dir / "final_topic_comparison.csv",
    "w",
    encoding="utf-8",
    newline=""
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[ "topic", "total_count", "pmid", "title", "source", "pubdate"]
    )
    writer.writeheader()
    writer.writerows(results)

print("파일 저장 완료")

most_topic = max(topic_counts, key=topic_counts.get)
print(f"세 주제 중 검색 결과 수가 가장 많은 주제: {most_topic} {topic_counts[most_topic]}")
print(f"patient 포함 논문 수: {patient_counts}")
print(f"가장 최근 연도 논문의 PMID: {results[0]['pmid']}")
print(f"가장 최근 연도 논문의 제목: {results[0]['title']}")
