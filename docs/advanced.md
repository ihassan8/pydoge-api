# 🧩 Advanced Usage

This page goes beyond the quickstart: error handling, async pagination, output modes,
client configuration, and working directly with the typed response models.

---

## ⚙️ Runtime flags

`DogeAPI` takes four flags that change how every endpoint behaves:

| Flag | Default | Effect |
|------|---------|--------|
| `fetch_all` | `False` | Follow pagination and return **all** pages merged into one response |
| `output_pydantic` | `True` | Return Pydantic models. `False` returns export-capable `dict`s |
| `handle_response` | `True` | Parse the body. `False` returns the raw `httpx.Response` |
| `run_async` | `False` | Fetch remaining pages concurrently with asyncio |

Any other keyword arguments are forwarded to `DogeAPIClient` (see
[Client configuration](#client-configuration)).

---

## 🚨 Error handling

A request that keeps failing (HTTP `429`/`5xx` after all retries) or returns a
non-retriable error (`400`, `401`, `403`, `404`, …) raises `DogeAPIRequestError`:

```python
from pydoge_api import DogeAPI, DogeAPIRequestError

with DogeAPI() as api:
    try:
        grants = api.savings.get_grants(sort_by="savings")
    except DogeAPIRequestError as err:
        print(err.method)       # "GET"
        print(err.url)          # the full request URL
        print(err.status_code)  # e.g. 503
        print(str(err))         # "[503] GET https://... failed: Max retries exceeded"
```

The same `DogeAPIRequestError` is raised from both the synchronous and `run_async=True`
paths, so you only need one `except` clause.

### Tuning retries

Retry behavior is configured on the client (pass these straight to `DogeAPI`):

| Param | Default | Description |
|-------|---------|-------------|
| `max_retries` | `5` | Attempts for retriable (`429`/`5xx`) responses |
| `backoff_factor` | `1.5` | Exponential backoff base; honors a `Retry-After` header when present |
| `max_backoff` | `60.0` | Upper bound (seconds) on any single backoff sleep |

```python
api = DogeAPI(max_retries=3, backoff_factor=2.0, max_backoff=30.0)
```

---

## ⚡ Async pagination

When fetching large, multi-page datasets, set `run_async=True` so the remaining pages are
requested concurrently instead of one-by-one:

```python
with DogeAPI(fetch_all=True, run_async=True) as api:
    contracts = api.savings.get_contracts(sort_by="savings")
    print(contracts.meta.total_results)
```

The async path reuses your client's `base_url`, `timeout`, and headers.

!!! tip "Jupyter / IPython"
    Notebooks already run an event loop. Async mode falls back to
    [`nest_asyncio`](https://pypi.org/project/nest-asyncio/) in that case — make sure it's
    installed (it ships as a dependency) or you'll get a `RuntimeError` in interactive
    environments.

---

## 🔀 Output modes

### Dict mode (`output_pydantic=False`)

Returns plain `dict`s that still carry the `.export()` / `.to_dataframe()` / `.summary()`
helpers:

```python
with DogeAPI(output_pydantic=False) as api:
    grants = api.savings.get_grants()
    print(grants["result"]["grants"][0]["agency"])
    grants.export("grants", format="csv")  # helpers still work
```

### Raw response mode (`handle_response=False`)

Returns the underlying `httpx.Response` untouched — no parsing, no models:

```python
with DogeAPI(handle_response=False) as api:
    resp = api.savings.get_grants()
    print(resp.status_code)
    print(resp.json()["meta"])
```

---

## 🛠️ Client configuration

Extra keyword arguments on `DogeAPI` flow through to `DogeAPIClient` and then to the
underlying `httpx.Client`:

```python
with DogeAPI(timeout=30.0, headers={"User-Agent": "my-app/1.0"}) as api:
    leases = api.savings.get_leases()
```

You can also inject a fully pre-configured `httpx.Client` (handy for custom transports,
auth, or testing):

```python
import httpx
from pydoge_api import DogeAPI

session = httpx.Client(base_url="https://api.doge.gov", timeout=20.0)
with DogeAPI(session=session) as api:
    payments = api.payments.get_payments()
```

When you pass your own `session`, the SDK will **not** close it for you.

---

## 🧱 Working with the response models

With `output_pydantic=True` (the default) every response is a typed Pydantic model. You can
navigate it directly instead of converting to a DataFrame:

```python
with DogeAPI(fetch_all=True) as api:
    grants = api.savings.get_grants(sort_by="savings")

    print(grants.success)               # bool
    print(grants.meta.total_results)    # int
    print(grants.meta.pages)            # int

    for grant in grants.result.grants:
        print(grant.agency, grant.savings, grant.value)
```

Each endpoint returns its own response/record types:

| Endpoint | Response model | Record collection |
|----------|----------------|-------------------|
| `savings.get_grants()` | `GrantResponse` | `.result.grants` (`Grant`) |
| `savings.get_contracts()` | `ContractResponse` | `.result.contracts` (`Contract`) |
| `savings.get_leases()` | `LeaseResponse` | `.result.leases` (`Lease`) |
| `payments.get_payments()` | `PaymentResponse` | `.result.payments` (`Payment`) |

See the [Models reference](reference/models_savings.md) for every field.

---

## 🧮 Combined savings dataset

`api.savings.all()` fetches grants, contracts, and leases and concatenates them into one
tidy `pandas.DataFrame` tagged with a `kind` column — ideal for cross-category analysis:

```python
with DogeAPI(fetch_all=True) as api:
    df = api.savings.all()

# Total savings by category
print(df.groupby("kind")["savings"].sum())

# Top agencies across everything
print(df.groupby("agency")["savings"].sum().nlargest(10))
```

Columns that exist on only one endpoint (`recipient`, `vendor`, `location`, …) are filled
with `NaN` where they don't apply. `all()` requires `handle_response=True` (the default)
since it needs parsed data; pass `parse_dates=False` to keep raw date strings.

---

## 🔎 Sorting & filtering

```python
with DogeAPI() as api:
    # Savings endpoints: sort_by + sort_order
    api.savings.get_grants(sort_by="savings", sort_order="desc")
    api.savings.get_contracts(sort_by="value", sort_order="asc")

    # Payments: filter by a field/value pair (filter: agency_name | date | org_name)
    api.payments.get_payments(filter="agency_name", filter_value="NASA")
```

---

## 📊 Payment statistics

`api.payments.get_statistics()` calls `/payments/statistics` and returns aggregate
counts — by agency, by request date, and by organization. It is **not paginated** and
has no `meta`:

```python
with DogeAPI() as api:
    stats = api.payments.get_statistics()

for row in stats.result.agency:
    print(row.agency_name, row.count)

# `request_date` and `org_names` follow the same {name, count} shape
```
