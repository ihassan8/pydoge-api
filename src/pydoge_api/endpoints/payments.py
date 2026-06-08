from typing import TYPE_CHECKING, Optional, Union, cast

import httpx

from ..client import DogeAPIClient
from ..models.payments import PaymentParams, PaymentResponse, PaymentStatisticsResponse
from ..utils.exporter import handle_dict
from ..utils.pagination import _fetch_paginated

if TYPE_CHECKING:
    from ..api import DogeAPI


class PaymentsAPI:
    """
    Access payments-related endpoints (/payments/*).
    """

    def __init__(self, client: DogeAPIClient, api: 'DogeAPI'):
        """
        Parameters
        ----------
        client : DogeAPIClient
            HTTP client instance.
        api : DogeAPI
            Shared config provider for fetch_all, output_pydantic, etc.
        """
        self.client = client
        self.api = api

    def get_payments(
        self,
        *,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        filter: Optional[str] = None,
        filter_value: Optional[str] = None,
        page: int = 1,
        per_page: int = 100,
    ) -> Union[PaymentResponse, dict, httpx.Response]:
        """
        Retrieve payment records made by government agencies.

        Parameters
        ----------
        sort_by : str, optional
            Field to sort by. Options include 'amount' or 'date'.
        sort_order : str, optional
            Sort direction. One of 'asc' or 'desc'.
        filter : str, optional
            Filter key. One of 'agency_name', 'date', or 'org_name'.
        filter_value : str, optional
            The value to filter by.
        page : int, default=1
            Starting page number.
        per_page : int, default=100
            Number of results per page.

        Returns
        -------
        PaymentResponse or dict or httpx.Response
            Pydantic model if `output_pydantic=True`,
            exportable dict if `output_pydantic=False`,
            or raw response if `handle_response=False`.
        """
        params = PaymentParams(
            sort_by=sort_by,
            sort_order=sort_order,
            filter=filter,
            filter_value=filter_value,
            page=page,
            per_page=per_page,
        )
        query = params.model_dump(exclude_none=True)

        result = self.client.get("/payments", params=query, decode=self.api.handle_response)
        if not self.api.handle_response:
            return result

        model = PaymentResponse(**cast(dict, result))

        return _fetch_paginated(
            api=self.api,
            client=self.client,
            endpoint="/payments",
            params=params,
            initial_response=model,
            key="payments",
            model_cls=PaymentResponse,
        )

    def get_statistics(self) -> Union[PaymentStatisticsResponse, dict, httpx.Response]:
        """
        Retrieve aggregate payment statistics (`/payments/statistics`).

        Returns per-agency, per-date, and per-organization payment counts. This
        endpoint is not paginated and carries no ``meta``.

        Returns
        -------
        PaymentStatisticsResponse or dict or httpx.Response
            Pydantic model if `output_pydantic=True`,
            plain dict if `output_pydantic=False`,
            or raw response if `handle_response=False`.
        """
        result = self.client.get("/payments/statistics", decode=self.api.handle_response)
        if not self.api.handle_response:
            return result

        if self.api.output_pydantic:
            return PaymentStatisticsResponse(**cast(dict, result))
        return cast(dict, handle_dict(cast(dict, result)))

