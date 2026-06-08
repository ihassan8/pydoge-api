"""Command-line interface for PyDOGE API.

A modern Typer + Rich CLI for pulling, previewing, exporting, and summarizing DOGE
datasets without writing any Python.

Examples
--------
```bash
pydoge grants --sort-by savings --fetch-all --limit 20
pydoge contracts --export csv --out contracts
pydoge payments --filter agency_name --filter-value NASA --summary
pydoge all --export json                # combined grants+contracts+leases
pydoge version
```
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from .api import DogeAPI

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="PyDOGE API — access Department of Government Efficiency (DOGE) data from the terminal.",
)
console = Console()

EXPORT_FORMATS = ("csv", "xlsx", "json")


def _render_table(df, *, limit: int, title: str) -> None:
    """Print the first ``limit`` rows of a DataFrame as a Rich table."""
    preview = df.head(limit)
    table = Table(title=f"{title}  (showing {len(preview)} of {len(df)} rows)")
    for col in preview.columns:
        table.add_column(str(col), overflow="fold")
    for _, row in preview.iterrows():
        table.add_row(*("" if pd.isna(v) else str(v) for v in row.tolist()))
    console.print(table)


def _emit(result: Any, *, title: str, export: Optional[str], out: str, summary: bool, limit: int) -> None:
    """Shared handling for a single-endpoint response (model or DictExportable)."""
    df = result.to_dataframe()
    if export:
        path = result.export(out, format=export)
        console.print(f"[green]✓[/] Saved {len(df)} rows to [bold]{path}[/]")
    if summary:
        console.print(result.summary(to_stdout=False))
    if not export and not summary:
        _render_table(df, limit=limit, title=title)


def _export_dataframe(df, out: str, fmt: str) -> Path:
    """Export a plain DataFrame (used by the combined `all` command)."""
    fmt = fmt.lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(f"{out}_{timestamp}.{fmt}")
    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "xlsx":
        df.to_excel(path, index=False)
    elif fmt == "json":
        path.write_text(df.to_json(orient="records", indent=2, date_format="iso"))
    else:
        raise typer.BadParameter(f"Unsupported format '{fmt}'. Choose: {', '.join(EXPORT_FORMATS)}.")
    return path


# ── Shared option definitions ───────────────────────────────────────────────

_SortBy = typer.Option(None, "--sort-by", help="Field to sort by (e.g. savings, value).")
_SortOrder = typer.Option(None, "--sort-order", help="Sort direction: asc or desc.")
_FetchAll = typer.Option(False, "--fetch-all/--no-fetch-all", help="Follow pagination and fetch every page.")
_PerPage = typer.Option(100, "--per-page", help="Records per page (max 500).")
_Limit = typer.Option(10, "--limit", help="Rows to show in the preview table.")
_Export = typer.Option(None, "--export", help=f"Write to a file: {', '.join(EXPORT_FORMATS)}.")
_Out = typer.Option(None, "--out", help="Output filename stem (a timestamp + extension is appended).")
_Summary = typer.Option(False, "--summary", help="Print an analytic summary instead of a preview.")


@app.command()
def grants(
    sort_by: Optional[str] = _SortBy,
    sort_order: Optional[str] = _SortOrder,
    fetch_all: bool = _FetchAll,
    per_page: int = _PerPage,
    limit: int = _Limit,
    export: Optional[str] = _Export,
    out: Optional[str] = _Out,
    summary: bool = _Summary,
) -> None:
    """Cancelled or reduced government grants."""
    with DogeAPI(fetch_all=fetch_all) as api:
        result = api.savings.get_grants(sort_by=sort_by, sort_order=sort_order, per_page=per_page)
        _emit(result, title="Grants", export=export, out=out or "grants", summary=summary, limit=limit)


@app.command()
def contracts(
    sort_by: Optional[str] = _SortBy,
    sort_order: Optional[str] = _SortOrder,
    fetch_all: bool = _FetchAll,
    per_page: int = _PerPage,
    limit: int = _Limit,
    export: Optional[str] = _Export,
    out: Optional[str] = _Out,
    summary: bool = _Summary,
) -> None:
    """Cancelled or optimized government contracts."""
    with DogeAPI(fetch_all=fetch_all) as api:
        result = api.savings.get_contracts(sort_by=sort_by, sort_order=sort_order, per_page=per_page)
        _emit(result, title="Contracts", export=export, out=out or "contracts", summary=summary, limit=limit)


@app.command()
def leases(
    sort_by: Optional[str] = _SortBy,
    sort_order: Optional[str] = _SortOrder,
    fetch_all: bool = _FetchAll,
    per_page: int = _PerPage,
    limit: int = _Limit,
    export: Optional[str] = _Export,
    out: Optional[str] = _Out,
    summary: bool = _Summary,
) -> None:
    """Terminated or downsized government leases."""
    with DogeAPI(fetch_all=fetch_all) as api:
        result = api.savings.get_leases(sort_by=sort_by, sort_order=sort_order, per_page=per_page)
        _emit(result, title="Leases", export=export, out=out or "leases", summary=summary, limit=limit)


@app.command()
def payments(
    filter: Optional[str] = typer.Option(None, "--filter", help="Filter key: agency_name, date, or org_name."),
    filter_value: Optional[str] = typer.Option(None, "--filter-value", help="Value to filter by."),
    sort_by: Optional[str] = _SortBy,
    sort_order: Optional[str] = _SortOrder,
    fetch_all: bool = _FetchAll,
    per_page: int = _PerPage,
    limit: int = _Limit,
    export: Optional[str] = _Export,
    out: Optional[str] = _Out,
    summary: bool = _Summary,
) -> None:
    """Payment transactions made by government agencies."""
    with DogeAPI(fetch_all=fetch_all) as api:
        result = api.payments.get_payments(
            sort_by=sort_by, sort_order=sort_order, filter=filter, filter_value=filter_value, per_page=per_page
        )
        _emit(result, title="Payments", export=export, out=out or "payments", summary=summary, limit=limit)


@app.command(name="all")
def combined(
    fetch_all: bool = typer.Option(True, "--fetch-all/--no-fetch-all", help="Follow pagination (default on)."),
    limit: int = _Limit,
    export: Optional[str] = _Export,
    out: Optional[str] = _Out,
) -> None:
    """Combined grants + contracts + leases as one tidy table (with a `kind` column)."""
    with DogeAPI(fetch_all=fetch_all) as api:
        df = api.savings.all()
    if export:
        path = _export_dataframe(df, out or "doge_savings", export)
        console.print(f"[green]✓[/] Saved {len(df)} rows to [bold]{path}[/]")
    else:
        _render_table(df, limit=limit, title="All savings")


@app.command()
def version() -> None:
    """Print the installed pydoge-api version."""
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version

    try:
        console.print(_pkg_version("pydoge_api"))
    except PackageNotFoundError:  # pragma: no cover - only when running from a non-installed tree
        console.print("unknown")


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
