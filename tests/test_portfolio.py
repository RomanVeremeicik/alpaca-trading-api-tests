"""
Portfolio & Account Tests — Alpaca Paper Trading API
Covers: account info, positions, buying power, schema validation
"""
import pytest
import allure


@allure.epic("Alpaca Trading API")
@allure.feature("Account")
@pytest.mark.portfolio
class TestAccount:

    @allure.title("Get account — returns 200")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_account_returns_200(self, client):
        r = client.get("/v2/account")
        assert r.status_code == 200

    @allure.title("Account schema — all required financial fields present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_account_schema(self, client):
        data = client.get("/v2/account").json()
        required = ["id", "status", "currency", "buying_power",
                    "portfolio_value", "equity", "cash"]
        for field in required:
            assert field in data, f"Missing account field: {field}"

    @allure.title("Account currency — is USD")
    @allure.severity(allure.severity_level.NORMAL)
    def test_account_currency_is_usd(self, client):
        data = client.get("/v2/account").json()
        assert data["currency"] == "USD"

    @allure.title("Account status — is ACTIVE")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_account_status_is_active(self, client):
        data = client.get("/v2/account").json()
        assert data["status"] == "ACTIVE"

    @allure.title("Buying power — is non-negative number")
    @allure.severity(allure.severity_level.NORMAL)
    def test_buying_power_is_positive_number(self, client):
        data = client.get("/v2/account").json()
        buying_power = float(data["buying_power"])
        assert buying_power >= 0


@allure.epic("Alpaca Trading API")
@allure.feature("Positions")
@pytest.mark.portfolio
class TestPositions:

    @allure.title("Get positions — returns list")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_positions_returns_list(self, client):
        r = client.get("/v2/positions")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @allure.title("Get non-existent position — returns 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_nonexistent_position_returns_404(self, client):
        r = client.get("/v2/positions/ZZZZ")
        assert r.status_code == 404

    @allure.title("Position schema — all required fields present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_position_schema_when_exists(self, client, sample_market_order, cleanup_orders):
        client.post("/v2/orders", json=sample_market_order)
        positions = client.get("/v2/positions").json()
        if not positions:
            pytest.skip("No positions available — market may be closed")
        pos = positions[0]
        for field in ["symbol", "qty", "market_value", "avg_entry_price", "side"]:
            assert field in pos, f"Missing position field: {field}"
