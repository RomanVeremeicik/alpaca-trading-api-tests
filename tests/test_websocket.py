"""
WebSocket Streaming Tests — Alpaca Paper Trading API
Covers: connection handshake, authentication, subscription, message receipt

Note: these tests require market hours OR crypto stream (24/7).
Crypto stream is used here as it's always available.
"""
import pytest
import allure
import json
import os
import websocket
import threading
import time


WS_URL = "wss://stream.data.alpaca.markets/v1beta3/crypto/us"


@allure.epic("Alpaca Trading API")
@allure.feature("WebSocket Streaming")
@pytest.mark.websocket
class TestWebSocketStreaming:

    def _collect_messages(self, url, send_payloads: list, timeout: float = 5.0) -> list:
        received = []
        done = threading.Event()

        def on_open(ws):
            for payload in send_payloads:
                ws.send(json.dumps(payload))

        def on_message(ws, message):
            data = json.loads(message)
            if isinstance(data, list):
                received.extend(data)
            else:
                received.append(data)

        def on_error(ws, error):
            done.set()

        def on_close(ws, *args):
            done.set()

        ws_app = websocket.WebSocketApp(
            url,
            header=[
                f"APCA-API-KEY-ID: {os.getenv('ALPACA_API_KEY', '')}",
                f"APCA-API-SECRET-KEY: {os.getenv('ALPACA_SECRET_KEY', '')}",
            ],
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        thread = threading.Thread(target=ws_app.run_forever, daemon=True)
        thread.start()
        time.sleep(timeout)
        ws_app.close()
        return received

    @allure.title("WebSocket connection — receives 'connected' message")
    @allure.description("Server sends 'connected' message immediately on connect.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_websocket_connection_receives_connected_message(self):
        messages = self._collect_messages(WS_URL, send_payloads=[], timeout=3.0)
        msg_types = [m.get("T") for m in messages]
        assert "connected" in msg_types or "success" in msg_types, (
            f"Expected 'connected' or 'success' message, got: {msg_types}"
        )

    @allure.title("WebSocket auth — valid credentials accepted")
    @allure.description("Valid API credentials result in 'success' message.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_websocket_auth_success(self):
        auth_payload = {
            "action": "auth",
            "key": os.getenv("ALPACA_API_KEY", ""),
            "secret": os.getenv("ALPACA_SECRET_KEY", ""),
        }
        messages = self._collect_messages(WS_URL, send_payloads=[auth_payload], timeout=4.0)
        msg_types = [m.get("T") for m in messages]
        assert "success" in msg_types, (
            f"Expected 'success' (auth) message, got: {msg_types}"
        )

    @allure.title("WebSocket auth — invalid credentials rejected")
    @allure.description("Invalid credentials result in auth_timeout or error, not success.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_websocket_invalid_credentials_rejected(self):
        auth_payload = {
            "action": "auth",
            "key": "INVALID_KEY",
            "secret": "INVALID_SECRET",
        }
        received = []
        done = threading.Event()

        def on_open(ws):
            ws.send(json.dumps(auth_payload))

        def on_message(ws, message):
            data = json.loads(message)
            if isinstance(data, list):
                received.extend(data)
            else:
                received.append(data)
            if any(m.get("T") in ("error", "auth_timeout") for m in received):
                done.set()
                ws.close()

        ws_app = websocket.WebSocketApp(
            WS_URL, on_open=on_open, on_message=on_message
        )
        thread = threading.Thread(target=ws_app.run_forever, daemon=True)
        thread.start()
        done.wait(timeout=5.0)
        ws_app.close()

        msg_types = [m.get("T") for m in received]
        assert any(t in ("error", "auth_timeout") for t in msg_types), (
            f"Expected error on bad credentials, got: {msg_types}"
        )

    @allure.title("WebSocket subscription — BTC/USD quotes received")
    @allure.description("After auth, subscribing to BTC/USD quotes yields quote messages.")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_websocket_subscription_to_btc_quotes(self):
        auth = {"action": "auth",
                "key": os.getenv("ALPACA_API_KEY", ""),
                "secret": os.getenv("ALPACA_SECRET_KEY", "")}
        subscribe = {"action": "subscribe", "quotes": ["BTC/USD"]}
        messages = self._collect_messages(
            WS_URL, send_payloads=[auth, subscribe], timeout=6.0
        )
        quote_messages = [m for m in messages if m.get("T") == "q"]
        assert len(quote_messages) > 0, (
            "Expected at least one quote message for BTC/USD subscription"
        )

    @allure.title("WebSocket quote schema — all required fields present")
    @allure.description("BTC/USD quote messages contain required fields.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_websocket_quote_message_schema(self):
        auth = {"action": "auth",
                "key": os.getenv("ALPACA_API_KEY", ""),
                "secret": os.getenv("ALPACA_SECRET_KEY", "")}
        subscribe = {"action": "subscribe", "quotes": ["BTC/USD"]}
        messages = self._collect_messages(
            WS_URL, send_payloads=[auth, subscribe], timeout=6.0
        )
        quotes = [m for m in messages if m.get("T") == "q"]
        if not quotes:
            pytest.skip("No quote messages received — check connection")
        q = quotes[0]
        for field in ["S", "bp", "ap", "bs", "as", "t"]:
            assert field in q, f"Missing quote field: {field}"
        assert q["S"] == "BTC/USD"