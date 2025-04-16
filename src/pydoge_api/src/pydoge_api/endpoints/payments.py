from math import ceil
from ..client import DogeAPIClient
from ..models.payments import PaymentParams, PaymentResponse
from ..utils.pagination import _fetch_paginated

from typing import Optional


class PaymentsAPI(DogeAPIClient):
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
        agency: Optional[str] = None,
        year: Optional[int] = None,
        page: int = 1,
        per_page: int = 100,
    ):
        """
        Retrieve payment records made by government agencies.

        Parameters
        ----------
        agency : str, optional
            Filter by agency name.
        year : int, optional
            Filter by transaction year.
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
        params = PaymentParams(agency=agency, year=year, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)

        result = self.client.get("/payments", params=query, decode=self.api.handle_response)
        if not self.api.handle_response:
            return result

        model = PaymentResponse(**result)

        return _fetch_paginated(
            api=self.api,
            client=self.client,
            endpoint="/payments",
            params=params,
            initial_response=model,
            key="payments",
            model_cls=PaymentResponse,
        )


