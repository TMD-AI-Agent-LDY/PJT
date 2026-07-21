"""Streamlit 복약 문의 안전 분류 Agent."""

import os

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIDetectionError
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model

from middleware import create_pii_middlewares
from schemas import MedicationInquiryAnalysis
from tools import search_medication_information


SYSTEM_PROMPT = """
당신은 복약 문의를 안전하게 분류하고 다음 행동을 안내하는 Agent입니다.

반드시 따를 규칙:
1. 모든 문의에서 search_medication_information Tool로 약품명을 조회한 뒤 답변하세요.
2. Tool에 없는 약품의 성분, 효능, 복용법, 부작용을 추측하지 마세요.
3. 복용 여부가 불확실하거나 중복 복용 가능성이 있으면 '우선 확인'으로 분류하고,
   임의로 추가 복용하라고 지시하지 마세요. 약 포장·처방전을 확인하고 약사에게 문의하도록 안내하세요.
4. 어지럼증, 구토, 새로운 이상 증상, 불확실한 처방 내용은 '우선 확인'으로 분류하세요.
5. 호흡곤란, 입술·얼굴·혀·목의 부종, 의식 저하, 경련, 심한 흉통, 빠르게 악화되는 증상은 '긴급'으로 분류하세요.
6. '긴급'이면 next_action을 '긴급 도움 요청'으로 설정하고, 즉시 119에 연락하거나 응급실에서 도움을 받도록 안내하세요.
7. 일반적인 보관 방법, 복용 시간, 기본 정보, 복약 기록 문의는 '일반'으로 분류하세요.
8. [REDACTED_EMAIL]로 가려진 이메일과 마스킹된 전화번호의 원래 값을 복원하거나 추측하지 마세요.
9. 진단을 단정하지 말고, 임의로 약을 중단·추가·변경하라고 지시하지 마세요.
""".strip()


def create_medication_agent():
    """환경 설정에 맞는 모델과 Middleware로 Agent를 생성한다."""
    model_name = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    model_provider = os.getenv("MODEL_PROVIDER", "groq")
    model = init_chat_model(model_name, model_provider=model_provider)

    return create_agent(
        model=model,
        tools=[search_medication_information],
        middleware=create_pii_middlewares(),
        response_format=ToolStrategy(MedicationInquiryAnalysis),
        system_prompt=SYSTEM_PROMPT,
    )


load_dotenv()
st.set_page_config(page_title="복약 문의 안전 분류 Agent")
st.title("복약 문의 안전 분류 Agent")

medication_name = st.text_input("약품명")
inquiry_text = st.text_area(
    "복약 문의",
    placeholder="복약과 관련된 질문을 입력하세요.",
)
analyze_button = st.button("분석하기")

if analyze_button:
    if not medication_name.strip() or not inquiry_text.strip():
        st.warning("약품명과 문의 내용을 모두 입력해주세요.")
    else:
        try:
            with st.spinner("복약 문의를 분석하고 있습니다..."):
                if "medication_agent" not in st.session_state:
                    st.session_state.medication_agent = create_medication_agent()

                agent = st.session_state.medication_agent
                response = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": (
                                    f"약품명: {medication_name.strip()}\n"
                                    f"복약 문의: {inquiry_text.strip()}"
                                ),
                            }
                        ]
                    }
                )
                result: MedicationInquiryAnalysis = response["structured_response"]

            st.subheader("Agent 답변")
            if result.urgency == "긴급":
                st.error(result.answer)
            else:
                st.info(result.answer)

            st.write(f"문의 유형: {result.inquiry_type}")
            st.write(f"긴급도: {result.urgency}")
            st.write(f"권장 행동: {result.next_action}")

            with st.expander("판단 이유"):
                st.write(result.reason)
        except PIIDetectionError:
            st.error(
                "주민등록번호가 감지되어 요청이 차단되었습니다.\n\n"
                "주민등록번호를 삭제한 뒤 다시 문의해주세요."
            )
        except Exception:
            st.error("분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
