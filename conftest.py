import pytest
import requests
import os
from dotenv import load_dotenv
from utils.client import AlpacaClient

load_dotenv()

def pytest_configure(config):
    config.addinivalue_line("markers", "orders: Order management tests")
    config.addinivalue_line("markers", "portfolio: Portfolio and positions tests")
    config.addinivalue_line("markers", "market: Market data tests")
    config.addinivalue_line("markers", "websocket: WebSocket streaming tests")


@pytest.fixture(scope="session")
def client():
    """Shared Alpaca paper trading client for entire test session."""
    return AlpacaClient()


@pytest.fixture(scope="session")
def account(client):
    """Fetch account info once per session."""
    return client.get("/v2/account").json()


@pytest.fixture
def cleanup_orders(client):
    """Cancel all open orders after each test that creates them."""
    yield
    client.delete("/v2/orders")


@pytest.fixture
def sample_market_order():
    return {
        "symbol": "AAPL",
        "qty": "1",
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
    }


@pytest.fixture
def sample_limit_order():
    return {
        "symbol": "TSLA",
        "qty": "1",
        "side": "buy",
        "type": "limit",
        "limit_price": "1.00",  # Very low — won't fill in paper trading
        "time_in_force": "gtc",
    }
