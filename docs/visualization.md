# 📈 Visualization

The optional `viz` extra turns any response DataFrame into a chart. Install it with:

```bash
pip install "pydoge-api[viz]"
```

This pulls in **matplotlib** (bar / line / distribution / cumulative charts) and **plotly**
(the interactive US-state choropleth). The helpers live in `pydoge_api.viz` and operate on
the DataFrames returned by `.to_dataframe()`.

!!! tip "Dates just work"
    `.to_dataframe()` parses `date` / `payment_date` / `deleted_date` into real
    `datetime64` columns by default, so the time-based charts below work without any extra
    preparation. Pass `to_dataframe(parse_dates=False)` to opt out.

---

## Top agencies (bar)

```python
from pydoge_api import DogeAPI
from pydoge_api import viz

with DogeAPI(fetch_all=True) as api:
    df = api.savings.get_grants(sort_by="savings").to_dataframe()

ax = viz.plot_top_agencies(df, metric="savings", top_n=10)
ax.figure.savefig("top_agencies.png", bbox_inches="tight")
```

`plot_top_agencies(df, metric=..., by=..., top_n=...)` groups by `by` (default `agency`),
sums `metric`, and draws a horizontal bar chart. Works for any categorical column — e.g.
`by="vendor"` on contracts or `by="recipient"` on grants.

## Savings over time (line / area / bar)

```python
with DogeAPI(fetch_all=True) as api:
    df = api.savings.get_grants().to_dataframe()

viz.plot_over_time(df, date_col="date", value_col="savings", freq="ME")  # monthly
```

`freq` accepts any pandas offset alias — `"ME"` (month-end), `"QE"` (quarter), `"YE"`
(year). For payments use `date_col="payment_date"`, for contracts `date_col="deleted_date"`.

## Value distribution (histogram)

DOGE values are heavily skewed, so a log scale is often clearer:

```python
with DogeAPI(fetch_all=True) as api:
    df = api.savings.get_contracts().to_dataframe()

viz.plot_distribution(df, column="value", bins=40, log=True)
```

## Cumulative savings

```python
viz.plot_cumulative(df, date_col="date", value_col="savings")
```

## Lease savings by state (interactive choropleth)

Leases include a `location` (`"City, ST"`). `plot_state_choropleth` parses out the state,
rolls up the metric, and returns a **plotly** figure:

```python
with DogeAPI(fetch_all=True) as api:
    leases = api.savings.get_leases().to_dataframe()

fig = viz.plot_state_choropleth(leases, value_col="savings")
fig.show()                     # interactive window
fig.write_html("by_state.html")  # or export to a standalone HTML file
```

Need the state codes as data? Use the helpers directly:

```python
leases = viz.add_state_column(leases)   # adds a "state" column
viz.state_from_location("Houston, TX")  # -> "TX"
```

---

## Customizing charts

Every matplotlib helper accepts an existing `ax` and a `title`, and returns the `Axes`, so
you can compose subplots or restyle freely:

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
viz.plot_top_agencies(df, ax=axes[0], title="Top agencies")
viz.plot_over_time(df, ax=axes[1], title="Monthly savings")
fig.tight_layout()
```
