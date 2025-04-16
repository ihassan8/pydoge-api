from typing import Optional
from ..client import DogeAPIClient
from ..models.savings import (
    GrantParams, GrantResponse,
    ContractParams, ContractResponse,
    LeaseParams, LeaseResponse
)
from ..utils.pagination import _fetch_paginated
from ..utils.exporter import handle_dict


class SavingsAPI:
    """
    Access all endpoints under /savings including grants, contracts, and leases.

    This class handles paginated retrieval of financial savings data via a shared
    DogeAPIClient. Supports both Pydantic model and dict export modes.
    """

    def __init__(self, client: DogeAPIClient, api: 'DogeAPI'):
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
        self,
        *,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        per_page: int = 100
    ):
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

        model = GrantResponse(**result)

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
        self,
        *,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        per_page: int = 100
    ):
        """
        Retrieve cancelled or optimized government contracts.

        Parameters
        ----------
        sort_by : str, optional
            Field to sort by. Options include 'savings', 'value', or 'agency'.
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

        model = ContractResponse(**result)

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
        self,
        *,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        per_page: int = 100
    ):
        """
        Retrieve terminated or downsized government leases.

        Parameters
        ----------
        sort_by : str, optional
            Field to sort by. Options include 'sq_ft', 'value', or 'agency'.
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

        model = LeaseResponse(**result)

        return _fetch_paginated(
            api=self.api,
            client=self.client,
            endpoint="/savings/leases",
            params=params,
            initial_response=model,
            key="leases",
            model_cls=LeaseResponse,
        )

