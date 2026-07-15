import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:  # pragma: no cover - handled in UI
    Groq = None


APP_TITLE = "Streamlit AI Chatbot"
DB_PATH = "chatbot.db"
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant. Answer clearly and concisely in Korean unless the user asks otherwise."
MODEL_OPTIONS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "qwen/qwen3-32b",
    "gemma2-9b-it",
]
PROMPT_PRESETS = {
    "기본": DEFAULT_SYSTEM_PROMPT,
    "밝은 톤": "You are a bright, cheerful assistant. Answer in Korean with an upbeat and friendly tone.",
    "구수한 톤": "You are a warm, folksy assistant. Answer in Korean with a cozy, familiar, and easygoing tone.",
    "쌉T": "You are a very logical, direct assistant. Answer in Korean with concise, structured, no-nonsense responses.",
    "쌉F": "You are a very empathetic assistant. Answer in Korean with gentle, considerate, and emotionally aware responses.",
    "장난기 많은 톤": "You are a playful assistant. Answer in Korean with light humor and a witty tone, without losing clarity.",
    "차분한 톤": "You are a calm assistant. Answer in Korean with steady, reassuring, and well-balanced responses.",
}
DEFAULT_MODEL = MODEL_OPTIONS[0]
DEFAULT_PROMPT_KEY = "기본"


load_dotenv()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate_rooms_table(conn):
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(chat_rooms);").fetchall()}
    if "model_name" not in columns:
        conn.execute(f"ALTER TABLE chat_rooms ADD COLUMN model_name TEXT NOT NULL DEFAULT '{DEFAULT_MODEL}'")
    if "prompt_key" not in columns:
        conn.execute(
            f"ALTER TABLE chat_rooms ADD COLUMN prompt_key TEXT NOT NULL DEFAULT '{DEFAULT_PROMPT_KEY}'"
        )
    if "system_prompt" not in columns:
        conn.execute(
            f"ALTER TABLE chat_rooms ADD COLUMN system_prompt TEXT NOT NULL DEFAULT '{DEFAULT_SYSTEM_PROMPT}'"
        )


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chat_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model_name TEXT NOT NULL DEFAULT 'openai/gpt-oss-120b',
                prompt_key TEXT NOT NULL DEFAULT '기본',
                system_prompt TEXT NOT NULL DEFAULT 'You are a helpful AI assistant. Answer clearly and concisely in Korean unless the user asks otherwise.',
                created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                FOREIGN KEY (room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_room_created_at
                ON messages(room_id, created_at, id);
            """
        )
        _migrate_rooms_table(conn)


def list_rooms(order_by: str = "recent"):
    order_sql = "ASC" if order_by == "oldest" else "DESC"
    with get_connection() as conn:
        return conn.execute(
            f"""
            SELECT
                r.id,
                r.name,
                r.model_name,
                r.prompt_key,
                r.system_prompt,
                r.created_at,
                COALESCE(m.last_message_at, r.created_at) AS last_activity_at,
                COALESCE(m.message_count, 0) AS message_count
            FROM chat_rooms r
            LEFT JOIN (
                SELECT
                    room_id,
                    MAX(created_at) AS last_message_at,
                    COUNT(*) AS message_count
                FROM messages
                GROUP BY room_id
            ) m ON m.room_id = r.id
            ORDER BY datetime(last_activity_at) {order_sql}, r.id {order_sql}
            """
        ).fetchall()


def create_room_with_config(name: str, model_name: str, prompt_key: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chat_rooms (name, model_name, prompt_key, system_prompt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name.strip(),
                model_name,
                prompt_key,
                PROMPT_PRESETS.get(prompt_key, DEFAULT_SYSTEM_PROMPT),
                utc_now_iso(),
            ),
        )
        return cursor.lastrowid


def rename_room(room_id: int, name: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE chat_rooms SET name = ? WHERE id = ?", (name.strip(), room_id))


def update_room_config(room_id: int, model_name: str, prompt_key: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE chat_rooms SET model_name = ?, prompt_key = ?, system_prompt = ? WHERE id = ?",
            (model_name, prompt_key, PROMPT_PRESETS.get(prompt_key, DEFAULT_SYSTEM_PROMPT), room_id),
        )


def delete_room(room_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_rooms WHERE id = ?", (room_id,))


def clear_room_messages(room_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE room_id = ?", (room_id,))


def save_message(room_id: int, role: str, content: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (room_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (room_id, role, content, utc_now_iso()),
        )


def load_messages(room_id: int):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE room_id = ?
            ORDER BY datetime(created_at) ASC, id ASC
            """,
            (room_id,),
        ).fetchall()


