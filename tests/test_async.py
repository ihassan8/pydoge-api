"""Tests for the async request helper (`_async_get`).

`asyncio_mode = "auto"` (pyproject) runs these without an explicit marker. A
`MockTransport` works for `httpx.AsyncClient` too, so these stay fully offline.
"""

from __future__ import annotations

import httpx
import pytest

from pydoge_api.client import DogeAPIRequestError
from pydoge_api.utils.async_tools import _async_get


def make_async_client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url="https://api.doge.gov",
        transport=httpx.MockTransport(handler),
    )


async def test_async_get_success():
    client = make_async_client(lambda r: httpx.Response(200, json={"ok": True}))
    try:
        assert await _async_get(client, "/x", {}) == {"ok": True}
    finally:
        await client.aclose()


async def test_async_get_retries_then_succeeds():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, json={}, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": True})

    client = make_async_client(handler)
    try:
        assert await _async_get(client, "/x", {}, max_retries=3) == {"ok": True}
        assert calls["n"] == 2
    finally:
        await client.aclose()


async def test_async_get_non_retriable_raises_typed_error():
    client = make_async_client(lambda r: httpx.Response(404, json={}))
    try:
        with pytest.raises(DogeAPIRequestError) as exc:
            await _async_get(client, "/x", {})
        assert exc.value.status_code == 404
    finally:
        await client.aclose()


async def test_async_get_exhausts_raises_typed_error():
    client = make_async_client(lambda r: httpx.Response(503, json={}, headers={"Retry-After": "0"}))
    try:
        with pytest.raises(DogeAPIRequestError) as exc:
            await _async_get(client, "/x", {}, max_retries=2)
        assert exc.value.status_code == 503
    finally:
        await client.aclose()
