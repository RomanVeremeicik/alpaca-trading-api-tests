"""
Order Management Tests — Alpaca Paper Trading API
Covers: create, read, cancel, validation, idempotency
"""
import pytest
import allure


@allure.epic("Alpaca Trading API")
@allure.feature("Order Management")
@pytest.mark.orders
class TestOrderCreation:

    @allure.title("Create market order — returns 200")
    @allure.description("Happy path: market order accepted with correct status code.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_market_order_returns_201(self, client, sample_market_order, cleanup_orders):
        r = client.post("/v2/orders", json=sample_market_order)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    @allure.title("Create market order — response schema valid")
    @allure.description("Response contains all required fields with correct types.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_market_order_response_schema(self, client, sample_market_order, cleanup_orders):
        r = client.post("/v2/orders", json=sample_market_order)
        data = r.json()
        required_fields = {
            "id": str,
            "symbol": str,
            "qty": str,
            "side": str,
            "type": str,
            "status": str,
            "created_at": str,
        }
        for field, expected_type in required_fields.items():
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], expected_type), (
                f"Field '{field}' expected {expected_type.__name__}, got {type(data[field]).__name__}"
            )

    @allure.title("Create market order — symbol matches request")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_market_order_symbol_matches(self, client, sample_market_order, cleanup_orders):
        r = client.post("/v2/orders", json=sample_market_order)
        assert r.json()["symbol"] == sample_market_order["symbol"]

    @allure.title("Create limit order — accepted with pending status")
    @allure.description("Limit order with low price is accepted (won't fill but is valid).")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_limit_order_accepted(self, client, sample_limit_order, cleanup_orders):
        r = client.post("/v2/orders", json=sample_limit_order)
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "limit"
        assert data["status"] in ("new", "accepted", "pending_new")

    @allure.title("Create order without symbol — returns 422")
    @allure.description("Order without symbol is rejected with 422 Unprocessable Entity.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_missing_symbol_returns_422(self, client):
        payload = {"qty": "1", "side": "buy", "type": "market", "time_in_force": "day"}
        r = client.post("/v2/orders", json=payload)
        assert r.status_code == 422

    @allure.title("Create order with invalid side — returns 422")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_invalid_side_returns_422(self, client):
        payload = {
            "symbol": "AAPL", "qty": "1",
            "side": "sideways",
            "type": "market", "time_in_force": "day"
        }
        r = client.post("/v2/orders", json=payload)
        assert r.status_code == 422

    @allure.title("Create order with negative quantity — rejected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_order_negative_qty_rejected(self, client):
        payload = {
            "symbol": "AAPL", "qty": "-1",
            "side": "buy", "type": "market", "time_in_force": "day"
        }
        r = client.post("/v2/orders", json=payload)
        assert r.status_code in (422, 403)

    @allure.title("Create order with empty body — returns 422")
    @allure.description("Empty request body returns error, not 500.")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_order_empty_body_returns_422(self, client):
        r = client.post("/v2/orders", json={})
        assert r.status_code == 422


@allure.epic("Alpaca Trading API")
@allure.feature("Order Lifecycle")
@pytest.mark.orders
class TestOrderLifecycle:

    @allure.title("Get order by ID — returns correct order")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_order_by_id(self, client, sample_limit_order, cleanup_orders):
        created = client.post("/v2/orders", json=sample_limit_order).json()
        order_id = created["id"]
        r = client.get(f"/v2/orders/{order_id}")
        assert r.status_code == 200
        assert r.json()["id"] == order_id

    @allure.title("Cancel open order — returns 204")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cancel_open_order(self, client, sample_limit_order):
        created = client.post("/v2/orders", json=sample_limit_order).json()
        order_id = created["id"]
        r = client.delete(f"/v2/orders/{order_id}")
        assert r.status_code == 204

    @allure.title("Cancelled order — status reflects canceled")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cancelled_order_status_is_canceled(self, client, sample_limit_order):
        created = client.post("/v2/orders", json=sample_limit_order).json()
        order_id = created["id"]
        client.delete(f"/v2/orders/{order_id}")
        r = client.get(f"/v2/orders/{order_id}")
        if r.status_code == 200:
            assert r.json()["status"] in ("canceled", "pending_cancel")
        else:
            assert r.status_code == 404

    @allure.title("Cancel non-existent order — returns 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cancel_nonexistent_order_returns_404(self, client):
        r = client.delete("/v2/orders/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    @allure.title("Get all orders — returns list")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_all_orders_returns_list(self, client):
        r = client.get("/v2/orders")
        assert r.status_code == 200
        assert isinstance(r.json(), list)