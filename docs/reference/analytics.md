# 📊 DogeAnalytics

`DogeAnalytics` is a high-level reporting layer built on top of `SavingsAPI`.
It helps you quickly rank and summarize grants, leases, and contracts using the DOGE API,
returning ready-to-use `pandas.DataFrame` results.

---

## 🚀 Instantiating DogeAnalytics

### ✅ With context manager (recommended)

```python
from pydoge_api import DogeAnalytics

with DogeAnalytics(fetch_all=True) as da:
    top = da.top_agencies_by_savings(top_n=10)
    print(top)
```

### ❗ Without context manager

```python
da = DogeAnalytics(fetch_all=True)
top = da.top_agencies_by_savings(top_n=10)
da.close()  # Don't forget to close manually
```

### ♻️ Reusing an existing client

```python
from pydoge_api import DogeAPI, DogeAnalytics

with DogeAPI(fetch_all=True) as api:
    da = DogeAnalytics(client=api.client, fetch_all=True)
    print(da.lease_area_summary())
```

## ⚙️ Constructor Parameters

| Param | Description | Default |
|------|-------|------|
| `client` | Reuse an existing `DogeAPIClient`. If omitted, a new `DogeAPI` is created internally | `None` |
| `fetch_all` | Fetch all pages for paginated responses | `False` |
| `output_pydantic` | Return full Pydantic model vs plain dict | `True` |
| `handle_response` | Whether to parse and return the response body | `True` |
| `run_async` | Enable async pagination where supported | `False` |
| `**api_kwargs` | Additional kwargs forwarded to `DogeAPI` / `DogeAPIClient` (e.g. `headers`, `timeout`) | |

!!! tip
    For meaningful rankings you almost always want `fetch_all=True` — otherwise only the
    first page (default 100 records) is aggregated.

## 🏆 Available analytics methods

| Method | Returns (DataFrame columns) |
|--------|------------------------------|
| `top_agencies_by_savings(top_n=10)` | `Agency`, `Total Savings` |
| `top_contracts_by_value(top_n=10)` | all contract columns, sorted by `value` |
| `lease_area_summary()` | `Agency`, `Total Square Feet` |
| `top_agencies_by_leases(top_n=10)` | `agency`, `savings` |
| `top_agencies_by_contracts(top_n=10)` | `agency`, `savings` |

```python
with DogeAnalytics(fetch_all=True) as da:
    da.top_agencies_by_savings(top_n=10)
    da.top_contracts_by_value(top_n=10)
    da.lease_area_summary()
    da.top_agencies_by_leases(top_n=5)
    da.top_agencies_by_contracts(top_n=3)
```

## 📑 Need the raw data instead?

`DogeAnalytics` exposes the underlying `SavingsAPI` as `.savings`, so you can pull a full
DataFrame and run your own analysis:

```python
with DogeAnalytics(fetch_all=True) as da:
    grants_df = da.savings.get_grants().to_dataframe()
    contracts_df = da.savings.get_contracts().to_dataframe()
    leases_df = da.savings.get_leases().to_dataframe()
```

## 💾 Exporting Results

Use `.export_dataset()` to save any DataFrame with a timestamped filename. It returns the
written `Path`.

```python
with DogeAnalytics(fetch_all=True) as da:
    df = da.top_agencies_by_savings()
    path = da.export_dataset(df, "top_savers", format="xlsx")
    print(f"Saved to: {path}")
```

**Supported Formats**

- `csv` → comma-separated
- `xlsx` → Excel spreadsheet
- `json` → pretty-printed array

---

## 📦 Class Reference

::: pydoge_api.analytic.DogeAnalytics
    options:
      show_source: true
