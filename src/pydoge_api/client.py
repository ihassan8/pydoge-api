import random
import time
from typing import Optional, Union

import httpx

from ._logging import logger
from .config import BASE_URL, TIMEOUT


class DogeAPIRequestError(Exception):
    """Raised when a request fails after all retries."""

    def __init__(self, method: str, url: str, status_code: int, message: str):
        self.method = method
        self.url = url
        self.status_code = status_code
        super().__init__(f"[{status_code}] {method} {url} failed: {message}")


class DogeAPIClient:
    """
    DOGE API client with built-in retry logic for unstable endpoints.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = TIMEOUT,
        session: Optional[httpx.Client] = None,
        max_retries: int = 5,
        backoff_factor: float = 1.5,
        max_backoff: float = 60.0,
        **httpx_kwargs,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff

        if session:
            if not isinstance(session, httpx.Client):
                raise TypeError("Custom session must be an instance of httpx.Client")
            self.client = session
            self._owns_session = False
        else:
            self.client = httpx.Client(base_url=base_url, timeout=timeout, **httpx_kwargs)
            self._owns_session = True

    def rest_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Perform a REST request with retry logic for 429 and 5xx errors.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.)
        url : str
            Full target URL.
        **kwargs : dict
            Passed to httpx.request() (params, json, data, headers, etc.)

        Returns
        -------
        httpx.Response
            Response object, or raises DogeAPIRequestError.
        """
        retriable = {429, 500, 502, 503, 504}
        retries = 0

        while retries <= self.max_retries:
            try:
                logger.debug(f"→ {method} {url} params={kwargs.get('params') or {}}")
                response = self.client.request(method, url, **kwargs)
                logger.debug(f"← {response.status_code} {method} {url} ({len(response.content)} bytes)")
                if response.status_code < 400:
                    return response
                if response.status_code not in retriable:
                    # Non-retriable client/server error (400, 401, 403, 404, ...):
                    # surface a clear, typed error instead of returning the body.
                    raise DogeAPIRequestError(
                        method, url, response.status_code, response.text[:200] or "Request failed"
                    )
            except httpx.RequestError as e:
                logger.warning(f"⚠️ Network error during {method} {url}: {e}")
                err_response = getattr(e, "response", None)
                if err_response is None:
                    raise
                response = err_response

            # Retry triggered
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait = float(retry_after)
                except ValueError:
                    wait = self.backoff_factor * (retries + 1)
            else:
                jitter = random.uniform(0, 0.3)
                wait = self.backoff_factor * (2**retries) + jitter

            # Cap the wait so large retry counts can't produce multi-minute sleeps.
            wait = min(wait, self.max_backoff)

            logger.warning(
                f"🔁 Retry {retries + 1}/{self.max_retries} for {method} {url} "
                f"→ HTTP {response.status_code}. Waiting {wait:.2f}s..."
            )
            time.sleep(wait)
            retries += 1

        logger.error(f"❌ {method} {url} failed after {self.max_retries} retries.")
        raise DogeAPIRequestError(method, url, response.status_code, "Max retries exceeded")

    def get(self, endpoint: str, params: Optional[dict] = None, decode: bool = True) -> Union[dict, httpx.Response]:
        url = f"{self.base_url}{endpoint}"
        response = self.rest_request("GET", url, params=params)
        return response.json() if decode else response

    def post(
        self,
        endpoint: str,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        decode: bool = True,
    ) -> Union[dict, httpx.Response]:
        url = f"{self.base_url}{endpoint}"
        response = self.rest_request("POST", url, data=data, json=json)
        return response.json() if decode else response

    def close(self):
        if self._owns_session:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
