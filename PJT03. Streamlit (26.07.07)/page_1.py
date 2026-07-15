import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

st.title("My Chatbot")

# -----------------------------
# 대화 기록 저장
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "당신은 친절한 AI 챗봇입니다. "
                "사용자의 질문에 자연스럽게 답변하세요. "
                "모르는 내용은 추측하지 말고 모른다고 알려주세요."
            )
        }
    ]


# -----------------------------
# Stream 방식 응답
# -----------------------------
def stream_gpt(question):
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    system = st.session_state.messages[0]
    history = [system] + st.session_state.messages[-10:]

    # ⭐ stream=True
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0.7,
        messages=history,
        stream=True
    )

    full_answer = ""

    # 응답이 출력될 위치
    placeholder = st.empty()

    for chunk in response:

        if (
            chunk.choices
            and chunk.choices[0].delta.content is not None
        ):
            text = chunk.choices[0].delta.content
            full_answer += text

            # 실시간 출력 + 커서 효과
            placeholder.markdown(full_answer + "▌")

    # 마지막 커서 제거
    placeholder.markdown(full_answer)

    # 대화 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_answer
    })


# -----------------------------
# 이전 대화 출력
# -----------------------------
for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# 입력창
# -----------------------------
prompt = st.chat_input("무엇을 도와드릴까요?")

if prompt:

    # 사용자 메시지는 즉시 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 말풍선 생성
    with st.chat_message("assistant"):
        stream_gpt(prompt)