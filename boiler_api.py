import sys
import requests
import json
import os

BASE_URL = "https://boiler.stout.ru"

LOGIN_URL = f"{BASE_URL}/login.php"
API_URL = f"{BASE_URL}/api/dashboard/"

# креды берём из GitHub Secrets
LOGIN = os.environ.get("STOUT_LOGIN")
PASSWORD = os.environ.get("STOUT_PASSWORD")

if not LOGIN or not PASSWORD:
    print("Ошибка: отсутствуют логин или пароль. Добавьте STOUT_LOGIN и STOUT_PASSWORD в GitHub Secrets.")
    sys.exit(1)

def login(session):
    """Авторизация на сайте (имитация обычного входа через форму)"""
    payload = {
        "login": LOGIN,
        "pswd": PASSWORD,
        "submit": "login"
    }

    resp = session.post(LOGIN_URL, data=payload)
    if "dashboard" not in resp.text and resp.status_code != 200:
        print("⚠️ Не удалось войти. Ответ сервера:")
        print(resp.text)
        sys.exit(1)

    print("✔ Авторизация успешна")

def set_temperature(session, temp):
    """Отправляет команду setEnvGoal"""
    payload = {
        "action": "setEnvGoal",
        "deviceId": "74664",
        "data": {
            "id": 11,
            "goal": temp,
            "resetMode": 0
        }
    }

    headers = {"Content-Type": "application/json"}

    resp = session.post(API_URL, data=json.dumps(payload), headers=headers)
    print("Ответ сервера:", resp.text)

def main():
    if len(sys.argv) < 2:
        print("Использование: python boiler_api.py <температура>")
        sys.exit(1)

    temp = float(sys.argv[1])
    print(f"Устанавливаю температуру: {temp}°C...")

    session = requests.Session()
    login(session)
    set_temperature(session, temp)

if __name__ == "__main__":
    main()
