# PubMed API를 활용한 논문 데이터 수집

## 프로젝트 개요

### 프로젝트 소개

NCBI PubMed API를 활용하여 의료·바이오 분야의 논문 데이터를 수집하고, 검색 결과를 분석 및 정리하는 프로젝트입니다.

### 프로젝트 목표

- NCBI PubMed API Key를 발급받고 안전하게 관리하는 방법을 익힌다.
- `requests`를 활용하여 API를 호출하고 데이터를 수집한다.
- JSON, XML, CSV 형식의 데이터를 읽고 저장하는 방법을 익힌다.
- 반복문, 조건문, 리스트, 딕셔너리를 활용하여 논문 데이터를 분석 및 집계한다.

## 준비 사항

- NCBI 계정 생성
- PubMed API Key 발급
- `.env` 파일에 `NCBI_API_KEY` 저장

## 요구사항

- AI를 사용하지 않고 직접 구현하는 것을 원칙으로 진행
- 제출 기한: 26.07.09. 18:00

### 제출 파일

```
problem_01.py
problem_02.py
...
problem_08.py
output/
README.md
.gitignore
```

- `problem_01.py` ~ `problem_08.py` : 각 요구사항 구현 코드
- `output/` : 실행 결과 파일
- `README.md` : 요구사항별 구현 내용
- `.gitignore` : API Key 등 민감한 정보 제외

---

### 요구사항 1

> API Key 발급 및 기본 검색

1. `.env` 파일을 생성하고 `NCBI_API_KEY`를 저장
2. 필요한 라이브러리 import
3. `pathlib`를 활용하여 프로젝트 경로 및 `output` 폴더 생성
4. `requests`를 이용해 ESearch API URL과 요청 파라미터(params) 설정
5. `params`에 검색 조건(`db`, `term`, `retmode`, `api_key`)을 설정하여 API 요청
6. 응답받은 JSON 데이터를 `output/raw_esearch_ai_cancer.json` 파일로 저장
7. 요구사항에 맞게 검색 결과 개수와 PMID 5개를 터미널에 출력

### 요구사항 2

> 여러 주제어 검색 결과 비교

1. 필요한 라이브러리 import
2. `pathlib`를 활용하여 프로젝트 경로 및 `output` 폴더 생성
3. `requests`를 이용해 ESearch API URL과 요청 파라미터(`params`) 설정
4. `params`에 검색 조건(`db`, `term`, `retmode`, `api_key`)을 설정하여 API 요청
5. 여러 주제어를 리스트에 저장
6. `for`문을 통해 각 주제어의 검색 결과를 조회
7. 검색 결과에서 `topic`과 `count`만 추출하여 `results` 리스트에 저장
8. `results`를 `topic_counts.csv` 파일로 저장
9. `max()`, `min()`, `lambda`를 활용하여 검색 결과가 가장 많은 주제어와 가장 적은 주제어를 집계
10. 요구사항에 맞게 결과를 터미널에 출력

### 요구사항 3

> 특정 주제 논문 50개 수집

1. 필요한 라이브러리 import
2. `pathlib`를 활용하여 프로젝트 경로 및 `output` 폴더 생성
3. `requests`를 이용해 ESearch API URL과 요청 파라미터(`params`) 설정
4. `params`에 검색 조건(`db`, `term`, `retmode`, `retmax`, `api_key`)을 설정하여 API 요청
5. `retmax`를 50으로 설정하여 PMID 50개를 조회
6. 응답 데이터에서 `idlist`만 추출하여 `result` 변수에 저장
7. `pmids_cancer_immunotherapy.txt` 파일 생성
8. `"\n".join()`을 사용하여 PMID를 한 줄에 하나씩 저장
9. 요구사항에 맞게 저장된 PMID 개수와 첫 번째, 마지막 PMID를 터미널에 출력

### 요구사항 4

> 연도별 논문 수 분석

1. 필요한 라이브러리 import
2. `pathlib`를 활용하여 프로젝트 경로 및 `output` 폴더 생성
3. 연도별 논문 수를 조회하기 위해 연도를 저장한 `years` 리스트 생성
4. `requests`를 이용해 ESearch API URL과 요청 파라미터(`params`) 설정
5. `params`에 검색 조건(`db`, `term`, `retmode`, `pdat`, `api_key`)을 설정하여 API 요청
6. `pdat`를 이용하여 각 연도의 논문 수 조회
7. 연도(`year`)와 논문 수(`count`)를 `results` 리스트에 저장
8. `max()`와 `lambda`를 활용하여 논문 수가 가장 많은 연도를 집계
9. 요구사항에 맞게 가장 많은 논문 수를 기록한 연도와 논문 수를 터미널에 출력

