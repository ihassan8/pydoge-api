"""Tests for DogeAPIClient retry logic and lifecycle."""

from __future__ import annotations

import httpx
import pytest

from pydoge_api.client import DogeAPIClient, DogeAPIRequestError


def test_get_decodes_json(client_factory, grants_payload):
    client = client_factory(lambda req: httpx.Response(200, json=grants_payload))
    result = client.get("/savings/grants")
    assert result == grants_payload


def test_get_raw_response_when_not_decoding(client_factory, grants_payload):
    client = client_factory(lambda req: httpx.Response(200, json=grants_payload))
    result = client.get("/savings/grants", decode=False)
    assert isinstance(result, httpx.Response)
    assert result.status_code == 200


def test_retries_on_429_then_succeeds(client_factory, grants_payload):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            # Retry-After "0" keeps the test fast.
            return httpx.Response(429, json={}, headers={"Retry-After": "0"})
        return httpx.Response(200, json=grants_payload)

    client = client_factory(handler, max_retries=3)
    result = client.get("/savings/grants")
    assert result == grants_payload
    assert calls["n"] == 2


def test_retries_on_5xx(client_factory, grants_payload):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] <= 2:
            return httpx.Response(503, json={}, headers={"Retry-After": "0"})
        return httpx.Response(200, json=grants_payload)

    client = client_factory(handler, max_retries=5)
    assert client.get("/savings/grants") == grants_payload
    assert calls["n"] == 3


def test_raises_after_max_retries(client_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={}, headers={"Retry-After": "0"})

    client = client_factory(handler, max_retries=2)
    with pytest.raises(DogeAPIRequestError) as exc:
        client.get("/savings/grants")
    assert exc.value.status_code == 500
    assert exc.value.method == "GET"


def test_non_retriable_4xx_raises(client_factory):
    # 404 is not retriable, so it surfaces as a typed error rather than the body.
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404, json={"detail": "nope"})

    client = client_factory(handler, max_retries=3)
    with pytest.raises(DogeAPIRequestError) as exc:
        client.get("/savings/grants")
    assert exc.value.status_code == 404
    assert calls["n"] == 1  # not retried


def test_backoff_is_capped(client_factory, mocker):
    slept = []
    mocker.patch("pydoge_api.client.time.sleep", side_effect=lambda s: slept.append(s))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={})  # no Retry-After -> computed backoff

    client = client_factory(handler, max_retries=4, backoff_factor=100.0, max_backoff=2.0)
    with pytest.raises(DogeAPIRequestError):
        client.get("/savings/grants")
    assert slept  # retries did sleep
    assert all(s <= 2.0 for s in slept)


def test_custom_session_type_is_validated():
    with pytest.raises(TypeError):
        DogeAPIClient(session="not-an-httpx-client")


def test_owned_session_closed_on_exit():
    with DogeAPIClient() as client:
        inner = client.client
    assert inner.is_closed


def test_injected_session_not_closed_on_exit():
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
    session = httpx.Client(base_url="https://api.doge.gov", transport=transport)
    with DogeAPIClient(session=session) as client:
        assert client._owns_session is False
    assert session.is_closed is False
    session.close()
