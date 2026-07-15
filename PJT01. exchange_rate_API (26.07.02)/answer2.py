import requests

major_currencies = ["KRW", "EUR", "JPY", "GBP"]
currency = input("통화 코드를 입력하세요: ").upper()

url = f"https://api.frankfurter.app/latest?from=USD&to={currency}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    rate = data["rates"][currency]
    date = data["date"]

    print(f"1 USD = {rate} {currency}")
    print(f"기준일: {date}")

else:
    print("API 요청 실패:", response.status_code, response.text)