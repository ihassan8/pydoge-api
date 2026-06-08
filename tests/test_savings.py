"""Tests for the SavingsAPI endpoints."""

from __future__ import annotations

import httpx
import pandas as pd
import pytest

from pydoge_api.models.savings import ContractResponse, GrantResponse, LeaseResponse


def test_get_grants_returns_pydantic(api_factory, grants_payload):
    api = api_factory(lambda req: httpx.Response(200, json=grants_payload))
    grants = api.savings.get_grants(sort_by="savings")
    assert isinstance(grants, GrantResponse)
    assert grants.result.grants[0].agency == "NASA"
    assert grants.meta.total_results == 1


def test_get_grants_sends_query_params(api_factory, grants_payload):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(dict(request.url.params))
        return httpx.Response(200, json=grants_payload)

    api = api_factory(handler)
    api.savings.get_grants(sort_by="savings", sort_order="desc", per_page=50)
    assert seen["sort_by"] == "savings"
    assert seen["sort_order"] == "desc"
    assert seen["per_page"] == "50"


def test_get_contracts_returns_pydantic(api_factory, contracts_payload):
    api = api_factory(lambda req: httpx.Response(200, json=contracts_payload))
    contracts = api.savings.get_contracts()
    assert isinstance(contracts, ContractResponse)
    assert contracts.result.contracts[0].piid == "X1"


def test_get_leases_returns_pydantic(api_factory, leases_payload):
    api = api_factory(lambda req: httpx.Response(200, json=leases_payload))
    leases = api.savings.get_leases()
    assert isinstance(leases, LeaseResponse)
    assert leases.result.leases[0].location == "Washington, DC"


def test_output_dict_mode_is_exportable(api_factory, grants_payload):
    api = api_factory(lambda req: httpx.Response(200, json=grants_payload), output_pydantic=False)
    grants = api.savings.get_grants()
    assert isinstance(grants, dict)
    assert hasattr(grants, "export")  # DictExportable


def test_handle_response_false_returns_raw(api_factory, grants_payload):
    api = api_factory(lambda req: httpx.Response(200, json=grants_payload), handle_response=False)
    result = api.savings.get_grants()
    assert isinstance(result, httpx.Response)


def test_all_combines_endpoints(api_factory, grants_payload, contracts_payload, leases_payload):
    payloads = {
        "/savings/grants": grants_payload,
        "/savings/contracts": contracts_payload,
        "/savings/leases": leases_payload,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payloads[request.url.path])

    api = api_factory(handler)
    df = api.savings.all()

    assert list(df["kind"]) == ["grant", "contract", "lease"]
    assert {"agency", "savings", "value", "kind"}.issubset(df.columns)
    # Columns unique to one endpoint are present but NaN elsewhere.
    assert df.loc[df["kind"] == "grant", "recipient"].iloc[0] == "Acme Research"
    assert pd.isna(df.loc[df["kind"] == "contract", "recipient"].iloc[0])


def test_all_requires_parsed_responses(api_factory, grants_payload):
    api = api_factory(lambda req: httpx.Response(200, json=grants_payload), handle_response=False)
    with pytest.raises(TypeError):
        api.savings.all()
