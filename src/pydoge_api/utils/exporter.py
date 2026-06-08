from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import BaseModel

from .._logging import logger

#: Columns the DOGE API returns as date strings. They are coerced to ``datetime64``
#: by :meth:`ExportMixin.to_dataframe` so time-series analysis and plotting work out
#: of the box. (``date`` — grants/leases; ``payment_date`` — payments;
#: ``deleted_date`` — contracts.)
DATE_COLUMNS = ("date", "payment_date", "deleted_date")


def _coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert known date columns in ``df`` to ``datetime64`` (unparseable -> NaT)."""
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


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

        logger.info(f"💾 Exported {len(df)} rows to {path}")
        return path

    def to_dataframe(self, parse_dates: bool = True) -> pd.DataFrame:
        """
        Convert the response data collection to a Pandas DataFrame.

        Parameters
        ----------
        parse_dates : bool, default=True
            If True, coerce known date columns (``date``, ``payment_date``,
            ``deleted_date``) from date strings to ``datetime64``. Unparseable
            values become ``NaT``. Set False to keep the raw string columns.

        Returns
        -------
        pd.DataFrame
        """
        df = pd.DataFrame(self._get_collection())
        if parse_dates:
            df = _coerce_dates(df)
        logger.debug(f"to_dataframe: {len(df)} rows × {len(df.columns)} columns (parse_dates={parse_dates})")
        return df

    def summary(self, verbose: bool = False, save_as: Optional[str] = None, to_stdout: bool = True) -> str:
        """
        Build, optionally print, and optionally save an analytics summary of the dataset.

        Parameters
        ----------
        verbose : bool
            If True, include a head preview of the data.
        save_as : str, optional
            Path to save the summary text (e.g. "summary.md" or "report.txt").
        to_stdout : bool, default=True
            If True, print the summary to stdout. Set False to capture it silently
            via the return value.

        Returns
        -------
        str
            The rendered summary text.
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

        # Categorical-ish columns = everything that isn't numeric or datetime. Using
        # `exclude` (rather than `include="object"`) is stable across pandas 2/3, where
        # string columns are migrating off the `object` dtype.
        cat_cols = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns
        if not cat_cols.empty:
            p("🔠 Top Categories:")
            for col in cat_cols:
                top = df[col].value_counts().head(3)
                p(f"\n[{col}]")
                p(top.to_string())

        if verbose:
            p("\n📋 Sample Preview:")
            p(df.head().to_string())

        text = out.getvalue()

        if to_stdout:
            print(text)

        # Optionally save to file
        if save_as:
            with open(save_as, "w", encoding="utf-8") as f:
                f.write(text)

        return text


class DictExportable(dict, ExportMixin):
    """A dict subclass with .export() support"""

    pass


def handle_dict(obj):
    if isinstance(obj, dict) and not hasattr(obj, "export"):
        new_obj = DictExportable(**obj)
        return new_obj
    return obj
