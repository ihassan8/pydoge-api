"""Tests for the PaymentsAPI endpoints."""

from __future__ import annotations

import httpx

from pydoge_api.models.payments import PaymentResponse, PaymentStatisticsResponse


def test_get_payments_returns_pydantic(api_factory, payments_payload):
    api = api_factory(lambda req: httpx.Response(200, json=payments_payload))
    payments = api.payments.get_payments()
    assert isinstance(payments, PaymentResponse)
    assert payments.result.payments[0].payment_amt == 12.5
    assert payments.result.payments[0].agency_name == "HHS-ADMINISTRATION FOR COMMUNITY LIVING"


def test_payments_hits_payments_endpoint(api_factory, payments_payload):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json=payments_payload)

    api = api_factory(handler)
    api.payments.get_payments(per_page=25)
    assert seen["path"] == "/payments"
    assert seen["params"]["per_page"] == "25"


def test_payments_forwards_filters(api_factory, payments_payload):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(dict(request.url.params))
        return httpx.Response(200, json=payments_payload)

    api = api_factory(handler)
    api.payments.get_payments(filter="agency_name", filter_value="NASA", sort_by="amount")
    assert seen["filter"] == "agency_name"
    assert seen["filter_value"] == "NASA"
    assert seen["sort_by"] == "amount"


def test_payments_dict_mode(api_factory, payments_payload):
    api = api_factory(lambda req: httpx.Response(200, json=payments_payload), output_pydantic=False)
    payments = api.payments.get_payments()
    assert isinstance(payments, dict)
    assert hasattr(payments, "export")


def test_get_statistics_returns_pydantic(api_factory, payment_stats_payload):
    api = api_factory(lambda req: httpx.Response(200, json=payment_stats_payload))
    stats = api.payments.get_statistics()
    assert isinstance(stats, PaymentStatisticsResponse)
    assert stats.result.agency[0].count == 100
    assert stats.result.org_names[0].org_name.startswith("CONNECTICUT")


def test_get_statistics_hits_endpoint(api_factory, payment_stats_payload):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(200, json=payment_stats_payload)

    api = api_factory(handler)
    api.payments.get_statistics()
    assert seen["path"] == "/payments/statistics"
