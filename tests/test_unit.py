import pytest
from unittest.mock import MagicMock
from app.models import User, CoinTransaction
from app.main import MERC_ITEMS

@pytest.mark.unit
def test_user_creation():
    """
    checks if the User model is correctly initialized.
    """
    user = User(username="test_user", hashed_password="fake_hashed", coins=1000)
    assert user.username == "test_user"
    assert user.coins == 1000

@pytest.mark.unit
def test_merc_items_prices():
    """
    checks if the MERC_ITEMS dictionary is correctly initialized.
    """
    assert "t-shirt" in MERC_ITEMS
    assert MERC_ITEMS["t-shirt"] == 80
    assert "cup" in MERC_ITEMS
    assert MERC_ITEMS["cup"] == 20

@pytest.mark.unit
def test_coin_transaction_model():
    """
   checks if the CoinTransaction model is correctly initialized.
    """
    tx = CoinTransaction(from_user_id=1, to_user_id=2, amount=100)
    assert tx.from_user_id == 1
    assert tx.to_user_id == 2
    assert tx.amount == 100