from pathlib import Path
from typing import Any, Optional, cast

import pandas as pd

from .api import DogeAPI
from .client import DogeAPIClient


class DogeAnalytics:
    """
    High-level analytics engine for grants, contracts, and leases using SavingsAPI.

    Every method returns a ranked/aggregated ``pandas.DataFrame``. Requires parsed
    responses (``handle_response=True``, the default); pass ``fetch_all=True`` for
    meaningful rankings over the full dataset.
    """

    def __init__(self, client: Optional[DogeAPIClient] = None, **api_kwargs):
        """
        Parameters
        ----------
        client : DogeAPIClient, optional
            If provided, reuses the existing client (its lifecycle stays with the
            caller). Otherwise a new client is created internally.
        **api_kwargs : dict
            Passed to DogeAPI (e.g. fetch_all=True, run_async=True).
        """
        if api_kwargs.get("handle_response") is False:
            raise ValueError(
                "DogeAnalytics needs parsed data; handle_response must be True."
            )
        self._api = DogeAPI(client=client, **api_kwargs)
        self.savings = self._api.savings

    @staticmethod
    def _frame(response: Any) -> pd.DataFrame:
        """Convert an endpoint response (Pydantic model or DictExportable) to a DataFrame."""
        return cast(pd.DataFrame, response.to_dataframe())

    def top_agencies_by_savings(self, top_n: int = 10) -> pd.DataFrame:
        df = self._frame(self.savings.get_grants())
        top = df.groupby("agency")["savings"].sum().sort_values(ascending=False).head(top_n).reset_index()
        top.columns = ["Agency", "Total Savings"]
        return top

    def top_contracts_by_value(self, top_n: int = 10) -> pd.DataFrame:
        df = self._frame(self.savings.get_contracts())
        return df.sort_values("value", ascending=False).head(top_n).reset_index(drop=True)

    def lease_area_summary(self) -> pd.DataFrame:
        df = self._frame(self.savings.get_leases())
        summary = df.groupby("agency")["sq_ft"].sum().sort_values(ascending=False).reset_index()
        summary.columns = ["Agency", "Total Square Feet"]
        return summary

    def top_agencies_by_leases(self, top_n: int = 10) -> pd.DataFrame:
        df = self._frame(self.savings.get_leases())
        df = df[df["savings"].notnull()]
        return df.groupby("agency")["savings"].sum().sort_values(ascending=False).head(top_n).reset_index()

    def top_agencies_by_contracts(self, top_n: int = 10) -> pd.DataFrame:
        df = self._frame(self.savings.get_contracts())
        df = df[df["savings"].notnull()]
        return df.groupby("agency")["savings"].sum().sort_values(ascending=False).head(top_n).reset_index()

    def export_dataset(self, data: pd.DataFrame, filename: str, format: str = "csv") -> Path:
        format = format.lower()
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        path = Path(f"{filename}_{timestamp}.{format}")

        if format == "csv":
            data.to_csv(path, index=False)
        elif format == "xlsx":
            data.to_excel(path, index=False)
        elif format == "json":
            path.write_text(data.to_json(orient="records", indent=2, date_format="iso"))
        else:
            raise ValueError("Unsupported export format. Choose: csv, xlsx, json.")

        return path

    def close(self):
        """Close the internal session (no-op when reusing an injected client)."""
        self._api.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
