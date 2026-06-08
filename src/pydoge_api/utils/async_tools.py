from __future__ import annotations

import asyncio
import random

import httpx

from .._logging import logger
from ..client import DogeAPIClient, DogeAPIRequestError


def run_async(coro):
    """
    Runs a coroutine in a safe way, even inside Jupyter/Spyder event loops.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # asyncio.run failed because a loop is already running (e.g. Jupyter).
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop after all — create a fresh one and drive the coroutine.
            return asyncio.new_event_loop().run_until_complete(coro)
        try:
            import nest_asyncio
        except ImportError:
            raise RuntimeError("nest_asyncio required for async mode in interactive environments")
        nest_asyncio.apply()
        return loop.run_until_complete(coro)


async def _fetch_grants_pages(client: DogeAPIClient, endpoint: str, params, total_pages: int) -> list[dict]:
    """
    Asynchronously fetch all remaining pages of a paginated endpoint.

    Parameters
    ----------
    client : DogeAPIClient
        The configured client whose ``base_url``, ``timeout`` and headers are
        reused so async pagination targets the same host/auth as the sync path.
    endpoint : str
        Endpoint to call (e.g. "/savings/grants")
    params : BaseModel
        Pydantic model with pagination/query fields
    total_pages : int
        Total number of pages to request

    Returns
    -------
    list of dict
        Each element is a page's parsed response (dict)
    """
    headers = dict(client.client.headers)
    logger.debug(f"async: requesting pages 2–{total_pages} concurrently for {endpoint}")
    async with httpx.AsyncClient(base_url=client.base_url, timeout=client.timeout, headers=headers) as async_client:
        tasks = []
        for page in range(2, total_pages + 1):
            query = params.model_dump(exclude_none=True)
            query["page"] = page
            tasks.append(_async_get(async_client, endpoint, query, max_retries=client.max_retries))
        results = await asyncio.gather(*tasks)
    return results


async def _async_get(client: httpx.AsyncClient, endpoint: str, params: dict, *, max_retries: int = 5) -> dict:
    """
    Perform GET with retry/backoff on 429/5xx for async clients.

    Parameters
    ----------
    client : AsyncClient
        Shared httpx client.
    endpoint : str
        Endpoint path (e.g. "/savings/grants")
    params : dict
        Query string parameters
    max_retries : int, default=5
        Maximum number of attempts before raising.

    Returns
    -------
    dict
        Parsed JSON body

    Raises
    ------
    DogeAPIRequestError
        On a non-retriable status, or after exhausting all retries. Mirrors the
        sync :class:`DogeAPIClient` error contract.
    """
    base_delay = 0.5
    retriable = {429, 500, 502, 503, 504}

    for attempt in range(1, max_retries + 1):
        try:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            data: dict = response.json()
            return data
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status not in retriable:
                raise DogeAPIRequestError("GET", endpoint, status, e.response.text[:200] or "Request failed") from e

            if attempt == max_retries:
                raise DogeAPIRequestError("GET", endpoint, status, "Max retries exceeded") from e

            retry_after = e.response.headers.get("Retry-After")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                jitter = random.uniform(0, 0.3)
                delay = base_delay * (2 ** (attempt - 1)) + jitter

            logger.warning(f"🔁 [Async Retry {attempt}] {endpoint} → HTTP {status}. Sleeping {delay:.2f}s")
            await asyncio.sleep(delay)

    # Unreachable: the loop either returns or raises on every path. Present so static
    # analysis sees a definite terminal statement.
    raise DogeAPIRequestError("GET", endpoint, 0, "Max retries exceeded")
