# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — Unreleased

### ⚠️ Breaking changes
- **Payments model rewritten to match the DOGE OpenAPI spec.** `Payment` fields are now
  `payment_date`, `payment_amt`, `agency_name`, `award_description`, `fain`,
  `recipient_justification`, `agency_lead_justification`, `org_name`,
  `generated_unique_award_id`. The previous fields (`agency`, `amount`, `post_date`,
  `description`, `status_description`) have been removed. Code reading those attributes
  must be updated (e.g. `payment.amount` → `payment.payment_amt`).
- **Non-retriable HTTP errors now raise.** `DogeAPIClient` raises `DogeAPIRequestError`
  for non-retriable `4xx`/`5xx` responses instead of returning the raw body; the async
  path raises `DogeAPIRequestError` instead of `RuntimeError`.
- Valid `sort_by` values for savings endpoints are `savings | value | date`, and the
  payments `filter` values are `agency_name | date | org_name` (previous docs/examples
  used invalid values such as `sort_by="agency"` / `filter="agency"`).

### Added
- `SavingsAPI.all()` — fetch grants, contracts, and leases into one tidy DataFrame with a
  `kind` column.
- `PaymentsAPI.get_statistics()` (`/payments/statistics`) with `PaymentStatisticsResponse`.
- `pydoge` command-line interface (Typer + Rich): `grants`, `contracts`, `leases`,
  `payments`, `all`, `version`. Also runnable as `python -m pydoge_api`.
- Optional `viz` extra (matplotlib + plotly): `plot_top_agencies`, `plot_over_time`,
  `plot_distribution`, `plot_cumulative`, and `plot_state_choropleth`.
- `ExportMixin.to_dataframe(parse_dates=True)` — coerces `date` / `payment_date` /
  `deleted_date` to `datetime64`.
- `ExportMixin.summary()` now returns the summary text and accepts `to_stdout=False`.
- `DogeAPI(client=...)` accepts an existing `DogeAPIClient` (its lifecycle stays with the
  caller); `DogeAPIClient` gained a `max_backoff` cap.

### Changed
- Logging now runs through [PyLogShield](https://github.com/ihassan8/pylogshield) and is
  created lazily, so `import pydoge_api` has no filesystem/console side effects.
- `DogeAnalytics` reuses an injected client via `DogeAPI(client=...)` (the internal
  `DogeAPIClientWrapper` was removed) and now requires `handle_response=True`.

### Fixed
- Async pagination reused the wrong base URL/config; it now reuses the configured
  client's `base_url`, `timeout`, and headers.
- Payments responses no longer fail to parse against the live API.

### Packaging
- `typer` and `rich` are now runtime dependencies (for the CLI).
- Docs migrated to Zensical; CI/release run via `ihassan8/shared-workflows`.
