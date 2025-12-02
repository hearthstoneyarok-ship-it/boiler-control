import requests
import sys
import os

LOGIN = os.getenv("STOUT_LOGIN")
PASSWORD = os.getenv("STOUT_PASSWORD")

DEVICE_ID = "74664"
ENV_ID = 11  # отопление

def login(session: requests.Session):
    url = "https://boiler.stout.ru/auth/"
    payload = {
        "action": "login",
        "login": LOGIN,
        "pass": PASSWORD
    }
    r = session.post(url, json=payload)

    print("LOGIN RESPONSE STATUS:", r.status_code)
    print("LOGIN RESPONSE TEXT:", r.text[:500])  # первые 500 символов

    try:
        data = r.json()
        return data.get("err") == 0
    except Exception as e:
        print("JSON decode error:", e)
        return False


def set_temperature(session: requests.Session, value: float):
    url = "https://boiler.stout.ru/api/dashboard/"
    
    payload = {
        "action": "setEnvGoal",
        "deviceId": DEVICE_ID,
        "data": {
            "id": ENV_ID,
            "goal": value,
            "resetMode": 0
        }
    }

    r = session.post(url, json=payload)
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
