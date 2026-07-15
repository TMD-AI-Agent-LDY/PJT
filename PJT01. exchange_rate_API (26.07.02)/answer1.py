import requests

currency = "KRW"
url = f"https://api.frankfurter.app/latest?from=USD&to={currency}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    rate = data["rates"]["KRW"]
    print(f"1달러 = {round(rate)}원")

else:
    print("API 요청 실패:", response.status_code, response.text)