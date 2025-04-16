# 📊 DogeAnalytics

`DogeAnalytics` is a high-level data enrichment and reporting layer built on top of `SavingsAPI`.  
It helps you quickly analyze grants, leases, and contracts using the DOGE API.

---

## 🚀 Instantiating DogeAnalytics

### ✅ With context manager (recommended)

```python
from doge_api import DogeAnalytics

with DogeAnalytics(fetch_all=True) as da:
    df = da.grants_dataframe()
    print(df.head())
```

## ❗ Without context manager

```python
da = DogeAnalytics(fetch_all=True)
df = da.grants_dataframe()
da.close()  # Don't forget to close manually
```
## ⚙️ Constructor Parameters
| Param | Description | Default |
|------|-------|------|
| fetch_all | Fetch all pages for paginated responses | True |
| output_pydantic | Return full Pydantic model vs plain dict | True |
| handle_response | Whether to parse and return the response body | True |
| run_async | Enable async pagination where supported | False|
| **client_kwargs | Additional kwargs passed to DogeAPIClient (e.g. headers) | |

## 📑 Available DataFrames

```python
da.grants_dataframe()
da.contracts_dataframe()
da.leases_dataframe()

```

## 🏆 Top Agency Analysis

```python
da.top_agencies_by_savings(top_n=10)
da.top_agencies_by_leases(top_n=5)
da.top_agencies_by_contracts(top_n=3)

```
Each returns a sorted DataFrame like:
| agency | savings |
| NASA | 4,580,000 |
| DHS | 3,990,000 |

## 💾 Exporting Results
Use .export_dataset() to save any DataFrame with a timestamped filename.

```python
df = da.top_agencies_by_savings()
da.export_dataset(df, "top_savers", format="xlsx")
```

**Supported Formats**

- csv → Comma-separated
- xlsx → Excel spreadsheet
- json → Pretty-printed array