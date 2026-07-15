import streamlit as st

page_1 = st.Page("page_1.py", title="챗봇", icon=
"🤖")
page_2 = st.Page("page_2.py", title="엑셀 데이터 업로드", icon=
"📄")
page_3 = st.Page("page_3.py", title="프로필 페이지", icon=
"🙎‍♂️")

pages = st.navigation([page_1, page_2, page_3])

pages.run()