"""환율 Agent가 사용할 미들웨어와 가드레일 설정."""

import re

from langchain.agents.middleware import (
    PIIMiddleware,
    SummarizationMiddleware,
    before_model,
)
from langchain_core.language_models import BaseChatModel
from langchain.messages import AIMessage, HumanMessage


FINANCIAL_ACTION_BLOCK_MESSAGE = (
    "이 챗봇은 환율 조회와 금액 계산만 지원합니다.\n"
    "실제 환전, 송금, 결제 또는 계좌 접근은 수행할 수 없습니다."
)

SECURITY_BLOCK_MESSAGE = (
    "Agent의 안전 규칙을 변경하거나 내부 정보를 공개하는 요청은 처리할 수 없습니다.\n"
    "정상적인 환율 조회 질문을 입력해 주세요."
)


PROMPT_ATTACK_PATTERNS = (
    r"(?:이전|앞선|기존|시스템).{0,12}(?:지시|명령|규칙).{0,15}(?:무시|따르지|덮어쓰)",
    r"(?:지시|명령|규칙).{0,15}(?:모두|전부)?.{0,8}(?:무시|따르지|덮어쓰)",
    r"(?:frankfurter|api).{0,25}(?:호출|사용).{0,12}(?:하지\s*말|말고|금지).{0,40}(?:지어내|임의|대답|말해)",
    r"(?:환율|조회\s*결과|tool\s*결과|도구\s*결과).{0,30}(?:임의의?\s*값|바꿔|변경해|조작해|왜곡해)",
    r"(?:시스템\s*프롬프트|api[_\s-]*key|api\s*키|환경\s*변수).{0,30}(?:보여|알려|출력|공개|제공|뭐야|무엇)",
    r"ignore.{0,20}(?:previous|system|all).{0,15}instructions?",
    r"(?:show|reveal|print).{0,20}(?:system\s*prompt|api[_\s-]*key|environment\s*variables?)",
)

FINANCIAL_ACTION_PATTERNS = (
    # 계좌·카드·자금으로 실제 행동을 요청하는 경우
    r"(?:계좌|카드|자금).{0,50}(?:출금|인출|이체|결제|환전|송금).{0,20}(?:해\s*줘|해주세요|해라|실행|처리|진행)",
    # 행동 동사에 직접 실행 요청이 붙는 경우
    r"(?:환전|송금|결제|이체)(?:을|를)?\s*(?:해\s*줘|해주세요|해라|실행해|처리해|진행해)",
    # 계좌에 접근하거나 잔액을 확인하는 요청
    r"(?:금융\s*)?(?:계정|계좌).{0,25}(?:로그인|접속|잔액(?:을|를)?\s*(?:조회|확인|알려)|출금|인출)",
    r"잔액.{0,15}(?:조회|확인|알려).{0,20}(?:계정|계좌)",
    # 특정 계좌로 자금을 보내는 요청
    r"계좌.{0,30}(?:송금|이체|보내).{0,15}(?:해\s*줘|해주세요|해라|실행|처리)",
)


def _latest_user_text(state: dict) -> str | None:
    """가장 최근의 사용자 텍스트를 반환한다."""
    for message in reversed(state.get("messages", [])):
        if isinstance(message, HumanMessage) and isinstance(message.content, str):
            return message.content
    return None


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def create_pii_middlewares() -> list[PIIMiddleware]:
    """README 2번의 입력 PII 보호 규칙을 반환한다."""
    return [
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        PIIMiddleware(
            "credit_card",
            strategy="block",
            apply_to_input=True,
        ),
    ]


def phone_masking_middleware() -> list[PIIMiddleware]:
    phone_number_detector_regex = (
        r"\b010[-\s]?\d{3,4}[-\s]?\d{4}\b"
    )

    return [
        PIIMiddleware(
            "phone_number",
            detector=phone_number_detector_regex,
            strategy="mask",
            apply_to_input=True,
        )
    ]


@before_model(can_jump_to=["end"])
def prompt_security_guardrail(state, runtime):
    """프롬프트 우회·결과 조작·비밀정보 요청을 모델 호출 전에 차단한다."""
    del runtime
    user_text = _latest_user_text(state)

    if user_text and _matches_any(user_text, PROMPT_ATTACK_PATTERNS):
        return {
            "messages": [AIMessage(content=SECURITY_BLOCK_MESSAGE)],
            "jump_to": "end",
        }
    return None


@before_model(can_jump_to=["end"])
def financial_action_guardrail(state, runtime):
    """실제 환전·송금·결제·계좌 접근 요청을 모델 호출 전에 차단한다."""
    del runtime
    user_text = _latest_user_text(state)

    if user_text and _matches_any(user_text, FINANCIAL_ACTION_PATTERNS):
        return {
            "messages": [AIMessage(content=FINANCIAL_ACTION_BLOCK_MESSAGE)],
            "jump_to": "end",
        }
    return None


SUMMARY_PROMPT = """
당신은 환율 상담 대화의 맥락을 보존하는 요약 도우미입니다.
다음 정보를 정확히 남긴 간결한 한국어 요약만 작성하세요.
- 사용자가 질문한 기준 통화(base)와 대상 통화(quote) 코드
- 각 질문의 금액과 주요 환율·환산 결과
- "그럼", "아까", "그 기준"과 같은 후속 표현이 가리키는 통화쌍
- 사용자가 비교하고 있던 통화쌍과 비교 목적
개인정보의 원래 값은 복원하거나 추측하지 마세요.

<messages>
{messages}
</messages>
""".strip()


def create_summarization_middleware(
    summary_model: BaseChatModel,
) -> list[SummarizationMiddleware]:
    """대화가 길어지면 요약하되 최근 대화와 통화 맥락을 보존한다."""
    return [
        SummarizationMiddleware(
            # OpenAI 대신 현재 앱에서 사용 중인 Groq 모델을 요약에도 사용한다.
            model=summary_model,
            # README의 4회 대화 시나리오에서 요약을 확인할 수 있는 임계값
            trigger=("messages", 8),
            keep=("messages", 4),
            summary_prompt=SUMMARY_PROMPT,
        )
    ]
