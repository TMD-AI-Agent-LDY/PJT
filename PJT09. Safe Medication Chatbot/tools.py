"""복약 문의 Agent가 사용하는 약품 조회 Tool."""

from langchain.tools import tool


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


@tool
def search_medication_information(medication_name: str) -> str:
    """데이터에서 약품의 기본 정보를 조회합니다."""
    medication = MEDICATIONS.get(medication_name.strip())

    if medication is None:
        return (
            "해당 약품을 찾을 수 없습니다.\n"
            "약품 포장이나 처방전을 확인하고 약사 또는 의료기관에 문의해주세요."
        )

    return (
        f"약품명: {medication_name.strip()}\n"
        f"분류: {medication['category']}\n"
        f"복용 안내: {medication['instructions']}\n"
        f"주의사항: {medication['precautions']}"
    )
