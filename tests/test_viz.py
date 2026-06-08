"""Tests for the optional plotting helpers (`pydoge_api.viz`).

Skipped automatically when the ``viz`` extra (matplotlib/plotly) is not installed.
matplotlib uses the non-interactive Agg backend so nothing tries to open a window.
"""

from __future__ import annotations

import pandas as pd
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

from matplotlib.axes import Axes  # noqa: E402

from pydoge_api import viz  # noqa: E402


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"agency": "NASA", "savings": 100.0, "value": 200.0, "date": "2025-01-15", "location": "Houston, TX"},
            {"agency": "NASA", "savings": 50.0, "value": 80.0, "date": "2025-02-10", "location": "Houston, TX"},
            {"agency": "DOD", "savings": 300.0, "value": 400.0, "date": "2025-01-20", "location": "Arlington, VA"},
            {"agency": "GSA", "savings": 30.0, "value": 60.0, "date": "2025-03-05", "location": "Washington, DC"},
        ]
    )


def test_plot_top_agencies(sample_df):
    ax = viz.plot_top_agencies(sample_df, metric="savings", top_n=2)
    assert isinstance(ax, Axes)


def test_plot_over_time(sample_df):
    ax = viz.plot_over_time(sample_df, date_col="date", value_col="savings", freq="ME")
    assert isinstance(ax, Axes)


def test_plot_distribution(sample_df):
    ax = viz.plot_distribution(sample_df, column="value", log=True)
    assert isinstance(ax, Axes)


def test_plot_cumulative(sample_df):
    ax = viz.plot_cumulative(sample_df, date_col="date", value_col="savings")
    assert isinstance(ax, Axes)


def test_missing_column_raises(sample_df):
    with pytest.raises(KeyError):
        viz.plot_top_agencies(sample_df, metric="does_not_exist")


@pytest.mark.parametrize(
    "location,expected",
    [
        ("Washington, DC", "DC"),
        ("New York, NY", "NY"),
        ("Arlington, VA", "VA"),
        ("Somewhere", None),
        (None, None),
        (123, None),
    ],
)
def test_state_from_location(location, expected):
    assert viz.state_from_location(location) == expected


def test_add_state_column(sample_df):
    out = viz.add_state_column(sample_df)
    assert list(out["state"]) == ["TX", "TX", "VA", "DC"]


def test_plot_state_choropleth(sample_df):
    pytest.importorskip("plotly")
    fig = viz.plot_state_choropleth(sample_df, value_col="savings")
    # A plotly figure exposes a `.data` tuple of traces.
    assert hasattr(fig, "data")
    assert len(fig.data) == 1
