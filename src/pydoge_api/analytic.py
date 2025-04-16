import pandas as pd
from typing import Optional
from .client import DogeAPIClient
from .endpoints.savings import SavingsAPI
from .api import DogeAPI
from pathlib import Path

class DogeAnalytics:
    """
    High-level analytics engine for grants, contracts, and leases using SavingsAPI.
    """

    def __init__(self, client: Optional[DogeAPIClient] = None, **api_kwargs):
        """
        Parameters
        ----------
        client : DogeAPIClient, optional
            If provided, reuses existing client. Else creates via DogeAPI.
        **api_kwargs : dict
            Passed to DogeAPI (e.g. fetch_all=True).
        """
        self._api = DogeAPI(**api_kwargs) if client is None else DogeAPIClientWrapper(client, **api_kwargs)
        self.savings = self._api.savings

    def top_agencies_by_savings(self, top_n: int = 10) -> pd.DataFrame:
        grants = self.savings.get_grants()
        df = grants.to_dataframe() if hasattr(grants, "to_dataframe") else pd.DataFrame(grants["result"]["grants"])
        top = df.groupby("agency")["savings"].sum().sort_values(ascending=False).head(top_n).reset_index()
        top.columns = ["Agency", "Total Savings"]
        return top

    def top_contracts_by_value(self, top_n: int = 10) -> pd.DataFrame:
        contracts = self.savings.get_contracts()
        df = contracts.to_dataframe() if hasattr(contracts, "to_dataframe") else pd.DataFrame(contracts["result"]["contracts"])
        top = df.sort_values("value", ascending=False).head(top_n).reset_index(drop=True)
        return top

    def lease_area_summary(self) -> pd.DataFrame:
        leases = self.savings.get_leases()
        df = leases.to_dataframe() if hasattr(leases, "to_dataframe") else pd.DataFrame(leases["result"]["leases"])
        summary = df.groupby("agency")["sq_ft"].sum().sort_values(ascending=False).reset_index()
        summary.columns = ["Agency", "Total Square Feet"]
        return summary

    def top_agencies_by_leases(self, top_n: int = 10) -> pd.DataFrame:
        leases = self.savings.get_leases()
        df = leases.to_dataframe() if hasattr(leases, "to_dataframe") else pd.DataFrame(leases["result"]["leases"])
        df = df[df["savings"].notnull()]  # replace with correct field if different
        return df.groupby("agency")["savings"].sum().sort_values(ascending=False).head(top_n).reset_index()

    def top_agencies_by_contracts(self, top_n: int = 10) -> pd.DataFrame:
        contracts = self.savings.get_contracts()
        df = contracts.to_dataframe() if hasattr(contracts, "to_dataframe") else pd.DataFrame(contracts["result"]["contracts"])
        df = df[df["savings"].notnull()]  # replace with actual field name
        return df.groupby("agency")["savings"].sum().sort_values(ascending=False).head(top_n).reset_index()
    
    def export_dataset(self, data: pd.DataFrame, filename: str, format: str = "csv") -> Path:
        format = format.lower()
        ext = {"csv": "csv", "xlsx": "xlsx", "json": "json"}[format]
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        path = Path(f"{filename}_{timestamp}.{ext}")

        if format == "csv":
            data.to_csv(path, index=False)
        elif format == "xlsx":
            data.to_excel(path, index=False)
        elif format == "json":
            path.write_text(data.to_json(orient="records", indent=2))
        else:
            raise ValueError("Unsupported export format.")

    def close(self):
        """Closes internal session."""
        self._api.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DogeAPIClientWrapper:
    """
    Temporary wrapper for injecting custom client into SavingsAPI.
    """

    def __init__(self, client: DogeAPIClient, **api_kwargs):
        self.fetch_all = api_kwargs.get("fetch_all", False)
        self.output_pydantic = api_kwargs.get("output_pydantic", True)
        self.handle_response = api_kwargs.get("handle_response", True)
        self.run_async = api_kwargs.get("run_async", False)
        self.client = client
        self.savings = SavingsAPI(client=client, api=self)
