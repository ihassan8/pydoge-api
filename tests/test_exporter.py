"""Tests for ExportMixin and the dict-export helpers."""

from __future__ import annotations

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from pydoge_api.models.savings import GrantResponse
from pydoge_api.utils.exporter import DictExportable, handle_dict


def test_to_dataframe(grants_payload):
    resp = GrantResponse(**grants_payload)
    df = resp.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "agency" in df.columns


def test_to_dataframe_parses_dates_by_default(grants_payload):
    resp = GrantResponse(**grants_payload)
    df = resp.to_dataframe()
    assert is_datetime64_any_dtype(df["date"])


def test_to_dataframe_parse_dates_can_be_disabled(grants_payload):
    resp = GrantResponse(**grants_payload)
    df = resp.to_dataframe(parse_dates=False)
    # Left as raw strings (exact dtype varies across pandas versions: object/StringDtype).
    assert not is_datetime64_any_dtype(df["date"])
    assert df["date"].iloc[0] == "2025-01-01"


def test_export_csv(tmp_path, grants_payload):
    resp = GrantResponse(**grants_payload)
    path = resp.export(str(tmp_path / "grants"), format="csv")
    assert path.exists()
    assert path.suffix == ".csv"


def test_export_json(tmp_path, grants_payload):
    resp = GrantResponse(**grants_payload)
    path = resp.export(str(tmp_path / "grants"), format="json")
    assert path.exists()
    assert path.read_text().strip().startswith("[")


def test_export_rejects_unknown_format(tmp_path, grants_payload):
    resp = GrantResponse(**grants_payload)
    try:
        resp.export(str(tmp_path / "grants"), format="parquet")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for unsupported format")


def test_summary_writes_file(tmp_path, grants_payload):
    resp = GrantResponse(**grants_payload)
    out = tmp_path / "summary.md"
    resp.summary(save_as=str(out))
    assert out.exists()
    assert "PyDoge Data Summary" in out.read_text(encoding="utf-8")


def test_summary_returns_text_and_can_be_silent(capsys, grants_payload):
    resp = GrantResponse(**grants_payload)
    text = resp.summary(to_stdout=False)
    assert "PyDoge Data Summary" in text
    # Nothing printed when to_stdout=False.
    assert capsys.readouterr().out == ""


def test_handle_dict_wraps_plain_dict(grants_payload):
    wrapped = handle_dict(grants_payload)
    assert isinstance(wrapped, DictExportable)
    assert hasattr(wrapped, "export")
    # _get_collection returns the first value under "result"
    assert wrapped.to_dataframe().iloc[0]["agency"] == "NASA"
