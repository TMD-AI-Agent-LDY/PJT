import streamlit as st
import pandas as pd

st.set_page_config(page_title="엑셀 업로드", layout="wide")

st.title("📄 엑셀 데이터 업로드")

uploaded_file = st.file_uploader(
    "엑셀 파일(.xlsx)을 선택하세요.",
    type=["xlsx"]
)

if uploaded_file is not None:
    # 엑셀 읽기
    df = pd.read_excel(uploaded_file)

    st.success("업로드 완료!")

    # 데이터 정보
    col1, col2 = st.columns(2)
    with col1:
        st.metric("행(Row)", len(df))
    with col2:
        st.metric("열(Column)", len(df.columns))

    st.divider()

    # 데이터 출력
    st.subheader("데이터 미리보기")
    st.dataframe(df, use_container_width=True)

    # 컬럼 목록
    st.subheader("컬럼 정보")
    st.write(df.columns.tolist())