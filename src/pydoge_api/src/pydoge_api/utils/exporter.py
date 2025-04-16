import pandas as pd
from datetime import datetime
from io import StringIO
from pathlib import Path
from pydantic import BaseModel

class ExportMixin:
    def _get_timestamped_path(self, filename: str, ext: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return Path(f"{filename}_{timestamp}.{ext}")

    def _get_collection(self):
        if isinstance(self, BaseModel):
            result = self.model_dump(exclude_none=True).get("result")
        elif isinstance(self, dict):
            result = self.get("result")
        else:
            raise TypeError("Unsupported export type")

        if not result or not isinstance(result, dict):
            raise ValueError("Expected `result` to contain a data collection.")

        return next(iter(result.values()))  # e.g., grants, payments, etc.

    def export(self, filename: str = "doge_data", format: str = "csv") -> Path:
        format = format.lower()
        path = self._get_timestamped_path(filename, format)

        df = pd.DataFrame(self._get_collection())

        if format == "csv":
            df.to_csv(path, index=False)
        elif format == "xlsx":
            df.to_excel(path, index=False)
        elif format == "json":
            path.write_text(df.to_json(orient="records", indent=2))
        else:
            raise ValueError("Unsupported format. Choose: csv, xlsx, json.")

        return path

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the response data collection to a Pandas DataFrame.

        Returns
        -------
        pd.DataFrame
        """
        return pd.DataFrame(self._get_collection())

    def summary(self, verbose: bool = False, save_as: str = None):
        """
        Print and optionally save an analytics summary of the dataset.
    
        Parameters
        ----------
        verbose : bool
            If True, print a head preview of the data.
        save_as : str, optional
            Path to save the summary text (e.g. "summary.md" or "report.txt").
        """
    
        df = self.to_dataframe()
        out = StringIO()
    
        def p(text=""):
            print(text, file=out)
    
        p("📊 PyDoge Data Summary")
        p("=" * 40)
        p(f"🧾 Rows       : {df.shape[0]}")
        p(f"🧬 Columns    : {df.shape[1]}")
        p(f"🕳️  Total NaNs : {df.isnull().sum().sum()}\n")
    
        p("📑 Column Data Types:")
        p(df.dtypes.to_string())
        p("")
    
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        p("📉 Nulls by Column:")
        p(nulls.to_string() if not nulls.empty else "✅ No null values detected")
        p("")
    
        numeric_cols = df.select_dtypes(include="number").columns
        if not numeric_cols.empty:
            p("📈 Numeric Column Stats:")
            stats = df[numeric_cols].agg(["count", "mean", "std", "min", "max"]).T
            stats = stats[["count", "mean", "std", "min", "max"]]
            p(stats.round(2).to_string())
            p("")
    
        cat_cols = df.select_dtypes(include="object").columns
        if not cat_cols.empty:
            p("🔠 Top Categories:")
            for col in cat_cols:
                top = df[col].value_counts().head(3)
                p(f"\n[{col}]")
                p(top.to_string())
    
        if verbose:
            p("\n📋 Sample Preview:")
            p(df.head().to_string())
    
        # Print to terminal
        print(out.getvalue())
    
        # Optionally save to file
        if save_as:
            with open(save_as, "w", encoding="utf-8") as f:
                f.write(out.getvalue())
                
class DictExportable(dict, ExportMixin):
    """A dict subclass with .export() support"""
    pass

def handle_dict(obj):
    if isinstance(obj, dict) and not hasattr(obj, "export"):
        new_obj = DictExportable(**obj)
        return new_obj
    return obj