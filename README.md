# Alpaca Trading API — Test Suite

API test suite for [Alpaca Markets](https://alpaca.markets) paper trading platform.  
Built as a portfolio project to demonstrate QA engineering skills in a **fintech/trading domain**.

---

## What's covered

| Module | Tests | What's tested |
|---|---|---|
| `test_orders.py` | 13 | Order creation, schema validation, lifecycle, error handling |
| `test_portfolio.py` | 8 | Account info, positions, schema, edge cases |
| `test_market_data.py` | 5 | OHLCV bars, latest quotes, data integrity, invalid symbols |
| `test_websocket.py` | 5 | WS handshake, auth, subscription, message schema |
| **Total** | **~25** | |

---

## Tech stack

- **Python 3.11+**
- **pytest** — test runner with markers and fixtures
- **requests** — REST API calls
- **websocket-client** — WebSocket streaming tests
- **Alpaca Paper Trading API** — no real money, free account

---

## Project structure

```
alpaca-trading-api-tests/
├── conftest.py              # Shared fixtures, session-scoped client
├── pytest.ini               # Markers, output settings
├── requirements.txt
├── .env.example             # Credentials template
├── utils/
│   └── client.py            # Alpaca HTTP client wrapper
└── tests/
    ├── test_orders.py       # Order management (13 tests)
    ├── test_portfolio.py    # Account & positions (8 tests)
    ├── test_market_data.py  # Market data REST (5 tests)
    └── test_websocket.py    # WebSocket streaming (5 tests)
```

---

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/YOUR_USERNAME/alpaca-trading-api-tests.git
cd alpaca-trading-api-tests
pip install -r requirements.txt
```

**2. Get free paper trading API keys**

Sign up at [alpaca.markets](https://alpaca.markets) → Paper Trading → API Keys (free, no credit card).

**3. Set credentials**

```bash
cp .env.example .env
# Edit .env with your keys
export ALPACA_API_KEY=your_key
export ALPACA_SECRET_KEY=your_secret
```

---

## Running tests

```bash
# All tests
pytest

# By category
pytest -m orders
pytest -m portfolio
pytest -m market
pytest -m websocket

# Verbose with full output
pytest -v --tb=long

# Skip WebSocket (if running in CI without network)
pytest -m "not websocket"
```

---
## Performance Testing (k6)

Install k6: https://k6.io/docs/getting-started/installation/
```bash
# Smoke test
k6 run -e ALPACA_API_KEY=$ALPACA_API_KEY -e ALPACA_SECRET_KEY=$ALPACA_SECRET_KEY performance/smoke_test.js

# Load test
k6 run -e ALPACA_API_KEY=$ALPACA_API_KEY -e ALPACA_SECRET_KEY=$ALPACA_SECRET_KEY performance/load_test.js
```
## Key test patterns demonstrated

**Schema validation** — every response is checked for required fields and types, not just status codes:
```python
def test_account_schema(self, client):
    data = client.get("/v2/account").json()
    for field in ["id", "status", "currency", "buying_power", "equity"]:
        assert field in data
```

**Data integrity** — business logic assertions beyond HTTP layer:
```python
def test_ohlcv_high_gte_low(self, data_headers):
    for bar in bars:
        assert float(bar["h"]) >= float(bar["l"])
```

**Error path coverage** — 4xx responses explicitly tested with clear assertions:
```python
def test_cancel_nonexistent_order_returns_404(self, client):
    r = client.delete("/v2/orders/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
```

**WebSocket lifecycle** — connection → auth → subscribe → message schema:
```python
def test_websocket_auth_success(self):
    # connects, sends auth, asserts 'success' message received
```

**Fixture-based cleanup** — orders cancelled automatically after each test:
```python
@pytest.fixture
def cleanup_orders(client):
    yield
    client.delete("/v2/orders")  # teardown
```

---

## Notes

- All tests run against **paper trading** — no real money involved
- WebSocket tests use the **crypto stream** (BTC/USD) which is available 24/7
- Stock market data tests may skip on weekends/holidays if no bars are returned
- `pytest.skip()` is used gracefully for market-hours-dependent scenarios

# Alpaca Trading API — Test Suite

![CI](https://github.com/RomanVeremeicik/alpaca-trading-api-tests/actions/workflows/tests.yml/badge.svg)
---

## Author

Roman — Senior QA Engineer  
[GitHub](https://github.com/YOUR_USERNAME) · [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
