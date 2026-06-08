"""Tests for the Pydantic request/response models."""

from __future__ import annotations

from pydoge_api.models.payments import PaymentResponse
from pydoge_api.models.savings import (
    ContractResponse,
    GrantParams,
    GrantResponse,
    LeaseResponse,
)


def test_grant_params_defaults():
    params = GrantParams()
    assert params.page == 1
    assert params.per_page == 100
    # None fields drop out of the query payload.
    assert "sort_by" not in params.model_dump(exclude_none=True)


def test_grant_params_roundtrip():
    params = GrantParams(sort_by="savings", sort_order="desc")
    dumped = params.model_dump(exclude_none=True)
    assert dumped == {"sort_by": "savings", "sort_order": "desc", "page": 1, "per_page": 100}


def test_grant_response_validates(grants_payload):
    resp = GrantResponse(**grants_payload)
    assert resp.success is True
    assert resp.result.grants[0].value == 100.0


def test_contract_response_validates(contracts_payload):
    resp = ContractResponse(**contracts_payload)
    assert resp.result.contracts[0].piid == "X1"


def test_lease_response_validates(leases_payload):
    resp = LeaseResponse(**leases_payload)
    assert resp.result.leases[0].sq_ft == 1000.0


def test_payment_response_validates(payments_payload):
    resp = PaymentResponse(**payments_payload)
    payment = resp.result.payments[0]
    assert payment.agency_name == "HHS-ADMINISTRATION FOR COMMUNITY LIVING"
    assert payment.payment_amt == 12.5
