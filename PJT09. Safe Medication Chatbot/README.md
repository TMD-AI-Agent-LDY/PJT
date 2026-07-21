**미니 프로젝트: 복약 문의 안전 분류 Agent**

사용자가 복약 관련 질문을 입력하면 개인정보를 보호하고, 문의 유형과 긴급도를 분석한 뒤 다음 행동을 안내하는 Streamlit 서비스를 구현하세요.

---

**1. 최종 구현 화면**

Streamlit 화면에는 다음 요소만 구현하세요.

* 서비스 제목 (복약 문의 안전 분류 Agent)
* 약품명 입력창
* 문의 입력창
* 전송 버튼
* Agent 답변
* 문의 유형
* 긴급도
* 권장 행동

---

**2. 필수 요구사항**

다음 5개 요구사항을 구현하세요.

**요구사항 1 – Streamlit 입력 화면 구현**

다음 입력 요소를 구현하세요.

```python
medication_name = st.text_input("약품명")

inquiry_text = st.text_area(
    "복약 문의",
    placeholder="복약과 관련된 질문을 입력하세요.",
)

analyze_button = st.button("분석하기")
```

입력값이 비어 있는 경우 Agent를 실행하지 말고 안내 메시지를 출력하세요.

```text
약품명과 문의 내용을 모두 입력해주세요.
```

---

**업무 2 – 약품 조회 Tool 구현**

다음 Tool을 구현하세요.

```python
@tool
def search_medication_information(
    medication_name: str,
) -> str:
    """데이터에서 약품의 기본 정보를 조회합니다."""
```

약품 정보 데이터는 아래 Python 딕셔너리를 사용하세요.

```python
MEDICATIONS = {
    "혈압약 A": {
        "category": "혈압약",
        "instructions": "처방 지시와 약 봉투를 확인하세요.",
        "precautions": "복용 여부가 불확실한 경우 임의로 추가 복용하지 마세요.",
    },
    "당뇨약 B": {
        "category": "당뇨약",
        "instructions": "식사와 관련된 처방 지시를 확인하세요.",
        "precautions": "중복 복용 여부를 확인하고 약사에게 문의하세요.",
    },
    "수면제 C": {
        "category": "수면제",
        "instructions": "처방된 복용 시간을 확인하세요.",
        "precautions": "어지럼증과 낙상 위험에 주의하세요.",
    },
}
```

조회 결과가 없으면 다음과 같이 반환하세요.

```text
해당 약품을 찾을 수 없습니다.
약품 포장이나 처방전을 확인하고 약사 또는 의료기관에 문의해주세요.
```

Agent는 Tool에 없는 약품 정보를 추측해서는 안 됩니다.

---

**업무 3 – 개인정보 보호 Middleware 적용**

사용자 문의에 포함된 다음 개인정보를 보호하세요.

| 개인정보   | 처리 방식 |
| ------ | ----- |
| 이메일 주소 | 가림 처리 |
| 전화번호   | 마스킹   |
| 주민등록번호 | 요청 차단 |

이메일은 LangChain의 기본 PII 유형을 사용하세요.

```python
PIIMiddleware(
    "email",
    strategy="redact",
    apply_to_input=True,
)
```

전화번호는 다음 형식을 탐지하도록 Custom Detector를 작성하세요.

```text
010-1234-5678
010 1234 5678
01012345678
```

전화번호는 `mask` 방식으로 처리하세요.

주민등록번호는 다음 형식을 탐지하세요.

```text
900101-1234567
9001011234567
```

주민등록번호가 포함된 요청은 `block` 방식으로 차단하세요.

---

**업무 4 – 구조화된 분석 결과 구현**

Pydantic을 사용해 다음 출력 구조를 정의하세요.

```python
from typing import Literal
from pydantic import BaseModel, Field


class MedicationInquiryAnalysis(BaseModel):
    inquiry_type: Literal[
        "복용 시간",
        "복용 여부",
        "중복 복용",
        "부작용 의심",
        "약품 정보",
        "기타",
    ]

    urgency: Literal[
        "일반",
        "우선 확인",
        "긴급",
    ]

    next_action: Literal[
        "일반 안내",
        "약사 확인",
        "의료기관 확인",
        "긴급 도움 요청",
    ]

    reason: str = Field(
        description="문의 유형과 긴급도를 판단한 이유"
    )

    answer: str = Field(
        description="사용자에게 보여줄 안전한 복약 안내"
    )
```

Agent가 이 구조에 맞춰 결과를 반환하도록 구현하세요.

---

**업무 5 – 분석 결과 출력**

Agent 실행 결과를 Streamlit 화면에 표시하세요.

```python
st.info(result.answer)

with st.expander("판단 이유"):
    st.write(result.reason)
```

긴급도가 `긴급`인 경우에는 `st.error()`를 사용하세요.

```python
if result.urgency == "긴급":
    st.error(result.answer)
else:
    st.info(result.answer)
```

---

**3. 긴급도 분류 기준**

**일반**

* 약 보관 방법 문의
* 일반적인 복용 시간 문의
* 약품의 기본 정보 문의
* 복약 기록 방법 문의

**우선 확인**

* 약을 복용했는지 기억나지 않음
* 중복 복용 가능성
* 복용 후 어지럼증
* 구토나 새로운 이상 증상
* 처방 내용이 불확실함

**긴급**

* 호흡곤란
* 입술, 얼굴, 혀 또는 목의 부종
* 의식 저하
* 경련
* 심한 흉통
* 빠르게 악화되는 증상

---

**5. 필수 테스트**

다음 입력을 모두 테스트하세요.

**테스트 1 – 일반 문의**

```text
혈압약 A는 언제 복용하나요?
```

기대 결과:

```text
긴급도: 일반
```

**테스트 2 – 복용 여부 불확실**

```text
오늘 아침 약을 먹었는지 기억이 안 납니다.
한 알 더 먹어도 되나요?
```

기대 결과:

```text
문의 유형: 복용 여부 또는 중복 복용
긴급도: 우선 확인
```

Agent가 추가 복용을 지시해서는 안 됩니다.

**테스트 3 – 부작용 의심**

```text
약을 먹은 뒤 어지럽고 걸을 때 휘청거립니다.
```

기대 결과:

```text
문의 유형: 부작용 의심
긴급도: 우선 확인
```

**테스트 4 – 긴급 증상**

```text
약을 먹은 뒤 숨쉬기 어렵고 입술이 붓습니다.
```

기대 결과:

```text
긴급도: 긴급
권장 행동: 긴급 도움 요청
```

**테스트 5 – 전화번호**

```text
약을 두 번 먹은 것 같아요. 어떻게 해야하죠?
010-1234-5678로 전화주세요.
```

기대 결과:

* 전화번호 마스킹
* 복약 문의는 정상 분석

**테스트 6 – 주민등록번호**

```text
제 주민등록번호는 900101-1234567입니다.
```

기대 결과:

* Agent 실행 차단
* 주민등록번호를 제거하고 다시 입력하도록 안내

---