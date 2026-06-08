"""Tests for the DogeAnalytics reporting layer.

Uses an injected mock-transport client (`DogeAnalytics(client=...)`) so nothing hits
the network. The combined path-dispatch handler serves all three savings endpoints.
"""

from __future__ import annotations

import httpx
import pytest

from pydoge_api import DogeAnalytics


def _savings_handler(grants_payload, contracts_payload, leases_payload):
    payloads = {
        "/savings/grants": grants_payload,
        "/savings/contracts": contracts_payload,
        "/savings/leases": leases_payload,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payloads[request.url.path])

    return handler


@pytest.fixture
def analytics(client_factory, grants_payload, contracts_payload, leases_payload):
    client = client_factory(_savings_handler(grants_payload, contracts_payload, leases_payload))
    return DogeAnalytics(client=client)


def test_top_agencies_by_savings(analytics):
    top = analytics.top_agencies_by_savings()
    assert list(top.columns) == ["Agency", "Total Savings"]
    assert top.iloc[0]["Agency"] == "NASA"
    assert top.iloc[0]["Total Savings"] == 40.0


def test_lease_area_summary(analytics):
    summary = analytics.lease_area_summary()
    assert list(summary.columns) == ["Agency", "Total Square Feet"]
    assert summary.iloc[0]["Total Square Feet"] == 1000.0


def test_top_contracts_by_value(analytics):
    df = analytics.top_contracts_by_value()
    assert "piid" in df.columns
    assert df.iloc[0]["value"] == 500.0


def test_top_agencies_by_contracts(analytics):
    df = analytics.top_agencies_by_contracts()
    assert "agency" in df.columns
    assert "savings" in df.columns


def test_export_dataset(analytics, tmp_path):
    df = analytics.top_agencies_by_savings()
    path = analytics.export_dataset(df, str(tmp_path / "top"), format="csv")
    assert path.exists()
    assert path.suffix == ".csv"


def test_requires_handle_response(client_factory, grants_payload):
    client = client_factory(lambda r: httpx.Response(200, json=grants_payload))
    with pytest.raises(ValueError):
        DogeAnalytics(client=client, handle_response=False)


def test_injected_client_not_closed(client_factory, grants_payload, contracts_payload, leases_payload):
    client = client_factory(_savings_handler(grants_payload, contracts_payload, leases_payload))
    with DogeAnalytics(client=client) as da:
        da.top_agencies_by_savings()
    # Reused client is the caller's responsibility — analytics must not close it.
    assert client.client.is_closed is False
