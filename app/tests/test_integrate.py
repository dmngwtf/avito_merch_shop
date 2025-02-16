import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.models import User
from app.database import get_db

# Создадим тестовую БД в памяти (SQLite) или используйте PostgreSQL,
# если нужно проверить реальные интеграции (с указанными настройками)
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    """Заменяем зависимость get_db на нашу тестовую базу."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.integration
def test_auth_and_buy_item():
    """
    Интеграционный тест на сценарий покупки мерча.
    1. Регистрируем/логиним пользователя.
    2. Проверяем баланс.
    3. Покупаем товар.
    4. Проверяем, что баланс уменьшился.
    """
    response = client.post("/api/auth", json={"username": "test_user", "password": "secret"})
    assert response.status_code == 200
    token = response.json()["token"]

    # Получаем баланс
    # Авторизация через Bearer-токен
    info_resp = client.get("/api/info", headers={"Authorization": f"Bearer {token}"})
    assert info_resp.status_code == 200
    initial_coins = info_resp.json()["coins"]
    assert initial_coins == 1000  # По умолчанию

    # Покупаем мерч (cup за 20 монет)
    buy_resp = client.get("/api/buy/cup", headers={"Authorization": f"Bearer {token}"})
    assert buy_resp.status_code == 200

    # Проверяем уменьшение баланса
    info_after_buy = client.get("/api/info", headers={"Authorization": f"Bearer {token}"})
    new_coins = info_after_buy.json()["coins"]
    assert new_coins == initial_coins - 20

@pytest.mark.integration
def test_coin_sending():
    """
    Интеграционный тест на сценарий передачи монет.
    1. Регистрируем двух пользователей.
    2. Первый отправляет монеты второму.
    3. Проверяем правильность изменения балансов.
    """
    resp_user1 = client.post("/api/auth", json={"username": "user1", "password": "pwd1"})
    resp_user2 = client.post("/api/auth", json={"username": "user2", "password": "pwd2"})
    assert resp_user1.status_code == 200
    assert resp_user2.status_code == 200

    token1 = resp_user1.json()["token"]
    token2 = resp_user2.json()["token"]

    info_user1 = client.get("/api/info", headers={"Authorization": f"Bearer {token1}"})
    info_user2 = client.get("/api/info", headers={"Authorization": f"Bearer {token2}"})
    assert info_user1.status_code == 200
    assert info_user2.status_code == 200
    coins_user1_before = info_user1.json()["coins"]
    coins_user2_before = info_user2.json()["coins"]

    transfer_amount = 100
    send_resp = client.post("/api/sendCoin",
                            json={"toUser": "user2", "amount": transfer_amount},
                            headers={"Authorization": f"Bearer {token1}"})
    assert send_resp.status_code == 200

    info_user1_after = client.get("/api/info", headers={"Authorization": f"Bearer {token1}"})
    info_user2_after = client.get("/api/info", headers={"Authorization": f"Bearer {token2}"})
    coins_user1_after = info_user1_after.json()["coins"]
    coins_user2_after = info_user2_after.json()["coins"]

    assert coins_user1_after == coins_user1_before - transfer_amount
    assert coins_user2_after == coins_user2_before + transfer_amount