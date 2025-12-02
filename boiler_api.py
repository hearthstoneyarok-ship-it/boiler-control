import requests
import sys
import os

LOGIN = os.getenv("STOUT_LOGIN")
PASSWORD = os.getenv("STOUT_PASSWORD")

DEVICE_ID = "74664"
ENV_ID = 11  # отопление

AUTH_URL = "https://boiler.stout.ru/api/auth/"
DASHBOARD_URL = "https://boiler.stout.ru/api/dashboard/"


def login(session: requests.Session) -> bool:
    """
    Логинится на boiler.stout.ru так же, как это делает браузер.
    """

    if not LOGIN or not PASSWORD:
        print("❌ Переменные окружения STOUT_LOGIN / STOUT_PASSWORD не заданы")
        return False

    # Инициализирующий GET, чтобы получить PHPSESSID (как в браузере при заходе на login.php)
    try:
        init_resp = session.get("https://boiler.stout.ru/login.php", timeout=10)
        print("INIT GET /login.php STATUS:", init_resp.status_code)
    except Exception as e:
        print("Ошибка при GET /login.php:", e)

    payload = {
        "action": "login",
        "data": {
            "login": LOGIN,
            "password": PASSWORD,
            "rememberMe": False,
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://boiler.stout.ru",
        "Referer": "https://boiler.stout.ru/login.php",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }

    r = session.post(AUTH_URL, json=payload, headers=headers, timeout=10)

    print("LOGIN RESPONSE STATUS:", r.status_code)

    try:
        data = r.json()
        print("LOGIN RESPONSE JSON:", data)

        # у них, судя по предыдущим ответам, поле err = 0 при успехе
        if isinstance(data, dict) and data.get("err") == 0:
            return True

        # если формат другой — хотя бы увидим его в логе
        return False

    except Exception as e:
        print("LOGIN RESPONSE is not JSON:", type(e), e)
        print("LOGIN RESPONSE TEXT (first 500 chars):")
        print(r.text[:500])
        return False


def set_temperature(session: requests.Session, value: float) -> str:
    """
    Вызывает action=setEnvGoal на /api/dashboard/
    """

    payload = {
        "action": "setEnvGoal",
        "deviceId": DEVICE_ID,
        "data": {
            "id": ENV_ID,
            "goal": value,
            "resetMode": 0,
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://boiler.stout.ru",
        "Referer": f"https://boiler.stout.ru/dashboard/index.php?d={DEVICE_ID}",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }

    r = session.post(DASHBOARD_URL, json=payload, headers=headers, timeout=10)

    print("SET TEMP RESPONSE STATUS:", r.status_code)
    try:
        data = r.json()
        print("SET TEMP RESPONSE JSON:", data)
        return str(data)
    except Exception:
        print("SET TEMP RESPONSE TEXT (first 500 chars):")
        print(r.text[:500])
        return r.text


def main():
    if len(sys.argv) < 2:
        print("Ошибка: укажите температуру, например: python boiler_api.py 50")
        return

    try:
        value = float(sys.argv[1])
    except ValueError:
        print("Ошибка: температура должна быть числом")
        return

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
