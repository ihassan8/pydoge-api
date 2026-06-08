"""Shared fixtures for the PyDOGE API test suite.

Every test runs fully offline: a :class:`httpx.MockTransport` is injected into
``DogeAPIClient`` through its ``session=`` parameter so no request ever leaves the
process.
"""

from __future__ import annotations

from typing import Callable

import httpx
import pytest

from pydoge_api import DogeAPI
from pydoge_api.client import DogeAPIClient

# ── Sample records ──────────────────────────────────────────────────────────

GRANT = {
    "date": "2025-01-01",
    "agency": "NASA",
    "recipient": "Acme Research",
    "value": 100.0,
    "savings": 40.0,
    "link": None,
    "description": "Cancelled grant",
}

CONTRACT = {
    "piid": "X1",
    "agency": "DOD",
    "vendor": "Acme Corp",
    "value": 500.0,
    "description": None,
    "fpds_status": None,
    "fpds_link": None,
    "deleted_date": None,
    "savings": 50.0,
}

LEASE = {
    "date": "2025-01-01",
    "location": "Washington, DC",
    "sq_ft": 1000.0,
    "description": None,
    "value": 200.0,
    "savings": 80.0,
    "agency": "GSA",
}

PAYMENT = {
    "payment_date": "2025-01-02",
    "payment_amt": 12.5,
    "agency_name": "HHS-ADMINISTRATION FOR COMMUNITY LIVING",
    "award_description": "Older Americans Act Title III",
    "fain": "2501CTOAFC",
    "recipient_justification": "Payment to the Area Agencies on Aging.",
    "agency_lead_justification": "Grantee drawing federal funds under this award.",
    "org_name": "CONNECTICUT STATE DEPT OF REHABILITATION SERVICES",
    "generated_unique_award_id": "ASST_NON_2501CTOAFC_7577",
}

PAYMENT_STATISTICS = {
    "success": True,
    "result": {
        "agency": [{"agency_name": "HHS-ADMINISTRATION FOR COMMUNITY LIVING", "count": 100}],
        "request_date": [{"date": "2025-04-17", "count": 100}],
        "org_names": [{"org_name": "CONNECTICUT STATE DEPT OF REHABILITATION SERVICES", "count": 100}],
    },
}


def envelope(key: str, items: list, *, pages: int = 1, total: int | None = None) -> dict:
    """Build a standard DOGE API response envelope."""
    return {
        "success": True,
        "result": {key: items},
        "meta": {"total_results": total if total is not None else len(items), "pages": pages},
    }


# ── Payload fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def grants_payload() -> dict:
    return envelope("grants", [GRANT])


@pytest.fixture
def contracts_payload() -> dict:
    return envelope("contracts", [CONTRACT])


@pytest.fixture
def leases_payload() -> dict:
    return envelope("leases", [LEASE])


@pytest.fixture
def payments_payload() -> dict:
    return envelope("payments", [PAYMENT])


@pytest.fixture
def payment_stats_payload() -> dict:
    return dict(PAYMENT_STATISTICS)


@pytest.fixture
def grant_record() -> dict:
    return dict(GRANT)


@pytest.fixture
def make_envelope():
    """Expose the envelope builder to tests that need custom multi-page payloads."""
    return envelope


# ── Client / API factories ──────────────────────────────────────────────────

Handler = Callable[[httpx.Request], httpx.Response]


def make_session(handler: Handler) -> httpx.Client:
    """An httpx.Client whose requests are served by ``handler`` (no network)."""
    return httpx.Client(base_url="https://api.doge.gov", transport=httpx.MockTransport(handler))


@pytest.fixture
def client_factory():
    """Factory returning a DogeAPIClient backed by a mock handler; auto-closed."""
    created: list[DogeAPIClient] = []

    def _factory(handler: Handler, **kwargs) -> DogeAPIClient:
        client = DogeAPIClient(session=make_session(handler), **kwargs)
        created.append(client)
        return client

    yield _factory
    for client in created:
        client.client.close()


@pytest.fixture
def api_factory():
    """Factory returning a DogeAPI backed by a mock handler; auto-closed."""
    created: list[DogeAPI] = []

    def _factory(handler: Handler, **flags) -> DogeAPI:
        api = DogeAPI(session=make_session(handler), **flags)
        created.append(api)
        return api

    yield _factory
    for api in created:
        api.close()


@pytest.fixture
def constant_handler():
    """Build a handler that always returns the given JSON payload."""

    def _build(payload: dict, status: int = 200, headers: dict | None = None) -> Handler:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status, json=payload, headers=headers or {})

        return handler

    return _build
