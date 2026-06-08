# 🖥️ Command-Line Interface

PyDOGE API ships a modern [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/)
CLI, so you can pull, preview, export, and summarize DOGE data without writing any Python.
It's installed automatically with the package as the `pydoge` command (also runnable as
`python -m pydoge_api`).

```bash
pydoge --help
```

---

## Commands

| Command | Description |
|---------|-------------|
| `pydoge grants` | Cancelled or reduced government grants |
| `pydoge contracts` | Cancelled or optimized government contracts |
| `pydoge leases` | Terminated or downsized government leases |
| `pydoge payments` | Payment transactions (supports `--filter`/`--filter-value`) |
| `pydoge all` | Combined grants + contracts + leases as one table |
| `pydoge version` | Print the installed version |

## Common options

Available on `grants`, `contracts`, `leases`, and `payments`:

| Option | Description |
|--------|-------------|
| `--sort-by` | Field to sort by (e.g. `savings`, `value`) |
| `--sort-order` | `asc` or `desc` |
| `--fetch-all / --no-fetch-all` | Follow pagination and fetch every page |
| `--per-page` | Records per page (max 500) |
| `--limit` | Rows to show in the preview table (default 10) |
| `--export` | Write to a file: `csv`, `xlsx`, or `json` |
| `--out` | Output filename stem (a timestamp + extension is appended) |
| `--summary` | Print an analytic summary instead of a preview |

`payments` additionally accepts `--filter` and `--filter-value`.

---

## Examples

Preview the top grants by savings as a Rich table:

```bash
pydoge grants --sort-by savings --fetch-all --limit 20
```

Export every contract to a timestamped CSV:

```bash
pydoge contracts --fetch-all --export csv --out contracts
# ✓ Saved 1234 rows to contracts_20250410_172308.csv
```

Filter payments by agency and print a statistical summary:

```bash
pydoge payments --filter agency --filter-value NASA --summary
```

Pull the combined savings dataset (grants + contracts + leases) to a single JSON file:

```bash
pydoge all --export json --out doge_savings
```

By default `pydoge all` fetches every page; pass `--no-fetch-all` for a quick sample.
