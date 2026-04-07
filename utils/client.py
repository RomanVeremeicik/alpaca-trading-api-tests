import requests
import os


BASE_URL = "https://paper-api.alpaca.markets"


class AlpacaClient:
    """
    Thin wrapper around requests for Alpaca paper trading API.
    Reads credentials from environment variables:
        ALPACA_API_KEY
        ALPACA_SECRET_KEY
    """

    def __init__(self):
        api_key = os.getenv("ALPACA_API_KEY", "")
        secret_key = os.getenv("ALPACA_SECRET_KEY", "")

        if not api_key or not secret_key:
            raise EnvironmentError(
                "Missing ALPACA_API_KEY or ALPACA_SECRET_KEY environment variables.\n"
                "Get free paper trading keys at https://alpaca.markets"
            )

        self.session = requests.Session()
        self.session.headers.update({
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
            "Content-Type": "application/json",
        })
        self.base_url = BASE_URL

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.session.patch(f"{self.base_url}{path}", **kwargs)
