import requests
import sys
import os

LOGIN = os.getenv("STOUT_LOGIN")
PASSWORD = os.getenv("STOUT_PASSWORD")

DEVICE_ID = "74664"
ENV_ID = 11  # отопление

AUTH_URL = "https://boiler.stout.ru/auth/"
DASHBOARD_URL = "https://boiler.stout.ru/api/dashboard/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://boiler.stout.ru",
    "Referer": "https://boiler.stout.ru/login.php",
}


def login(session: requests.Session) -> bool:
    payload = {
        "login": LOGIN,
        "pass": PASSWORD,
        # если на фронте есть “remember me” — его обычно тоже шлют
        "remember": "1",
    }

    r = session.post(AUTH_URL, data=payload, headers=HEADERS)

    print("LOGIN RESPONSE STATUS:", r.status_code)

    # Пытаемся сначала распарсить JSON
    try:
        data = r.json()
        print("LOGIN RESPONSE JSON:", data)
        # предполагаем, что err == 0 — успешный логин
        return data.get("err") == 0
    except Exception as e:
        # Если пришёл HTML / текст — выводим начало тела для дебага
        print("LOGIN RESPONSE is not JSON:", type(e), e)
        print("LOGIN RESPONSE TEXT (first 500 chars):")
        print(r.text[:500])
        return False


def set_temperature(session: requests.Session, value: float) -> str:
    payload = {
        "action": "setEnvGoal",
        "deviceId": DEVICE_ID,
        "data": {
            "id": ENV_ID,
            "goal": value,
            "resetMode": 0,
        },
    }

    r = session.post(DASHBOARD_URL, json=payload, headers=HEADERS)
    return r.text


def main():
    if len(sys.argv) < 2:
        print("Ошибка: укажите температуру, например: python boiler_api.py 50")
        return

    value = float(sys.argv[1])
    print(f"Устанавливаю температуру: {value}°C...")

    s = requests.Session()

    if login(s):
        print("✔ Авторизация успешна")
    else:
        print("❌ Ошибка авторизации")
        return

    response = set_temperature(s, value)
    print("Ответ сервера:", response)


if __name__ == "__main__":
    main()
