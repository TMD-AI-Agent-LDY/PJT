"""복약 문의 Agent의 개인정보 보호 Middleware 설정."""

from langchain.agents.middleware import PIIMiddleware


# 010-1234-5678, 010 1234 5678, 01012345678 형식을 모두 탐지한다.
PHONE_NUMBER_PATTERN = r"(?<!\d)010[-\s]?\d{4}[-\s]?\d{4}(?!\d)"

# 900101-1234567, 9001011234567 형식을 모두 탐지한다.
RESIDENT_REGISTRATION_NUMBER_PATTERN = r"(?<!\d)\d{6}-?\d{7}(?!\d)"


def create_pii_middlewares() -> list[PIIMiddleware]:
    """이메일·전화번호·주민등록번호 보호 규칙을 반환한다."""
    return [
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        PIIMiddleware(
            "phone_number",
            detector=PHONE_NUMBER_PATTERN,
            strategy="mask",
            apply_to_input=True,
        ),
        PIIMiddleware(
            "resident_registration_number",
            detector=RESIDENT_REGISTRATION_NUMBER_PATTERN,
            strategy="block",
            apply_to_input=True,
        ),
    ]
