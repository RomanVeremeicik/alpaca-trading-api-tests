# Alpaca Trading API — Test Suite

![CI](https://github.com/RomanVeremeicik/alpaca-trading-api-tests/actions/workflows/tests.yml/badge.svg)

API test suite for [Alpaca Markets](https://alpaca.markets) paper trading platform.  
Built as a portfolio project to demonstrate QA engineering skills in a **fintech/trading domain**.

> **Why this project?** Most QA portfolios test todo apps or demo sites. This project tests a real financial API — orders, positions, market data, and WebSocket streaming — the same patterns used in production fintech systems.

---

## What's covered

| Module | Tests | What's tested |
|---|---|---|
| `test_orders.py` | 13 | Order creation, schema validation, lifecycle, error handling |
| `test_portfolio.py` | 8 | Account info, positions, schema, edge cases |
| `test_market_data.py` | 9 | OHLCV bars, latest quotes, data integrity, parametrized symbols |
| `test_websocket.py` | 5 | WS handshake, auth, subscription, message schema |
| **Total** | **35** | |

---

## Tech stack

- **Python 3.11+**
- **pytest** — test runner with markers, fixtures, parametrize
- **requests** — REST API calls
- **websocket-client** — WebSocket streaming tests
- **Allure** — visual test reporting
- **k6** — performance and load testing
- **Docker** — containerized test execution
- **GitHub Actions** — CI/CD pipeline
- **Alpaca Paper Trading API** — no real money, free account

---

## Project structure
alpaca-trading-api-tests/
├── .github/workflows/
│   └── tests.yml            # GitHub Actions CI
├── tests/
│   ├── test_orders.py       # Order management (13 tests)
│   ├── test_portfolio.py    # Account & positions (8 tests)
│   ├── test_market_data.py  # Market data REST (9 tests)
│   └── test_websocket.py    # WebSocket streaming (5 tests)
├── utils/
│   └── client.py            # Alpaca HTTP client with logging
├── performance/
│   ├── smoke_test.js        # k6 smoke test
│   └── load_test.js         # k6 load test (5 VUs, 90s)
├── conftest.py              # Shared fixtures, session-scoped client
├── pytest.ini               # Markers, output settings
├── Dockerfile               # Container for test execution
├── docker-compose.yml       # Docker Compose setup
└── requirements.txt

---

## Setup

**1. Clone and install dependencies**
```bash
git clone https://github.com/RomanVeremeicik/alpaca-trading-api-tests.git
cd alpaca-trading-api-tests
pip install -r requirements.txt
```

**2. Get free paper trading API keys**

Sign up at [alpaca.markets](https://alpaca.markets) → Paper Trading → API Keys (free, no credit card).

**3. Set credentials**
```bash
cp env.example .env
# Edit .env with your keys
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

# Verbose
pytest -v --tb=long

# Via Docker
docker compose up --build
```

---

## Allure Report
```bash
pytest
allure serve allure-results
```

---

## Performance Testing (k6)
```bash
# Smoke test
k6 run -e ALPACA_API_KEY=$ALPACA_API_KEY -e ALPACA_SECRET_KEY=$ALPACA_SECRET_KEY performance/smoke_test.js

# Load test (5 VUs, ramp up → steady → ramp down)
k6 run -e ALPACA_API_KEY=$ALPACA_API_KEY -e ALPACA_SECRET_KEY=$ALPACA_SECRET_KEY performance/load_test.js
```

**Thresholds:**
- p95 latency < 2000ms
- error rate < 5%

---

## Key test patterns

**Schema validation** — fields and types, not just status codes:
```python
for field, expected_type in required_fields.items():
    assert field in data
    assert isinstance(data[field], expected_type)
```

**Data integrity** — business logic assertions:
```python
for bar in bars:
    assert float(bar["h"]) >= float(bar["l"])  # high always >= low
```

**Parametrized coverage** — multiple symbols in one test:
```python
@pytest.mark.parametrize("symbol", ["AAPL", "TSLA", "MSFT", "GOOGL"])
def test_multiple_symbols_return_quotes(self, data_headers, symbol):
    ...
```

**Error path coverage** — 4xx explicitly tested:
```python
def test_cancel_nonexistent_order_returns_404(self, client):
    r = client.delete("/v2/orders/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
```

**Fixture-based cleanup** — automatic teardown:
```python
@pytest.fixture
def cleanup_orders(client):
    yield
    client.delete("/v2/orders")
```

**WebSocket lifecycle** — connect → auth → subscribe → schema:
```python
def test_websocket_auth_success(self):
    # sends auth payload, asserts 'success' message received
```

---

## Notes

- All tests run against **paper trading** — no real money involved
- WebSocket tests use **crypto stream** (BTC/USD) — available 24/7
- Market data tests skip gracefully on weekends/holidays
- Bars endpoint requires paid Alpaca subscription — skipped automatically

---

## Author

Roman — Senior QA Engineer  
[GitHub](https://github.com/RomanVeremeicik) · [LinkedIn](https://www.linkedin.com/in/roman-veremeicik/)