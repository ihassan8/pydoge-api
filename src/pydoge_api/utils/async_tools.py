import asyncio
import random
import logging
import httpx
from ..client import DogeAPIClient

logger = logging.getLogger("pydoge_api")


def run_async(coro):
    """
    Runs a coroutine in a safe way, even inside Jupyter/Spyder event loops.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                raise RuntimeError("nest_asyncio required for async mode in interactive environments")
            return loop.run_until_complete(coro)
        return loop.run_until_complete(coro)


async def _fetch_grants_pages(endpoint: str, params, total_pages: int) -> list[dict]:
    """
    Asynchronously fetch all remaining pages of a paginated endpoint.

    Parameters
    ----------
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
    base_url = getattr(DogeAPIClient, "base_url", "https://api.doge.gov")
    results = []
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        tasks = []
        for page in range(2, total_pages + 1):
            query = params.model_dump(exclude_none=True)
            query["page"] = page
            tasks.append(_async_get(client, endpoint, query))
        results = await asyncio.gather(*tasks)
    return results


async def _async_get(client: httpx.AsyncClient, endpoint: str, params: dict) -> dict:
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

    Returns
    -------
    dict
        Parsed JSON body
    """
    max_retries = 5
    base_delay = 0.5
    retriable = {429, 500, 502, 503, 504}

    for attempt in range(1, max_retries + 1):
        try:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status not in retriable:
                raise

            retry_after = e.response.headers.get("Retry-After")
            try:
                delay = float(retry_after)
            except (TypeError, ValueError):
                jitter = random.uniform(0, 0.3)
                delay = base_delay * (2 ** (attempt - 1)) + jitter

            if attempt == max_retries:
                raise RuntimeError(f"Max async retries exceeded for {endpoint}") from e

            logger.warning(f"🔁 [Async Retry {attempt}] {endpoint} → HTTP {status}. Sleeping {delay:.2f}s")
            await asyncio.sleep(delay)
