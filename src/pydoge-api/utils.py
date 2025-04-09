import asyncio
import httpx

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
            return asyncio.ensure_future(coro)
        return loop.run_until_complete(coro)


async def _fetch_grants_pages(endpoint, params_obj, total_pages):
    async with httpx.AsyncClient(base_url="https://api.doge.gov") as client:
        tasks = []
        for p in range(2, total_pages + 1):
            params_obj.page = p
            clean_query = params_obj.model_dump(exclude_none=True)
            tasks.append(client.get(endpoint, params=clean_query))
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]