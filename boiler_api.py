import requests
import sys
import os

LOGIN = os.getenv("STOUT_LOGIN")
PASSWORD = os.getenv("STOUT_PASSWORD")

DEVICE_ID = "74664"
ENV_ID = 11  # отопление

LOGIN_URL = "https://boiler.stout.ru/auth/"
SET_TEMP_URL = "https://boiler.stout.ru/api/dashboard/"

# Общие заголовки, чтобы мы выглядели как обычный браузер
DEFAULT_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/json;charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://boiler.stout.ru/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def login(session: requests.Session) -> bool:
    payload = {
        "action": "login",
        "login": LOGIN,
        "pass": PASSWORD,
    }

    r = session.post(LOGIN_URL, json=payload, headers=DEFAULT_HEADERS, timeout=15)

    print("LOGIN RESPONSE STATUS:", r.status_code)

    # Если сервер внезапно вернул HTML / не json — показываем кусок и выходим
    content_type = r.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        print("LOGIN RESPONSE (non-JSON):", r.text[:500])
        return False

    try:
        data = r.json()
    except Exception as e:
        print("JSON decode error:", e)
        print("RAW LOGIN RESPONSE:", r.text[:500])
        return False

    print("LOGIN JSON:", data)
    return data.get("err") == 0


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

    r = session.post(SET_TEMP_URL, json=payload, headers=DEFAULT_HEADERS, timeout=15)
    print("SET TEMP RESPONSE STATUS:", r.status_code)
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
