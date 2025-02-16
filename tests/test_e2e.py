import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

@pytest.mark.e2e
def test_full_scenario():
    """E2E test demonstrating a full scenario."""
    # Step 1: Authenticate user A
    a_resp = client.post("/api/auth", json={"username": "userA", "password": "testpass"})
    assert a_resp.status_code == 200
    a_token = a_resp.json()["token"]

    # Step 2: A buys an item (e.g., pen)
    buy_resp = client.get(
        "/api/buy/pen", 
        headers={"Authorization": f"Bearer {a_token}"}
    )
    assert buy_resp.status_code == 200
    assert buy_resp.json()["message"] == "pen purchased successfully."

    # Step 3: A sends coins to user B
    b_resp = client.post("/api/auth", json={"username": "userB", "password": "testpass"})
    assert b_resp.status_code == 200
    send_resp = client.post(
        "/api/sendCoin",
        json={"toUser": "userB", "amount": 50},
        headers={"Authorization": f"Bearer {a_token}"}
    )
    assert send_resp.status_code == 200

    # Step 4: Verify coin balances
    a_info = client.get("/api/info", headers={"Authorization": f"Bearer {a_token}"})
    b_token = b_resp.json()["token"]
    b_info = client.get("/api/info", headers={"Authorization": f"Bearer {b_token}"})
    assert a_info.status_code == 200
    assert b_info.status_code == 200

    # A started with 1000, bought pen (-10) and sent 50 => 940
    assert a_info.json()["coins"] == 1000 - 10 - 50
    # B started with 1000, received 50 => 1050
    assert b_info.json()["coins"] == 1000 + 50