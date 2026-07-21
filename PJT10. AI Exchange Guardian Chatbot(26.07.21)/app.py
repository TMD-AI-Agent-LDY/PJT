import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import PIIDetectionError
from langgraph.checkpoint.memory import InMemorySaver

from tools import get_exchange_rate

from middleware import (
    create_pii_middlewares,
    create_summarization_middleware,
    financial_action_guardrail,
    phone_masking_middleware,
    prompt_security_guardrail,
)

load_dotenv()

if "agent" not in st.session_state:
    model = init_chat_model("openai/gpt-oss-120b", model_provider="groq")

    st.session_state.agent = create_agent(
        model,
        tools=[get_exchange_rate],
        checkpointer=InMemorySaver(),
        middleware=[
            *create_pii_middlewares(),
            *phone_masking_middleware(),
            prompt_security_guardrail,
            financial_action_guardrail,
            *create_summarization_middleware(model),
        ],
        system_prompt=(
            "환율 조회와 금액 환산만 돕습니다. "
            "[REDACTED_EMAIL]로 가려진 이메일의 원래 값을 복원하거나 추측하지 마세요. "
            "마스킹된 휴대전화 번호의 원래 값도 복원하거나 추측하지 마세요."
        ),
    )

agent = st.session_state.agent

if "messages" not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input("무엇을 도와드릴까요?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            {"configurable": {"thread_id": "1"}},
        )
        answer = response["messages"][-1].content
    except PIIDetectionError:
        answer = (
            "카드번호가 감지되어 요청이 차단되었습니다.\n\n"
            "카드번호를 삭제한 뒤 다시 질문해 주세요."
        )

    st.session_state.messages.append({"role": "assistant", "content": answer})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
