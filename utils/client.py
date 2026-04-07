import requests
import os
import logging

BASE_URL = "https://paper-api.alpaca.markets"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class AlpacaClient:
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

    def _log(self, method: str, path: str, response: requests.Response):
        logger.info(f"{method} {path} → {response.status_code}")

    def get(self, path: str, **kwargs) -> requests.Response:
        r = self.session.get(f"{self.base_url}{path}", **kwargs)
        self._log("GET", path, r)
        return r

    def post(self, path: str, **kwargs) -> requests.Response:
        r = self.session.post(f"{self.base_url}{path}", **kwargs)
        self._log("POST", path, r)
        return r

    def delete(self, path: str, **kwargs) -> requests.Response:
        r = self.session.delete(f"{self.base_url}{path}", **kwargs)
        self._log("DELETE", path, r)
        return r

    def patch(self, path: str, **kwargs) -> requests.Response:
        r = self.session.patch(f"{self.base_url}{path}", **kwargs)
        self._log("PATCH", path, r)
        return r