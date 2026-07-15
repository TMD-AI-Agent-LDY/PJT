-- 헬스케어 SQLite 데이터 분석 미니 프로젝트
-- 실행 방법: sqlite3 healthcare.sqlite3 < healthcare_analysis.sql

.bail on
.echo off
.headers on
.mode column
.nullvalue NULL

-- ============================================================
-- 0. CSV 데이터 적재
-- ============================================================
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS visits_2024;
DROP TABLE IF EXISTS visits_2025;

CREATE TABLE patients (
    "환자ID" TEXT PRIMARY KEY,
    "성별" TEXT NOT NULL,
    "나이" INTEGER NOT NULL,
    "지역" TEXT NOT NULL,
    "보험유형" TEXT NOT NULL,
    "가입일" TEXT NOT NULL,
    "키_cm" REAL,
    "체중_kg" REAL,
    "BMI" REAL,
    "흡연상태" TEXT,
    "운동습관" TEXT,
    "당뇨_기왕력" INTEGER,
    "고혈압_기왕력" INTEGER,
    "이상지질혈증_기왕력" INTEGER
);

CREATE TABLE visits_2024 (
    "방문ID" TEXT PRIMARY KEY,
    "환자ID" TEXT NOT NULL,
    "방문일" TEXT NOT NULL,
    "진료과" TEXT NOT NULL,
    "방문유형" TEXT NOT NULL,
    "주증상" TEXT,
    "수축기혈압" REAL,
    "이완기혈압" REAL,
    "심박수" REAL,
    "진료비_원" INTEGER NOT NULL,
    "보험청구액_원" INTEGER,
    "재방문필요" INTEGER,
    "처방여부" INTEGER,
    FOREIGN KEY ("환자ID") REFERENCES patients ("환자ID")
);

CREATE TABLE visits_2025 (
    "방문ID" TEXT PRIMARY KEY,
    "환자ID" TEXT NOT NULL,
    "방문일" TEXT NOT NULL,
    "진료과" TEXT NOT NULL,
    "방문유형" TEXT NOT NULL,
    "주증상" TEXT,
    "수축기혈압" REAL,
    "이완기혈압" REAL,
    "심박수" REAL,
    "진료비_원" INTEGER NOT NULL,
    "보험청구액_원" INTEGER,
    "재방문필요" INTEGER,
    "처방여부" INTEGER,
    FOREIGN KEY ("환자ID") REFERENCES patients ("환자ID")
);

.mode csv
.import --skip 1 patients.csv patients
.import --skip 1 visits_2024.csv visits_2024
.import --skip 1 visits_2025.csv visits_2025
.mode column

CREATE INDEX idx_patients_bmi ON patients ("BMI");
CREATE INDEX idx_patients_region ON patients ("지역");
CREATE INDEX idx_visits_2025_patient ON visits_2025 ("환자ID");
CREATE INDEX idx_visits_2025_cost ON visits_2025 ("진료비_원");

-- ============================================================
-- 요구사항 1. 테이블 Load 결과와 기본 조회
-- ============================================================
SELECT '요구사항 1-1: patients 앞 5개 행' AS 구분;
SELECT * FROM patients LIMIT 5;

SELECT '요구사항 1-2: visits_2024 앞 5개 행' AS 구분;
SELECT * FROM visits_2024 LIMIT 5;

SELECT '요구사항 1-3: visits_2025 앞 5개 행' AS 구분;
SELECT * FROM visits_2025 LIMIT 5;

-- ============================================================
-- 요구사항 2. SELECT, ORDER BY, LIMIT
-- ============================================================
SELECT '요구사항 2-1: 환자 주요 컬럼 조회' AS 구분;
SELECT "환자ID", "성별", "나이", "지역", "BMI"
FROM patients;

SELECT '요구사항 2-2: BMI가 높은 환자 상위 10명' AS 구분;
SELECT "환자ID", "성별", "나이", "지역", "BMI"
FROM patients
ORDER BY "BMI" DESC, "환자ID" ASC
LIMIT 10;

SELECT '요구사항 2-3: 진료비가 높은 2025년 방문 상위 10건' AS 구분;
SELECT *
FROM visits_2025
ORDER BY "진료비_원" DESC, "방문ID" ASC
LIMIT 10;

-- ============================================================
-- 요구사항 3. WHERE, IN, LIKE
-- ============================================================
SELECT '요구사항 3-1: BMI 25 이상 환자' AS 구분;
SELECT *
FROM patients
WHERE "BMI" >= 25
ORDER BY "BMI" DESC, "환자ID" ASC;

