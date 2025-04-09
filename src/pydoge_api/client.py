import httpx
import time
import logging
from .config import BASE_URL, TIMEOUT

logger = logging.getLogger("doge_api")
logger.setLevel(logging.INFO)

class DogeAPIClient:
    def __init__(self, base_url=BASE_URL, timeout=TIMEOUT, max_retries=5):
        self.client = httpx.Client(base_url=base_url, timeout=timeout)
        self.max_retries = max_retries

    def get(self, endpoint: str, params: dict = None, handle_response=True):
        retries = 0
        while retries <= self.max_retries:
            response = self.client.get(endpoint, params=params or {})
            logger.info(f"GET {endpoint} | {response.status_code}")
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_time = int(retry_after) if retry_after else 2 ** retries
                logger.warning(f"429 Rate Limit hit. Retrying in {wait_time}s (attempt {retries + 1})")
                time.sleep(wait_time)
                retries += 1
                continue
            response.raise_for_status()
            return response if not handle_response else response.json()

        logger.error(f"Max retries exceeded on endpoint {endpoint}")
        raise httpx.HTTPStatusError("429 Rate limit hit too many times", request=response.request, response=response)

