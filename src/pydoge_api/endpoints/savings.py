from typing import TYPE_CHECKING, Any, Optional, Union, cast

import httpx
import pandas as pd

from ..client import DogeAPIClient
from ..models.savings import ContractParams, ContractResponse, GrantParams, GrantResponse, LeaseParams, LeaseResponse
from ..utils.pagination import _fetch_paginated

if TYPE_CHECKING:
    from ..api import DogeAPI


class SavingsAPI:
    """
    Access all endpoints under /savings including grants, contracts, and leases.

    This class handles paginated retrieval of financial savings data via a shared
    DogeAPIClient. Supports both Pydantic model and dict export modes.
    """

    def __init__(self, client: DogeAPIClient, api: "DogeAPI"):
        """
        Parameters
        ----------
        client : DogeAPIClient
            Shared HTTP client instance for making API calls.
        api : DogeAPI
            Reference to parent DogeAPI instance for runtime config flags.
        """
        self.client = client
        self.api = api

    def get_grants(
        self, *, sort_by: Optional[str] = None, sort_order: Optional[str] = None, page: int = 1, per_page: int = 100
    ) -> Union[GrantResponse, dict, httpx.Response]:
        """
        Retrieve cancelled or reduced government grants.

        Parameters
        ----------
        sort_by : str, optional
            Field to sort by. Options include 'savings', 'value', or 'date'.
        sort_order : str, optional
            Sort direction. One of 'asc' or 'desc'.
        page : int, default=1
            Starting page number for paginated results.
        per_page : int, default=100
            Number of records to retrieve per page.

        Returns
        -------
        GrantResponse or dict or httpx.Response
            Pydantic model if `output_pydantic=True`,
            exportable dict if `output_pydantic=False`,
            or raw response if `handle_response=False`.
        """
        params = GrantParams(sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)

        result = self.client.get("/savings/grants", params=query, decode=self.api.handle_response)
        if not self.api.handle_response:
            return result

        model = GrantResponse(**cast(dict, result))

        return _fetch_paginated(
            api=self.api,
            client=self.client,
            endpoint="/savings/grants",
            params=params,
            initial_response=model,
            key="grants",
            model_cls=GrantResponse,
        )

    def get_contracts(
        self, *, sort_by: Optional[str] = None, sort_order: Optional[str] = None, page: int = 1, per_page: int = 100
    ) -> Union[ContractResponse, dict, httpx.Response]:
        """
        Retrieve cancelled or optimized government contracts.

        Parameters
        ----------
        sort_by : str, optional
            Field to sort by. Options include 'savings', 'value', or 'date'.
        sort_order : str, optional
            Sort direction. One of 'asc' or 'desc'.
        page : int, default=1
            Starting page number for paginated results.
        per_page : int, default=100
            Number of records to retrieve per page.

        Returns
        -------
        ContractResponse or dict or httpx.Response
            Pydantic model if `output_pydantic=True`,
            exportable dict if `output_pydantic=False`,
            or raw response if `handle_response=False`.
        """
        params = ContractParams(sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)

        result = self.client.get("/savings/contracts", params=query, decode=self.api.handle_response)
        if not self.api.handle_response:
            return result

        model = ContractResponse(**cast(dict, result))

        return _fetch_paginated(
            api=self.api,
            client=self.client,
            endpoint="/savings/contracts",
            params=params,
            initial_response=model,
            key="contracts",
            model_cls=ContractResponse,
        )

    def get_leases(
        self, *, sort_by: Optional[str] = None, sort_order: Optional[str] = None, page: int = 1, per_page: int = 100
    ) -> Union[LeaseResponse, dict, httpx.Response]:
        """
        Retrieve terminated or downsized government leases.

        Parameters
        ----------
        sort_by : str, optional
            Field to sort by. Options include 'savings', 'value', or 'date'.
        sort_order : str, optional
            Sort direction. One of 'asc' or 'desc'.
        page : int, default=1
            Starting page number for paginated results.
        per_page : int, default=100
            Number of records to retrieve per page.

        Returns
        -------
        LeaseResponse or dict or httpx.Response
            Pydantic model if `output_pydantic=True`,
            exportable dict if `output_pydantic=False`,
            or raw response if `handle_response=False`.
        """
        params = LeaseParams(sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)

        result = self.client.get("/savings/leases", params=query, decode=self.api.handle_response)
        if not self.api.handle_response:
            return result

        model = LeaseResponse(**cast(dict, result))

        return _fetch_paginated(
            api=self.api,
            client=self.client,
            endpoint="/savings/leases",
            params=params,
            initial_response=model,
            key="leases",
            model_cls=LeaseResponse,
        )

    def all(self, *, parse_dates: bool = True) -> pd.DataFrame:
        """Fetch grants, contracts, and leases into one tidy DataFrame.

        The three savings collections are concatenated and tagged with a ``kind``
        column (``"grant"``, ``"contract"``, or ``"lease"``). Columns that only exist
        on some endpoints (e.g. ``recipient``, ``vendor``, ``location``) are filled
        with ``NaN`` where absent — the natural shape for cross-category analysis such
        as total savings by agency across everything.

        Respects the parent `DogeAPI` flags (`fetch_all`, `output_pydantic`), but
        **requires** `handle_response=True` since it needs parsed data.

        Parameters
        ----------
        parse_dates : bool, default=True
            Coerce date columns to ``datetime64`` (see :meth:`ExportMixin.to_dataframe`).

        Returns
        -------
        pandas.DataFrame
            Combined grants + contracts + leases with a leading ``kind`` column.

        Raises
        ------
        TypeError
            If the API is configured with ``handle_response=False`` (raw responses
            cannot be combined).

        Examples
        --------
        >>> with DogeAPI(fetch_all=True) as api:
        ...     df = api.savings.all()
        >>> df.groupby(["kind", "agency"])["savings"].sum()
        """
        frames = []
        for kind, fetch in (
            ("grant", self.get_grants),
            ("contract", self.get_contracts),
            ("lease", self.get_leases),
        ):
            resp = fetch()
            if not hasattr(resp, "to_dataframe"):
                raise TypeError(
                    "SavingsAPI.all() requires parsed responses; construct DogeAPI with handle_response=True."
                )
            df = cast(Any, resp).to_dataframe(parse_dates=parse_dates)
            df.insert(0, "kind", kind)
            frames.append(df)
        return pd.concat(frames, ignore_index=True)
