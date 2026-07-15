import requests

major_currencies = ["KRW", "EUR", "JPY", "GBP"]
currency = input("통화 코드를 입력하세요: ").upper()

if currency not in major_currencies:
    print("입력 오류: 주요 통화 목록에 있는 값만 입력할 수 있습니다.")
else:
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