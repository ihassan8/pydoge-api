"""Tests for the `pydoge` Typer CLI.

`pydoge_api.cli.DogeAPI` is patched to inject an `httpx.MockTransport` session, so the
commands run fully offline. `COLUMNS` is set wide so Rich doesn't truncate cell text.
"""

from __future__ import annotations

import httpx
import pytest
from typer.testing import CliRunner

from pydoge_api import cli
from pydoge_api.api import DogeAPI

runner = CliRunner()
WIDE = {"COLUMNS": "250"}


def _session(payloads: dict) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payloads[request.url.path])

    return httpx.Client(base_url="https://api.doge.gov", transport=httpx.MockTransport(handler))


@pytest.fixture
def patched_api(mocker, grants_payload, contracts_payload, leases_payload, payments_payload):
    payloads = {
        "/savings/grants": grants_payload,
        "/savings/contracts": contracts_payload,
        "/savings/leases": leases_payload,
        "/payments": payments_payload,
    }

    def factory(**kwargs):
        return DogeAPI(session=_session(payloads), **kwargs)

    mocker.patch("pydoge_api.cli.DogeAPI", side_effect=factory)
    return payloads


def test_grants_preview(patched_api):
    result = runner.invoke(cli.app, ["grants", "--limit", "5"], env=WIDE)
    assert result.exit_code == 0
    assert "NASA" in result.output


def test_contracts_summary(patched_api):
    result = runner.invoke(cli.app, ["contracts", "--summary"], env=WIDE)
    assert result.exit_code == 0
    assert "PyDoge Data Summary" in result.output


def test_payments_filter(patched_api):
    result = runner.invoke(cli.app, ["payments", "--filter", "agency_name", "--filter-value", "NASA"], env=WIDE)
    assert result.exit_code == 0
    assert "HHS" in result.output


def test_all_combined(patched_api):
    result = runner.invoke(cli.app, ["all", "--no-fetch-all"], env=WIDE)
    assert result.exit_code == 0
    assert "grant" in result.output
    assert "lease" in result.output


def test_export_writes_file(patched_api, tmp_path):
    out = str(tmp_path / "grants")
    result = runner.invoke(cli.app, ["grants", "--export", "csv", "--out", out], env=WIDE)
    assert result.exit_code == 0
    assert "Saved" in result.output
    assert list(tmp_path.glob("grants_*.csv"))


def test_all_export_writes_file(patched_api, tmp_path):
    out = str(tmp_path / "combined")
    result = runner.invoke(cli.app, ["all", "--export", "json", "--out", out], env=WIDE)
    assert result.exit_code == 0
    assert list(tmp_path.glob("combined_*.json"))


def test_version():
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip()


def test_no_args_shows_help():
    result = runner.invoke(cli.app, [])
    # Typer exits with code 2 when it shows help because no command was given.
    assert result.exit_code in (0, 2)
    assert "Usage" in result.output
