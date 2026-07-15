import streamlit as st
import requests

st.title("환율 조회 웹앱")

currency_names = {
    "KRW": "대한민국 원 (KRW)",
    "USD": "미국 달러 (USD)",
    "EUR": "유로 (EUR)",
    "JPY": "일본 엔 (JPY)",
    "GBP": "영국 파운드 (GBP)"
}

currencies = ["KRW", "USD", "EUR", "JPY", "GBP"]

if "history" not in st.session_state:
    st.session_state.history = []

base_currency = st.selectbox(
    "기준 통화", 
    options=currencies, 
    index=1,
    format_func=lambda x: currency_names[x]
)

target_currency = st.selectbox(
    "변환할 통화", 
    options=currencies, 
    index=0,
    format_func=lambda x: currency_names[x]
)

amount = st.number_input("금액", min_value=0.0, value=100.0, step=1.0)

if st.button("환율 조회하기"):
    if base_currency == target_currency:
        st.warning("같은 통화끼리는 환율 조회가 필요 없습니다.")
    else:
        api_url = f"https://api.frankfurter.dev/v1/latest?base={base_currency}&symbols={target_currency}"
        
        try:
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                
                rate = data["rates"][target_currency]
                date = data["date"]
                total_converted = amount * rate
                
                st.write(f"1 {base_currency} = {rate:.2f} {target_currency}")
                st.write(f"{amount} {base_currency} = {total_converted:.2f} {target_currency}")
                st.write(f"기준일: {date}")
                
                st.markdown("### 환율 결과 (Metric)")
                st.metric(
                    label=f"{base_currency} ➔ {target_currency}", 
                    value=f"{total_converted:,.2f} {target_currency}",
                    delta=f"1 {base_currency} = {rate:.4f} {target_currency}"
                )
                
                history_item = f"[{date}] {amount} {base_currency} ➔ {total_converted:,.2f} {target_currency} (1 {base_currency} = {rate:.4f} {target_currency})"
                st.session_state.history.append(history_item)
                
            else:
                st.error(f"API 요청에 실패했습니다. (Error Code: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            st.error(f"네트워크 오류가 발생했습니다: {e}")


st.markdown("---")

st.subheader("최근 조회 이력")
if st.session_state.history:
    for item in reversed(st.session_state.history):
        st.write(item)
else:
    st.caption("조회된 이력이 없습니다.")