### 요구사항 5

> 저널별 빈도 분석

1. 필요한 라이브러리 import
2. `pathlib`를 활용하여 프로젝트 경로 및 입력 폴더(`data`) 지정
3. `with`문을 사용하여 CSV 파일 불러오기
4. `csv.DictReader`를 사용해 데이터를 딕셔너리 형태로 읽고 `for`문으로 순회
5. 저널명(`source`)을 기준으로 등장 횟수를 딕셔너리에 집계
6. `max()`를 활용하여 가장 많이 등장한 저널과 논문 수를 집계
7. 요구사항에 맞게 가장 많이 등장한 저널명과 논문 수를 터미널에 출력

### 요구사항 6

> Abstract 데이터 수집

1. 필요한 라이브러리 import
2. XML 데이터를 파싱하기 위해 `xml.etree.ElementTree` 라이브러리 추가
3. `pathlib`를 활용하여 프로젝트 경로 및 `output` 폴더 생성
4. `pmids_cancer_immunotherapy.txt` 파일을 읽어 PMID를 리스트에 저장
5. `requests`를 이용해 EFetch API URL과 요청 파라미터(`params`) 설정
6. `params`에 검색 조건(`db`, `id`, `retmode`, `api_key`)을 설정하여 API 요청
7. EFetch 응답을 XML 형식으로 받아 `ElementTree`를 사용해 파싱
8. 각 논문의 `PMID`, `ArticleTitle`, `AbstractText`를 추출하여 `results` 리스트에 저장
9. `results`를 `abstracts_cancer_immunotherapy.csv` 파일로 저장
10. 요구사항에 맞게 파일 저장 완료 메시지를 터미널에 출력

- **AI 활용 내역**: _EFetch를 사용하여 추출하고 XML 데이터를 처리하는 로직 구현에 AI를 도구로 활용하였습니다._

### 요구사항 7

> 키워드 포함 여부 분석

1. 필요한 라이브러리 import
2. `pathlib`를 활용하여 프로젝트 경로 및 입력 폴더(`output`) 지정
3. 분석할 키워드를 `keywords` 리스트에 저장
4. `with`문과 `csv.DictReader`를 사용하여 `abstracts_cancer_immunotherapy.csv` 파일을 읽기
5. `for`문을 통해 각 논문의 제목(`title`)과 초록(`abstract`)에서 키워드 포함 여부 확인
6. 키워드의 전체 등장 횟수를 `keyword_counts` 딕셔너리에 집계
7. 키워드가 포함된 논문 수를 `article_counts` 딕셔너리에 집계
8. `max()`를 활용하여 가장 많이 등장한 키워드와 해당 키워드가 포함된 논문 수를 집계
9. 요구사항에 맞게 가장 자주 등장하는 키워드와 등장 논문 수를 터미널에 출력

### 요구사항 8

> 최종 비교 리포트 작성

1. 필요한 라이브러리 import
2. `pathlib`를 활용하여 프로젝트 경로 및 `output` 폴더 생성
3. ESearch API와 EFetch API URL 설정
4. 비교할 주제를 `topics` 리스트에 저장
5. `requests`를 이용해 ESearch API를 호출하여 각 주제의 전체 논문 수와 PMID 20개를 조회
6. 조회한 PMID를 이용해 EFetch API를 호출하고 XML 데이터를 `ElementTree`로 파싱
7. 각 논문의 `PMID`, `제목`, `저널명`, `출판일`을 추출하여 `results` 리스트에 저장
8. 제목에 `patient`가 포함된 논문 수를 주제별로 집계
9. `results`를 `final_topic_comparison.csv` 파일로 저장
10. `max()`를 활용하여 검색 결과가 가장 많은 주제를 집계
11. 요구사항에 맞게 검색 결과가 가장 많은 주제, `patient`가 포함된 논문 수, 가장 최근 논문의 PMID와 제목을 터미널에 출력

- **AI 활용 내역**: _ESearch와 EFetch를 조합하여 여러 주제를 비교하고 XML 데이터를 처리하는 로직 구현에 AI를 도구로 활용하였습니다._

---

## 참고 자료

- NCBI E-Utilities API
  - https://www.ncbi.nlm.nih.gov/home/develop/api/
  - https://www.ncbi.nlm.nih.gov/books/NBK25500/
  - https://www.ncbi.nlm.nih.gov/books/NBK25499/
  - https://dataguide.nlm.nih.gov/eutilities/utilities.html
- Wikidocs
  - https://wikidocs.net/
