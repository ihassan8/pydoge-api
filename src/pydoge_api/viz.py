"""Plotting helpers for DOGE datasets.

These functions turn the DataFrames produced by :meth:`ExportMixin.to_dataframe`
into charts. They require the optional ``viz`` extra::

    pip install "pydoge-api[viz]"

matplotlib powers the bar/line/distribution/cumulative charts; plotly powers the
interactive US-state choropleth. Imports are deferred until a function is actually
called, so ``import pydoge_api.viz`` never fails just because the extra is missing.

Examples
--------
>>> from pydoge_api import DogeAPI
>>> from pydoge_api import viz
>>> with DogeAPI(fetch_all=True) as api:
...     df = api.savings.get_grants().to_dataframe()
>>> ax = viz.plot_top_agencies(df, metric="savings", top_n=10)
>>> fig = viz.plot_state_choropleth(
...     api.savings.get_leases().to_dataframe(), value_col="savings"
... )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - typing only
    from matplotlib.axes import Axes
    from plotly.graph_objects import Figure

__all__ = [
    "plot_top_agencies",
    "plot_over_time",
    "plot_distribution",
    "plot_cumulative",
    "plot_state_choropleth",
    "add_state_column",
    "state_from_location",
]

# Two-letter USPS codes accepted by plotly's ``locationmode="USA-states"``.
_US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via message only
        raise ImportError(
            "Plotting requires the 'viz' extra. Install it with: "
            'pip install "pydoge-api[viz]"'
        ) from exc
    return plt


def _require_plotly():
    try:
        import plotly.express as px  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via message only
        raise ImportError(
            "The choropleth requires the 'viz' extra. Install it with: "
            'pip install "pydoge-api[viz]"'
        ) from exc
    return px


def _new_axes(ax: Optional["Axes"]) -> "Axes":
    if ax is not None:
        return ax
    plt = _require_matplotlib()
    _, ax = plt.subplots()
    return ax


def plot_top_agencies(
    df: pd.DataFrame,
    *,
    metric: str = "savings",
    by: str = "agency",
    top_n: int = 10,
    ax: Optional["Axes"] = None,
    title: Optional[str] = None,
) -> "Axes":
    """Horizontal bar chart of the top ``by`` groups by summed ``metric``.

    Parameters
    ----------
    df : pandas.DataFrame
        A records DataFrame (e.g. from ``get_grants().to_dataframe()``).
    metric : str, default="savings"
        Numeric column to sum.
    by : str, default="agency"
        Grouping column.
    top_n : int, default=10
        Number of groups to show.
    ax : matplotlib.axes.Axes, optional
        Existing axes to draw on. A new figure is created if omitted.
    title : str, optional
        Chart title.
    """
    _require_columns(df, [by, metric])
    ax = _new_axes(ax)
    ranked = df.groupby(by)[metric].sum().sort_values(ascending=False).head(top_n)
    # Reverse so the largest bar is on top in a horizontal bar chart.
    ranked[::-1].plot.barh(ax=ax)
    ax.set_xlabel(metric)
    ax.set_ylabel(by)
    ax.set_title(title or f"Top {top_n} {by} by {metric}")
    return ax


def plot_over_time(
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    value_col: str = "savings",
    freq: str = "ME",
    agg: str = "sum",
    kind: str = "line",
    ax: Optional["Axes"] = None,
    title: Optional[str] = None,
) -> "Axes":
    """Aggregate ``value_col`` over time and plot it.

    Parameters
    ----------
    df : pandas.DataFrame
        Records DataFrame. ``date_col`` is coerced to datetime if needed.
    date_col : str, default="date"
        Datetime column to resample on.
    value_col : str, default="savings"
        Numeric column to aggregate.
    freq : str, default="ME"
        Pandas resample frequency (e.g. ``"ME"`` month-end, ``"QE"`` quarter, ``"YE"``).
    agg : str, default="sum"
        Aggregation passed to ``resample(...).agg``.
    kind : str, default="line"
        ``"line"``, ``"bar"`` or ``"area"``.
    """
    _require_columns(df, [date_col, value_col])
    ax = _new_axes(ax)
    series = df[[date_col, value_col]].copy()
    series[date_col] = pd.to_datetime(series[date_col], errors="coerce")
    series = series.dropna(subset=[date_col]).set_index(date_col).sort_index()
    resampled = series[value_col].resample(freq).agg(agg)
    resampled.plot(kind=kind, ax=ax)
    ax.set_xlabel(date_col)
    ax.set_ylabel(f"{agg}({value_col})")
    ax.set_title(title or f"{value_col} over time ({freq})")
    return ax


def plot_distribution(
    df: pd.DataFrame,
    *,
    column: str = "value",
    bins: int = 30,
    log: bool = False,
    ax: Optional["Axes"] = None,
    title: Optional[str] = None,
) -> "Axes":
    """Histogram of a numeric column (DOGE values are heavily skewed — try ``log=True``)."""
    _require_columns(df, [column])
    ax = _new_axes(ax)
    df[column].plot.hist(bins=bins, ax=ax)
    if log:
        ax.set_yscale("log")
    ax.set_xlabel(column)
    ax.set_title(title or f"Distribution of {column}")
    return ax


def plot_cumulative(
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    value_col: str = "savings",
    ax: Optional["Axes"] = None,
    title: Optional[str] = None,
) -> "Axes":
    """Cumulative total of ``value_col`` ordered by ``date_col``."""
    _require_columns(df, [date_col, value_col])
    ax = _new_axes(ax)
    series = df[[date_col, value_col]].copy()
    series[date_col] = pd.to_datetime(series[date_col], errors="coerce")
    series = series.dropna(subset=[date_col]).sort_values(date_col)
    series["__cum__"] = series[value_col].cumsum()
    ax.plot(series[date_col], series["__cum__"])
    ax.set_xlabel(date_col)
    ax.set_ylabel(f"cumulative {value_col}")
    ax.set_title(title or f"Cumulative {value_col}")
    return ax


def state_from_location(location: Any) -> Optional[str]:
    """Extract a two-letter USPS state code from a ``"City, ST"`` string.

    Returns ``None`` when no valid state code can be found.
    """
    if not isinstance(location, str):
        return None
    parts = [p.strip() for p in location.replace("/", ",").split(",") if p.strip()]
    for token in reversed(parts):
        code = token.upper()
        if code in _US_STATES:
            return code
    return None


def add_state_column(
    df: pd.DataFrame, *, location_col: str = "location", state_col: str = "state"
) -> pd.DataFrame:
    """Return a copy of ``df`` with a ``state_col`` derived from ``location_col``."""
    _require_columns(df, [location_col])
    out = df.copy()
    out[state_col] = out[location_col].map(state_from_location)
    return out


def plot_state_choropleth(
    df: pd.DataFrame,
    *,
    location_col: str = "location",
    value_col: str = "savings",
    agg: str = "sum",
    title: Optional[str] = None,
) -> "Figure":
    """Interactive US choropleth of ``value_col`` aggregated by state.

    Parses the lease ``location`` column (``"City, ST"``) into state codes, rolls up
    ``value_col``, and returns a plotly ``Figure`` (call ``.show()`` or
    ``.write_html(...)``). Rows without a recognizable state are dropped.
    """
    px = _require_plotly()
    _require_columns(df, [location_col, value_col])
    with_state = add_state_column(df, location_col=location_col)
    with_state = with_state.dropna(subset=["state"])
    rolled = with_state.groupby("state", as_index=False)[value_col].agg(agg)
    fig = px.choropleth(
        rolled,
        locations="state",
        locationmode="USA-states",
        color=value_col,
        scope="usa",
        title=title or f"{agg}({value_col}) by state",
    )
    return fig


def _require_columns(df: pd.DataFrame, columns: list) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"DataFrame is missing required column(s): {missing}")