def build_client():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None, "GROQ_API_KEY가 설정되어 있지 않습니다."
    if Groq is None:
        return None, "groq 패키지가 설치되어 있지 않습니다."
    return Groq(api_key=api_key), None


def chat_completion(messages, model_name: str):
    client, error = build_client()
    if error:
        return None, error

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip(), None
    except Exception as exc:  # pragma: no cover - runtime dependent
        return None, str(exc)


def ensure_session_state():
    defaults = {
        "selected_room_id": None,
        "new_room_name": "",
        "rename_room_name": "",
        "rename_room_target_id": None,
        "selected_model": DEFAULT_MODEL,
        "prompt_preset": DEFAULT_PROMPT_KEY,
        "room_order": "recent",
        "delete_confirm_room_id": None,
        "delete_confirm_checked": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def pick_default_room(rooms):
    if st.session_state.selected_room_id is not None:
        existing_ids = {room["id"] for room in rooms}
        if st.session_state.selected_room_id in existing_ids:
            return st.session_state.selected_room_id
    return rooms[0]["id"] if rooms else None


def sidebar_controls(rooms):
    st.sidebar.title("채팅방")
    st.sidebar.subheader("정렬")
    st.session_state.room_order = st.sidebar.radio(
        "채팅방 정렬",
        ["recent", "oldest"],
        format_func=lambda value: "최근 채팅방 순" if value == "recent" else "오래된 채팅방 순",
        index=0 if st.session_state.room_order == "recent" else 1,
        horizontal=True,
    )

    with st.sidebar.form("create_room_form", clear_on_submit=True):
        room_model = st.selectbox(
            "모델",
            MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(st.session_state.selected_model)
            if st.session_state.selected_model in MODEL_OPTIONS
            else 0,
        )
        room_prompt_key = st.selectbox(
            "시스템 프롬프트",
            list(PROMPT_PRESETS.keys()),
            index=list(PROMPT_PRESETS.keys()).index(st.session_state.prompt_preset)
            if st.session_state.prompt_preset in PROMPT_PRESETS
            else 0,
        )
        st.caption(PROMPT_PRESETS[room_prompt_key])
        st.text_input("새 채팅방 이름", key="new_room_name", placeholder="예: 프로젝트 상담")
        submitted = st.form_submit_button("채팅방 생성")
        if submitted:
            room_name = st.session_state.new_room_name.strip() or f"채팅방 {datetime.now().strftime('%m%d %H%M')}"
            new_room_id = create_room_with_config(room_name, room_model, room_prompt_key)
            st.session_state.selected_room_id = new_room_id
            st.session_state.selected_model = room_model
            st.session_state.prompt_preset = room_prompt_key
            st.rerun()

    st.sidebar.divider()

    room_options = {f"{room['name']} (메시지 {room['message_count']}개)": room["id"] for room in rooms}
    if room_options:
        labels = list(room_options.keys())
        selected_label = next(
            (label for label, room_id in room_options.items() if room_id == st.session_state.selected_room_id),
            labels[0],
        )
        chosen_label = st.sidebar.selectbox("저장된 채팅방", labels, index=labels.index(selected_label))
        st.session_state.selected_room_id = room_options[chosen_label]
    else:
        st.sidebar.info("저장된 채팅방이 없습니다. 새 채팅방을 만들어 주세요.")

    room_id = st.session_state.selected_room_id
    if room_id is not None:
        current_room = next((room for room in rooms if room["id"] == room_id), None)
        if st.session_state.rename_room_target_id != room_id:
            st.session_state.rename_room_name = current_room["name"] if current_room else ""
            st.session_state.rename_room_target_id = room_id

        st.sidebar.text_input("채팅방 이름 수정", key="rename_room_name")
        if st.sidebar.button("이름 저장", use_container_width=True):
            new_name = st.session_state.rename_room_name.strip()
            if new_name:
                rename_room(room_id, new_name)
                st.session_state.rename_room_name = ""
                st.session_state.rename_room_target_id = None
                st.rerun()

        st.sidebar.selectbox(
            "현재 채팅방 모델",
            MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(current_room["model_name"]) if current_room and current_room["model_name"] in MODEL_OPTIONS else 0,
            key="room_model_editor",
        )
        st.sidebar.selectbox(
            "현재 채팅방 프롬프트",
            list(PROMPT_PRESETS.keys()),
            index=list(PROMPT_PRESETS.keys()).index(current_room["prompt_key"]) if current_room and current_room["prompt_key"] in PROMPT_PRESETS else 0,
            key="room_prompt_editor",
        )
        st.sidebar.caption(PROMPT_PRESETS.get(st.session_state.room_prompt_editor, DEFAULT_SYSTEM_PROMPT))
        if st.sidebar.button("채팅방 설정 저장", use_container_width=True):
            update_room_config(room_id, st.session_state.room_model_editor, st.session_state.room_prompt_editor)
            st.rerun()

        if st.sidebar.button("현재 채팅방 대화 비우기", use_container_width=True):
            clear_room_messages(room_id)
            st.rerun()

        st.sidebar.divider()
        st.sidebar.subheader("삭제")
        st.session_state.delete_confirm_room_id = room_id
        st.session_state.delete_confirm_checked = st.sidebar.checkbox(
            "선택한 채팅방과 메시지를 삭제합니다.",
            value=st.session_state.delete_confirm_checked if st.session_state.delete_confirm_room_id == room_id else False,
            key=f"delete_confirm_{room_id}",
        )
        delete_button_disabled = not st.session_state.delete_confirm_checked
        if st.sidebar.button("현재 채팅방 삭제", type="primary", use_container_width=True, disabled=delete_button_disabled):
            delete_room(room_id)
            st.session_state.selected_room_id = None
            st.session_state.delete_confirm_room_id = None
            st.session_state.delete_confirm_checked = False
            st.rerun()


def render_messages(messages):
    for message in messages:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.markdown(message["content"])


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="💬", layout="wide")
    init_db()
    ensure_session_state()

    rooms = list_rooms(st.session_state.room_order)
    st.session_state.selected_room_id = pick_default_room(rooms)

    sidebar_controls(rooms)

    st.title("Streamlit AI 챗봇")
    st.caption("SQLite에 채팅방과 메시지를 영구 저장합니다.")

    room_id = st.session_state.selected_room_id
    if room_id is None:
        st.info("왼쪽 사이드바에서 채팅방을 생성해 주세요.")
        return

    current_room = next((room for room in rooms if room["id"] == room_id), None)
    room_title = current_room["name"] if current_room else "선택한 채팅방"
    st.subheader(room_title)
    if current_room:
        st.caption(f"모델: {current_room['model_name']} / 프롬프트: {current_room['prompt_key']}")

    stored_messages = load_messages(room_id)
    render_messages(stored_messages)

    prompt = st.chat_input("메시지를 입력하세요")
    if prompt:
        save_message(room_id, "user", prompt)

        history = load_messages(room_id)
        system_prompt = current_room["system_prompt"] if current_room else DEFAULT_SYSTEM_PROMPT
        selected_model = current_room["model_name"] if current_room else DEFAULT_MODEL
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend({"role": row["role"], "content": row["content"]} for row in history)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                reply, error = chat_completion(openai_messages, selected_model)
                if error:
                    st.error(error)
                else:
                    st.markdown(reply)
                    save_message(room_id, "assistant", reply)

        st.rerun()


if __name__ == "__main__":
    main()
