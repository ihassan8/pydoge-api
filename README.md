<a name="readme-top"></a>

<div align="center">

<img src="https://github.com/ihassan8/pydoge-api/raw/main/docs/img/logo_main.PNG" alt="PyDOGE Logo" width="176">

# PyDOGE API

**A modern, fully-typed Python SDK for the U.S. Department of Government Efficiency (DOGE) API** — pull cancelled grants, contracts, leases, and payments, then analyze, export, and visualize them in a few lines.

[![PyPI version](https://img.shields.io/pypi/v/pydoge-api?color=3f51b5&logo=pypi&logoColor=white)](https://pypi.org/project/pydoge-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydoge-api?color=3f51b5&logo=python&logoColor=white)](https://pypi.org/project/pydoge-api/)
[![Downloads](https://img.shields.io/pypi/dm/pydoge-api?color=3f51b5)](https://pypi.org/project/pydoge-api/)
[![CI](https://img.shields.io/github/actions/workflow/status/ihassan8/pydoge-api/ci.yml?branch=main&label=CI&logo=github)](https://github.com/ihassan8/pydoge-api/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-3f51b5?logo=readthedocs&logoColor=white)](https://ihassan8.github.io/pydoge-api)
[![License: MIT](https://img.shields.io/badge/license-MIT-3f51b5.svg)](https://github.com/ihassan8/pydoge-api/blob/main/LICENSE)

<a href="https://ihassan8.github.io/pydoge-api"><strong>📃 Documentation</strong></a> &nbsp;·&nbsp;
<a href="https://pypi.org/project/pydoge-api/">📦 PyPI</a> &nbsp;·&nbsp;
<a href="https://github.com/ihassan8/pydoge-api/issues/new">🐛 Report a bug</a>

</div>

---

PyDOGE API wraps the public [DOGE API](https://api.doge.gov/docs) — a federal transparency
initiative publishing detailed data on 💸 cancelled grants, 📑 contract terminations,
🏢 lease reductions, and 🧾 payment transactions — and turns it into a smooth workflow for
data scientists, analysts, and journalists.

## ✨ Highlights

|  | Feature | What you get |
|--|---------|--------------|
| 🔄 | **Auto-pagination** | Fetch one page or every page (`fetch_all=True`), sync or async |
| 🧱 | **Typed responses** | Pydantic v2 models — or plain dicts when you prefer |
| 🐼 | **DataFrames** | `.to_dataframe()` with automatic date parsing |
| 💾 | **One-line export** | CSV / Excel / JSON, timestamped |
| 📊 | **Instant summary** | rows, nulls, dtypes, and stats via `.summary()` |
| 🧮 | **Combined dataset** | `savings.all()` — grants + contracts + leases in one tidy frame |
| 📈 | **Built-in charts** | bar, time-series, distribution, US-state choropleth (`[viz]` extra) |
| 🖥️ | **Modern CLI** | `pydoge` — Typer + Rich, fetch/export/summarize from the terminal |
| 🔁 | **Retry-safe client** | exponential backoff on 429/5xx, with a cap |
| 🔒 | **Secure logging** | credential scrubbing + on-demand masking via [PyLogShield](https://github.com/ihassan8/pylogshield) |

## 📦 Installation

```bash
pip install pydoge-api              # core
pip install "pydoge-api[viz]"      # + charts (matplotlib, plotly)
```

> Requires Python 3.9+.

## ⚡ Quickstart

```python
from pydoge_api import DogeAPI

with DogeAPI(fetch_all=True) as api:
    grants = api.savings.get_grants(sort_by="savings")

    print(grants.meta.total_results)        # e.g. 15887
    df = grants.to_dataframe()              # pandas DataFrame, dates parsed
    grants.summary()                        # rows / nulls / dtypes / stats
    grants.export("grants", format="csv")  # -> grants_YYYYMMDD_HHMMSS.csv
```

Prefer the **combined** savings dataset?

```python
with DogeAPI(fetch_all=True) as api:
    df = api.savings.all()                  # grants + contracts + leases, with a `kind` column

print(df.groupby("kind")["savings"].sum())
```

## 🖥️ Command line

No Python required — the `pydoge` CLI ships with the package:

```bash
pydoge grants --sort-by savings --limit 10                       # Rich preview table
pydoge payments --filter agency_name --filter-value NASA --summary
pydoge contracts --fetch-all --export csv --out contracts        # timestamped CSV
pydoge all --export json                                          # combined dataset
```

## 📈 Visualize in one line

```python
from pydoge_api import DogeAPI, viz        # pip install "pydoge-api[viz]"

with DogeAPI(fetch_all=True) as api:
    df = api.savings.get_grants(sort_by="savings").to_dataframe()

viz.plot_top_agencies(df, metric="savings", top_n=10)
```

<div align="center">
<img src="https://github.com/ihassan8/pydoge-api/raw/main/docs/img/top_agencies_savings.png" alt="Top 10 agencies by grant savings" width="760">
</div>

Also available: `plot_over_time`, `plot_distribution`, `plot_cumulative`, and an interactive
US-state `plot_state_choropleth` for leases.

## 📚 More examples

<details>
<summary><strong>Contracts, leases & payments</strong></summary>

```python
from pydoge_api import DogeAPI

with DogeAPI(fetch_all=True) as api:
    contracts = api.savings.get_contracts(sort_by="value")
    leases    = api.savings.get_leases(sort_by="savings")
    payments  = api.payments.get_payments(filter="agency_name", filter_value="NASA")

    for resp, name in [(contracts, "contracts"), (leases, "leases"), (payments, "payments")]:
        resp.summary()
        resp.export(name, format="xlsx")
```

Sort fields: savings endpoints accept `savings | value | date`; payments accept `amount | date`.
Payment filters: `agency_name | date | org_name`.
</details>

<details>
<summary><strong>Output modes & async</strong></summary>

```python
# Plain dicts instead of Pydantic models (still export-capable)
with DogeAPI(output_pydantic=False) as api:
    grants = api.savings.get_grants()
    grants.export("grants", format="json")

# Raw httpx.Response (no parsing)
with DogeAPI(handle_response=False) as api:
    resp = api.savings.get_grants()
    print(resp.status_code, resp.json()["meta"])

# Concurrent pagination for large pulls
with DogeAPI(fetch_all=True, run_async=True) as api:
    payments = api.payments.get_payments()
```
</details>

<details>
<summary><strong>Without a context manager</strong></summary>

```python
api = DogeAPI(fetch_all=True)
try:
    grants = api.savings.get_grants(sort_by="savings")
    grants.export("grants", format="csv")
finally:
    api.close()
```
</details>

<details>
<summary><strong>Error handling</strong></summary>

```python
from pydoge_api import DogeAPI, DogeAPIRequestError

with DogeAPI() as api:
    try:
        grants = api.savings.get_grants()
    except DogeAPIRequestError as err:
        print(err.status_code, err.url)   # raised after retries / on non-retriable errors
```
</details>

## 🔒 Secure logging

PyDOGE logs through [PyLogShield](https://github.com/ihassan8/pylogshield) — cloud-credential
prefixes (`AWS_`, `AZURE_`, `GCP_`, `TOKEN`, …) are scrubbed automatically, and you can mask
secrets per call. The logger is created lazily, so `import pydoge_api` has **no** side effects.

```python
from pydoge_api._logging import get_logger

log = get_logger("pydoge_api", enable_json=True)
log.warning("api_key=SECRET123", mask=True)   # -> api_key=***
```

## 📖 Documentation

- **Full docs:** https://ihassan8.github.io/pydoge-api/ — quickstart, advanced usage, CLI,
  visualization, logging, and the complete API reference.
- **Official DOGE API:** https://api.doge.gov/docs
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

## 🤝 Contributing

Contributions are welcome! Open an issue with the `enhancement` label, or fork the repo and
send a pull request. If PyDOGE API is useful to you, please ⭐ the project — it helps.

## 📝 License

Released under the [MIT License](LICENSE).

<p align="right">(<a href="#readme-top">back to top</a>)</p>
