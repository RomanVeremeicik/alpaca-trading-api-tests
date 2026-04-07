"""
Market Data Tests — Alpaca Paper Trading API
Covers: latest quotes, bars (OHLCV), invalid symbols, data types
Uses Alpaca Data API v2 (separate base URL).
"""
import pytest
import requests
import allure
import os
from datetime import datetime, timedelta, timezone

DATA_URL = "https://data.alpaca.markets"

@pytest.fixture(scope="module")
def data_headers():
    return {
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY", ""),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY", ""),
    }


@allure.epic("Alpaca Trading API")
@allure.feature("Market Data")
@pytest.mark.market
class TestMarketData:

    @allure.title("Latest quote AAPL — returns 200 with bid/ask")
    @allure.description("Latest quote for AAPL returns 200 and contains bid/ask.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_latest_quote_aapl(self, data_headers):
        r = requests.get(
            f"{DATA_URL}/v2/stocks/AAPL/quotes/latest",
            headers=data_headers
        )
        assert r.status_code == 200
        data = r.json()
        assert "quote" in data
        quote = data["quote"]
        assert "ap" in quote, "Missing ask price (ap)"
        assert "bp" in quote, "Missing bid price (bp)"

    @allure.title("Quote prices AAPL — ask and bid are positive")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_quote_prices_are_positive(self, data_headers):
        r = requests.get(
            f"{DATA_URL}/v2/stocks/AAPL/quotes/latest",
            headers=data_headers
        )
        quote = r.json()["quote"]
        assert float(quote["ap"]) > 0, "Ask price must be > 0"
        assert float(quote["bp"]) > 0, "Bid price must be > 0"

    @allure.title("OHLCV bars TSLA — schema contains all required fields")
    @allure.description("Daily bars for TSLA include Open, High, Low, Close, Volume.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_bars_ohlcv_schema(self, data_headers):
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)
        r = requests.get(
            f"{DATA_URL}/v2/stocks/TSLA/bars",
            headers=data_headers,
            params={
                "timeframe": "1Day",
                "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "limit": 5,
            }
        )
        if r.status_code == 403:
            pytest.skip("Bars endpoint requires paid subscription")
        assert r.status_code == 200
        bars = r.json().get("bars", [])
        if not bars:
            pytest.skip("No bars returned — likely weekend/holiday range")
        bar = bars[0]
        for field in ["o", "h", "l", "c", "v", "t"]:
            assert field in bar, f"Missing OHLCV field: {field}"

    @allure.title("OHLCV data integrity — high always >= low")
    @allure.description("High price must always be >= Low price in any bar.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ohlcv_high_gte_low(self, data_headers):
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=10)
        r = requests.get(
            f"{DATA_URL}/v2/stocks/MSFT/bars",
            headers=data_headers,
            params={
                "timeframe": "1Day",
                "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "limit": 5
            }
        )
        bars = r.json().get("bars", [])
        if not bars:
            pytest.skip("No bars returned")
        for bar in bars:
            assert float(bar["h"]) >= float(bar["l"]), (
                f"High {bar['h']} < Low {bar['l']} on {bar['t']} — data integrity error"
            )

    @allure.title("Invalid symbol — returns 4xx error")
    @allure.description("Requesting a non-existent symbol returns 4xx, not 200 with garbage.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_symbol_returns_error(self, data_headers):
        r = requests.get(
            f"{DATA_URL}/v2/stocks/INVALIDZZZ/quotes/latest",
            headers=data_headers
        )
        assert r.status_code in (400, 404, 422), (
            f"Expected 4xx for invalid symbol, got {r.status_code}"
        )