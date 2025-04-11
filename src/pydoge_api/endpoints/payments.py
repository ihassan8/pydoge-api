from math import ceil
from ..client import DogeAPIClient
from ..models.payments import PaymentParams, PaymentResponse
from ..utils.runner import run_async, _fetch_grants_pages
from ..utils.exporter import handle_dict

class PaymentsEndpoint:
    """
    Payments made by the US Government. Currently, this includes a limited amount of grant payments issued from the Program Support Center, but will expand to include all payments from the US Government..
    """

    def __init__(self, client: DogeAPIClient, api: 'DogeAPI'):
        self.client = client
        self.api = api

    def get_payments(self, *, sort_by=None, sort_order=None, page=1, per_page=100,
                     filter=None, filter_value=None):
        """
        Retrieve government payments with optional filtering and pagination.

        Parameters
        ----------
        
        sort_by : str, optional
            Field to sort by. Options include 'amount', 'post_date', etc.
            
        sort_order : str, optional
            Sort order direction: 'asc' or 'desc'.
            
        page : int, optional
            Page number to fetch (default is 1).
            
        per_page : int, optional
            Items per page to return (default 100, max 500).
            
        filter : str, optional
            Optional filter key (e.g. 'agency').
            
        filter_value : str, optional
            Value to filter results by.

        Returns
        -------
        
        PaymentResponse | dict | httpx.Response
            Parsed Pydantic model if `output_pydantic=True`, raw dict otherwise,
            or `httpx.Response` if `handle_response=False`.
        """
        fetch_all = self.api.fetch_all
        output_pydantic = self.api.output_pydantic
        handle_response = self.api.handle_response
        run_async_flag = self.api.run_async

        params = PaymentParams(
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page,
            filter=filter,
            filter_value=filter_value
        )

        query = params.model_dump(exclude_none=True)
        result = self.client.get("/payments", query, handle_response)

        if not handle_response:
            return result

        response = PaymentResponse(**result)

        if not fetch_all or response.meta.pages <= 1:
            if output_pydantic:
                return response 
            else: 
                return handle_dict(response.model_dump(exclude_none=True))

        if run_async_flag:
            data_pages = run_async(_fetch_grants_pages("/payments", params, response.meta.pages))
            for page_data in data_pages:
                if not page_data.get("success"):
                    raise ValueError(f"API returned error: {page_data}")
                next_response = PaymentResponse(**page_data)
                response.result.payments.extend(next_response.result.payments)
        else:
            for p in range(page + 1, response.meta.pages + 1):
                params.page = p
                next_data = self.client.get("/payments", params.model_dump(exclude_none=True), handle_response)
                next_response = PaymentResponse(**next_data)
                response.result.payments.extend(next_response.result.payments)

        response.meta.total_results = len(response.result.payments)
        response.meta.pages = ceil(len(response.result.payments) / per_page)

        if output_pydantic:
            return response 
        else: 
            return handle_dict(response.model_dump(exclude_none=True))

