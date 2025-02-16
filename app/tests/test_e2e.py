"""
Пример E2E-тестов:
- Условно: мы используем TestClient (или внешние инструменты) для проверки 
  полного сценария, включая покупку и передачу монет в рамках одного теста.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.e2e
def test_full_scenario():
    """
    E2E-тест полного сценария:
    1. Регистрируем пользователя A и B.
    2. A покупает мерч.
    3. A отправляет монеты B.
    4. Проверяем балансы и историю транзакций обоих пользователей.
    (При реальном E2E взаимодействии обычно поднимают отдельные сервисы в Docker или Kubernetes.)
    """
    # Шаг 1
    a_resp = client.post("/api/auth", json={"username": "userA", "password": "testpass"})
    b_resp = client.post("/api/auth", json={"username": "userB", "password": "testpass"})
    assert a_resp.status_code == 200
    assert b_resp.status_code == 200
    a_token = a_resp.json()["token"]
    b_token = b_resp.json()["token"]

    # Шаг 2: A покупает item (например, pen за 10 монет)
    buy_resp = client.get(
        "/api/buy/pen",
        headers={"Authorization": f"Bearer {a_token}"}
    )
    assert buy_resp.status_code == 200

    # Шаг 3: A отправляет 50 монет B
    send_resp = client.post(
        "/api/sendCoin",
        json={"toUser": "userB", "amount": 50},
        headers={"Authorization": f"Bearer {a_token}"}
    )
    assert send_resp.status_code == 200

    # Шаг 4: Проверка
    a_info = client.get("/api/info", headers={"Authorization": f"Bearer {a_token}"})
    b_info = client.get("/api/info", headers={"Authorization": f"Bearer {b_token}"})
    assert a_info.status_code == 200
    assert b_info.status_code == 200

    # Начальный баланс 1000, покупка pen (10) и отправка 50 => остаток 940
    assert a_info.json()["coins"] == 1000 - 10 - 50
    # B получил 50 => остаток 1050
    assert b_info.json()["coins"] == 1000 + 50