SELECT '요구사항 3-2: 서울 또는 경기 거주 환자' AS 구분;
SELECT *
FROM patients
WHERE "지역" IN ('서울', '경기')
ORDER BY "지역", "환자ID";

SELECT '요구사항 3-3: 내과 또는 응급의학과 방문' AS 구분;
SELECT *
FROM visits_2025
WHERE "진료과" IN ('내과', '응급의학과')
ORDER BY "방문일", "방문ID";

SELECT '요구사항 3-4: 주증상에 기침이 포함된 방문' AS 구분;
SELECT *
FROM visits_2025
WHERE "주증상" LIKE '%기침%'
ORDER BY "방문일", "방문ID";

-- ============================================================
-- 요구사항 4. JOIN
-- ============================================================
SELECT '요구사항 4-1: 환자 정보가 포함된 2025년 방문 기록' AS 구분;
SELECT
    v."방문ID",
    v."방문일",
    v."진료과",
    v."방문유형",
    v."진료비_원",
    p."성별",
    p."나이",
    p."지역",
    p."BMI"
FROM visits_2025 AS v
INNER JOIN patients AS p ON v."환자ID" = p."환자ID";

SELECT '요구사항 4-2: BMI 25 이상 환자의 방문 기록' AS 구분;
SELECT
    v."방문ID",
    v."방문일",
    v."진료과",
    v."방문유형",
    v."진료비_원",
    p."성별",
    p."나이",
    p."지역",
    p."BMI"
FROM visits_2025 AS v
INNER JOIN patients AS p ON v."환자ID" = p."환자ID"
WHERE p."BMI" >= 25
ORDER BY p."BMI" DESC, v."방문ID" ASC;

SELECT '요구사항 4-3: JOIN 결과 중 진료비 상위 20건' AS 구분;
SELECT
    v."방문ID",
    v."방문일",
    v."진료과",
    v."방문유형",
    v."진료비_원",
    p."성별",
    p."나이",
    p."지역",
    p."BMI"
FROM visits_2025 AS v
INNER JOIN patients AS p ON v."환자ID" = p."환자ID"
ORDER BY v."진료비_원" DESC, v."방문ID" ASC
LIMIT 20;

-- ============================================================
-- 요구사항 5. GROUP BY와 집계 함수
-- ============================================================
SELECT '요구사항 5-1: 지역별 환자 수' AS 구분;
SELECT "지역", COUNT(*) AS "환자수"
FROM patients
GROUP BY "지역"
ORDER BY "환자수" DESC, "지역" ASC;

SELECT '요구사항 5-2: 진료과별 방문 건수' AS 구분;
SELECT "진료과", COUNT(*) AS "방문건수"
FROM visits_2025
GROUP BY "진료과"
ORDER BY "방문건수" DESC, "진료과" ASC;

SELECT '요구사항 5-3: 진료과별 총 진료비' AS 구분;
SELECT "진료과", SUM("진료비_원") AS "총진료비_원"
FROM visits_2025
GROUP BY "진료과"
ORDER BY "총진료비_원" DESC, "진료과" ASC;

SELECT '요구사항 5-4: 방문유형별 평균 진료비' AS 구분;
SELECT "방문유형", ROUND(AVG("진료비_원"), 2) AS "평균진료비_원"
FROM visits_2025
GROUP BY "방문유형"
ORDER BY "평균진료비_원" DESC, "방문유형" ASC;

-- ============================================================
-- 선택 요구사항 6. UNION ALL
-- UNION ALL은 중복을 제거하지 않고 두 조회 결과를 그대로 합친다.
-- ============================================================
SELECT '요구사항 6-1: 2024~2025년 진료비 상위 20건' AS 구분;
WITH all_visits AS (
    SELECT '2024' AS "연도", * FROM visits_2024
    UNION ALL
    SELECT '2025' AS "연도", * FROM visits_2025
)
SELECT *
FROM all_visits
ORDER BY "진료비_원" DESC, "방문ID" ASC
LIMIT 20;

SELECT '요구사항 6-2: 2024~2025년 진료과별 방문 건수' AS 구분;
WITH all_visits AS (
    SELECT * FROM visits_2024
    UNION ALL
    SELECT * FROM visits_2025
)
SELECT "진료과", COUNT(*) AS "방문건수"
FROM all_visits
GROUP BY "진료과"
ORDER BY "방문건수" DESC, "진료과" ASC;
