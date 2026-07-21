"""복약 문의 Agent의 구조화 출력 스키마."""

from typing import Literal

from pydantic import BaseModel, Field


class MedicationInquiryAnalysis(BaseModel):
    """사용자에게 표시할 복약 문의 분석 결과."""

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

    reason: str = Field(description="문의 유형과 긴급도를 판단한 이유")
    answer: str = Field(description="사용자에게 보여줄 안전한 복약 안내")
