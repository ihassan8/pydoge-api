# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyDOGE API is a Python SDK for the public-facing API of the **Department of Government
Efficiency (DOGE)** (`https://api.doge.gov`). It provides fully typed, auto-paginated,
export-ready access to the savings (grants, contracts, leases) and payments endpoints,
plus a small analytics layer built on Pandas. Internal logging is provided by
[PyLogShield](https://github.com/ihassan8/pylogshield) for credential scrubbing and
optional sensitive-data masking.

## Build & Development Commands

Declared `requires-python = ">=3.8"` in `pyproject.toml`; CI matrix tests 3.8–3.12 on
Ubuntu and Windows.

```bash
# Install in development mode with dev/test tooling
pip install -e ".[dev]"

# Install the optional plotting extra (matplotlib + plotly)
pip install -e ".[viz]"

# Run tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ -v --cov=src/pydoge_api --cov-report=term-missing

# Run a single test file / test
pytest tests/test_client.py -v
pytest tests/test_client.py::test_retries_on_429 -v

# Lint and type-check
ruff check src/ tests/
mypy src/ --ignore-missing-imports

# Build the Zensical docs locally
pip install -r docs/requirements.txt
zensical build          # or: zensical serve

# Build the package
python -m build
```

## Architecture

### Core package (`src/pydoge_api/`)

- **`api.py`** — `DogeAPI`: the unified entrypoint. Holds the shared `DogeAPIClient`
  and the global runtime flags (`fetch_all`, `output_pydantic`, `handle_response`,
  `run_async`) that every endpoint reads. Context-manager friendly (`with DogeAPI() as
  api:`). Exposes `.savings` and `.payments`.

- **`client.py`** — `DogeAPIClient`: low-level `httpx.Client` wrapper with retry/backoff
  (`rest_request`) for `429` and `5xx`, honoring `Retry-After`. `get()`/`post()` are thin
  helpers; `DogeAPIRequestError` is raised after `max_retries`. Accepts a caller-supplied
  `session=httpx.Client(...)` (validated by type) — this is the seam used in tests via
  `httpx.MockTransport`.

- **`endpoints/savings.py`** — `SavingsAPI`: `get_grants`, `get_contracts`, `get_leases`.
  Each builds a `*Params` model, calls the client, parses into the matching `*Response`
  model, then delegates pagination to `_fetch_paginated`. `all()` fetches all three and
  returns one tidy `DataFrame` tagged with a `kind` column (requires `handle_response=True`).

- **`endpoints/payments.py`** — `PaymentsAPI`: `get_payments` (`filter`/`filter_value`,
  `sort_by`/`sort_order`) — keyword args match `PaymentParams`.

- **`models/common.py`** — shared `Meta` pagination model used by every `*Response`.

- **`models/savings.py`, `models/payments.py`** — Pydantic v2 request (`*Params`) and
  response (`*Response`, with nested `Result*` + `Meta`) models. Response models mix in
  `ExportMixin`.

- **`utils/pagination.py`** — `_fetch_paginated`: DRY pagination for every endpoint.
  Short-circuits when `fetch_all` is off or only one page exists; otherwise fetches the
  remaining pages (sync loop, or async via `run_async`) and patches `meta`.

- **`utils/async_tools.py`** — `run_async` (safe even inside Jupyter via `nest_asyncio`)
  and the async page-fetch helpers with their own retry/backoff.

- **`utils/exporter.py`** — `ExportMixin`: `.export()` (csv/xlsx/json, timestamped),
  `.to_dataframe()` (coerces `date`/`payment_date`/`deleted_date` to `datetime64` via
  `parse_dates=True`; see `DATE_COLUMNS`), `.summary()`. `DictExportable`/`handle_dict`
  give the same methods to plain-dict output (when `output_pydantic=False`).

- **`cli.py` / `__main__.py`** — Typer + Rich CLI exposed as the `pydoge` console script
  (and `python -m pydoge_api`). Commands: `grants`, `contracts`, `leases`, `payments`,
  `all`, `version`; each supports `--export`/`--summary`/`--limit` and previews results as
  a Rich table. Entry point: `pydoge_api.cli:main`.

- **`viz.py`** — optional plotting helpers (requires the `viz` extra: matplotlib +
  plotly). `plot_top_agencies`, `plot_over_time`, `plot_distribution`, `plot_cumulative`
  (matplotlib `Axes`), and `plot_state_choropleth` (plotly `Figure`, parses lease
  `location` → state via `state_from_location`/`add_state_column`). Imports are lazy, so
  `import pydoge_api.viz` works without the extra; calling a plot function raises a clear
  install hint if it's missing.

- **`analytic.py`** — `DogeAnalytics`: higher-level Pandas roll-ups (top agencies by
  savings, contract value, lease square footage). Can reuse an existing client.

- **`_logging.py`** — internal logging shim. `get_logger()` wraps
  `pylogshield.get_logger` with `enable_context_scrubber=True`. The module-level
  `logger` (imported by `client.py` and `utils/async_tools.py`) is a **lazy proxy**
  (`_LazyLogger`): PyLogShield opens `~/.logs/<name>.log` and attaches handlers in its
  constructor, so the proxy defers creation until the first actual log call — `import
  pydoge_api` has no filesystem/console side effects. Pass `log_directory`/`add_console`
  through `get_logger` to change the destination.

### Public API (`__init__.py`)

Exports `DogeAPI`, `DogeAPIClient`, `DogeAPIRequestError`, `DogeAnalytics`,
`SavingsAPI`, `PaymentsAPI`.

### Key patterns

- The three runtime flags interact: `handle_response=False` returns the raw
  `httpx.Response` and skips all parsing; `output_pydantic=False` returns
  `DictExportable` dicts instead of Pydantic models; `fetch_all=True` triggers
  pagination; `run_async=True` switches pagination to the asyncio path.
- Logging is a drop-in `logging.Logger` subclass — existing `logger.warning(...)` /
  `logger.error(...)` call sites are unchanged. Pass `mask=True` to a log call to redact
  `key=value` / `key: value` secrets in the message string.
- Version is auto-generated from git tags by `setuptools_scm` into
  `src/pydoge_api/_version.py` (git-ignored; do not edit by hand).

## Testing

Tests live in `tests/` and never hit the network — `DogeAPIClient` is constructed with
an `httpx.Client(transport=httpx.MockTransport(handler))` so requests are served from
in-memory fixtures. `asyncio_mode = "auto"` is set in `pyproject.toml`, so async tests
need no `@pytest.mark.asyncio`.

Test modules:
- `test_client.py` — retry/backoff, `Retry-After`, `DogeAPIRequestError`, custom-session
  validation, context-manager close.
- `test_savings.py` / `test_payments.py` — params → request, response parsing, the
  `handle_response=False` raw passthrough.
- `test_pagination.py` — multi-page merge + `meta` patching; `fetch_all=False`
  short-circuit.
- `test_exporter.py` — `export` (csv/json/xlsx), `to_dataframe` (+ date parsing),
  `summary`, `handle_dict`/`DictExportable`.
- `test_models.py` — Pydantic model validation round-trips.
- `test_async.py` — `_async_get` retry/success and `DogeAPIRequestError` unification.
- `test_logging.py` — `_logging.get_logger` returns a PyLogShield instance.
- `test_viz.py` — plotting helpers and `state_from_location` (skipped when the `viz`
  extra is absent via `pytest.importorskip`).
- `test_cli.py` — Typer CLI commands via `CliRunner`, with `DogeAPI` patched to a mock
  transport (and `savings.all()` combined-dataset coverage in `test_savings.py`).

## Release Process

Automated via GitHub Actions:
- Push to `main` runs `ci.yml` (test/lint/typecheck/audit/coverage via
  `ihassan8/shared-workflows`); on success `release.yml` deploys the Zensical docs to
  GitHub Pages.
- Push a bare SemVer tag (e.g. `git tag 1.2.3 && git push origin 1.2.3`) builds and
  publishes to PyPI. Requires the `PYPI_API_TOKEN` secret (trusted publishing disabled).
