import os
import re
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

load_dotenv()

API_URL = "https://api.frankfurter.dev/v2/rate"
MODEL = "openai/gpt-oss-120b"
SYSTEM_PROMPT = """
당신은 친절하고 사람처럼 대화하는 한국어 환율 안내원입니다.
딱딱한 보고서나 항목 나열 대신, 옆에서 설명하듯 짧고 자연스러운 문장으로 답하세요.
사용자의 말투와 맥락을 살피고 후속 질문에는 "네, 그럼"처럼 자연스럽게 이어가세요.
과도한 인사, 같은 말 반복, 도구를 사용했다는 설명은 하지 마세요.

환율 질문에는 반드시 get_exchange_rate 도구를
매번 호출하고, 결과의 기준일·환율·환산 금액·통화 코드를 답변에 포함하세요.
후속 질문에서 빠진 통화는 이전 대화에서 찾으세요.
통화 이름은 ISO 코드로 바꾸세요(달러 USD, 원화 KRW, 유로 EUR, 엔화 JPY,
영국 파운드 GBP, 캐나다 달러 CAD, 호주 달러 AUD, 위안 CNY, 프랑 CHF).
과거 날짜가 있으면 YYYY-MM-DD로 도구에 전달하고, 없으면 빈 문자열을 전달하세요.
도구 오류는 추측하지 말고 사용자에게 그대로 설명하세요.
""".strip()


@tool
def get_exchange_rate(
    base: str, quote: str, amount: float = 1, requested_date: str = ""
) -> str:
    """환율을 조회해 금액을 환산합니다.

    Args:
        base: 기준 통화의 3자리 ISO 코드.
        quote: 대상 통화의 3자리 ISO 코드.
        amount: 환산할 0 이상의 금액.
        requested_date: 과거 조회일(YYYY-MM-DD). 최신 환율은 빈 문자열.
    """
    base, quote = base.upper().strip(), quote.upper().strip()
    if not re.fullmatch(r"[A-Z]{3}", base) or not re.fullmatch(r"[A-Z]{3}", quote):
        return "오류: 통화 코드는 USD처럼 영문 3자리여야 합니다."

    try:
        amount = float(amount)
        if amount < 0:
            raise ValueError
    except (TypeError, ValueError):
        return "오류: 금액은 0 이상의 숫자여야 합니다."

    if requested_date:
        try:
            if date.fromisoformat(requested_date) > date.today():
                return "오류: 미래 날짜의 환율은 조회할 수 없습니다."
        except ValueError:
            return "오류: 날짜는 YYYY-MM-DD 형식이어야 합니다."

    if base == quote:
        return (
            f"기준일: {requested_date or '해당 없음'}\n환율: 1 {base} = 1 {quote}\n"
            f"환산 금액: {amount:,.2f} {base} = {amount:,.2f} {quote}"
        )

    try:
        response = requests.get(
            f"{API_URL}/{base}/{quote}",
            params={"date": requested_date} if requested_date else None,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        rate = float(data["rate"])
    except requests.HTTPError:
        return f"오류: {base} 또는 {quote}는 지원하지 않는 통화입니다."
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return "오류: 환율 서버에서 정보를 가져오지 못했습니다."

    return (
        f"기준일: {data['date']}\n환율: 1 {base} = {rate:,.6f} {quote}\n"
        f"환산 금액: {amount:,.2f} {base} = {amount * rate:,.2f} {quote}"
    )


@st.cache_resource
def get_agent():
    model = init_chat_model(MODEL, model_provider="groq", temperature=0.3)
    return create_agent(model, [get_exchange_rate], system_prompt=SYSTEM_PROMPT)


def stream_answer(messages):
    """도구 호출이 끝난 뒤 생성되는 AI 답변만 스트리밍합니다."""
    for chunk, _ in get_agent().stream(
        {"messages": messages}, stream_mode="messages"
    ):
        if getattr(chunk, "type", "") in {"ai", "AIMessageChunk"}:
            if isinstance(chunk.content, str) and chunk.content:
                yield chunk.content


st.set_page_config(page_title="실시간 환율 챗봇", page_icon="💱")
st.title("실시간 환율 챗봇")

if "rooms" not in st.session_state:
    st.session_state.rooms = {"대화 1": []}

with st.sidebar:
    st.header("대화방")
    room = st.selectbox("대화방 선택", st.session_state.rooms)
    if st.button("새 대화방", use_container_width=True):
        name = f"대화 {len(st.session_state.rooms) + 1}"
        st.session_state.rooms[name] = []
        st.rerun()
    tracing = os.getenv("LANGSMITH_TRACING", "").lower() == "true"
    st.caption(f"LangSmith 추적: {'켜짐' if tracing else '꺼짐'}")

messages = st.session_state.rooms[room]
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

api_key = os.getenv("GROQ_API_KEY", "").strip()
if not api_key:
    st.error(".env에 GROQ_API_KEY를 설정해 주세요.")

if prompt := st.chat_input(
    "예: 100달러는 원화로 얼마야?", disabled=not api_key
):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("답변을 생각하고 있어요..."):
                answer = st.write_stream(stream_answer(messages))
        except Exception as error:
            answer = f"처리 중 오류가 발생했습니다. ({type(error).__name__})"
            st.error(answer)

    messages.append({"role": "assistant", "content": answer})
