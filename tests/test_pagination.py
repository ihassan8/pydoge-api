"""Tests for the shared pagination logic (sync path)."""

from __future__ import annotations

import httpx


def test_sync_pagination_merges_pages(api_factory, grant_record, make_envelope):
    g1 = {**grant_record, "recipient": "Recipient 1"}
    g2 = {**grant_record, "recipient": "Recipient 2"}

    def handler(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("page", "1")
        item = g2 if page == "2" else g1
        return httpx.Response(200, json=make_envelope("grants", [item], pages=2, total=2))

    api = api_factory(handler, fetch_all=True)
    grants = api.savings.get_grants()

    recipients = [g.recipient for g in grants.result.grants]
    assert recipients == ["Recipient 1", "Recipient 2"]
    # meta is patched to reflect the merged collection.
    assert grants.meta.total_results == 2


def test_no_pagination_when_fetch_all_false(api_factory, grant_record, make_envelope):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json=make_envelope("grants", [grant_record], pages=2, total=2))

    api = api_factory(handler, fetch_all=False)
    grants = api.savings.get_grants()

    assert len(grants.result.grants) == 1
    assert calls["n"] == 1  # only the first page was requested


def test_no_extra_request_for_single_page(api_factory, grant_record, make_envelope):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, json=make_envelope("grants", [grant_record], pages=1, total=1))

    api = api_factory(handler, fetch_all=True)
    api.savings.get_grants()
    assert calls["n"] == 1
