from math import ceil
from ..client import DogeAPIClient
from ..models.savings import (
    GrantParams, GrantResponse,
    ContractParams, ContractResponse,
    LeaseParams, LeaseResponse
)
#import asyncio
from ..utils.runner import run_async, _fetch_grants_pages
from ..utils.exporter import handle_dict
# =============================================================================
# async def _fetch_grants_pages(endpoint, params_obj, total_pages):
#     async with httpx.AsyncClient(base_url="https://api.doge.gov") as client:
#         tasks = []
#         for p in range(2, total_pages + 1):
#             params_obj.page = p
#             clean_query = params_obj.model_dump(exclude_none=True)
#             tasks.append(client.get(endpoint, params=clean_query))
#         responses = await asyncio.gather(*tasks)
#         return [r.json() for r in responses]
# =============================================================================

class SavingsEndpoint:
    """
    Grants, contracts and leases the Department of Government Efficiency has cancelled.
    """

    def __init__(self, client: DogeAPIClient, api: 'DogeAPI'):
        self.client = client
        self.api = api

    def get_grants(self, *, sort_by=None, sort_order=None, page=1, per_page=100):
        """
        Retrieve canceled government grants.
    
        Parameters
        ----------
        
        sort_by : str, optional
            Field to sort by: 'savings', 'value', or 'date'.
            
        sort_order : str, optional
            Sort order direction: 'asc' or 'desc'.
            
        page : int, optional
            Page number to start from (default: 1).
            
        per_page : int, optional
            Number of results per page (default: 100).
    
        Returns
        -------
        
        GrantResponse | dict | httpx.Response
            Parsed model, raw dict, or raw response depending on DogeAPI config.
        """
        fetch_all = self.api.fetch_all
        output_pydantic = self.api.output_pydantic
        handle_response = self.api.handle_response
        run_async_flag = self.api.run_async

        params = GrantParams(sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)
        result = self.client.get("/savings/grants", query, handle_response)

        if not handle_response:
            return result

        response = GrantResponse(**result)

        if not fetch_all or response.meta.pages <= 1:
            if output_pydantic:
                return response 
            else: 
                return handle_dict(response.model_dump(exclude_none=True))

        if run_async_flag:
            data_pages = run_async(_fetch_grants_pages("/savings/grants", params, response.meta.pages))
            for page_data in data_pages:
                if not page_data.get("success"):
                    raise ValueError(f"API returned error: {page_data}")
                next_response = GrantResponse(**page_data)
                response.result.grants.extend(next_response.result.grants)
        else:
            for p in range(page + 1, response.meta.pages + 1):
                params.page = p
                next_data = self.client.get("/savings/grants", params.model_dump(exclude_none=True), handle_response)
                next_response = GrantResponse(**next_data)
                response.result.grants.extend(next_response.result.grants)

        response.meta.total_results = len(response.result.grants)
        response.meta.pages = ceil(len(response.result.grants) / per_page)
        if output_pydantic:
            return response 
        else: 
            return handle_dict(response.model_dump(exclude_none=True))

    def get_contracts(self, *, sort_by=None, sort_order=None, page=1, per_page=100):
        """
        Retrieve canceled government contracts.

        Parameters
        ----------
        
        sort_by : str, optional
            Field to sort by. Options: 'savings', 'value', or 'agency'.
            
        sort_order : str, optional
            Sort direction: 'asc' or 'desc'.
            
        page : int, optional
            Page number to retrieve (default is 1).
            
        per_page : int, optional
            Number of results per page (default is 100).

        Returns
        -------
        
        ContractResponse | dict | httpx.Response
            Parsed model, raw dict, or raw response depending on DogeAPI config.
        """
        fetch_all = self.api.fetch_all
        output_pydantic = self.api.output_pydantic
        handle_response = self.api.handle_response
        run_async_flag = self.api.run_async

        params = ContractParams(sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)
        result = self.client.get("/savings/contracts", query, handle_response)

        if not handle_response:
            return result

        response = ContractResponse(**result)

        if not fetch_all or response.meta.pages <= 1:
            if output_pydantic:
                return response 
            else: 
                return handle_dict(response.model_dump(exclude_none=True))

        if run_async_flag:
            data_pages = run_async(_fetch_grants_pages("/savings/contracts", params, response.meta.pages))
            for page_data in data_pages:
                if not page_data.get("success"):
                    raise ValueError(f"API returned error: {page_data}")
                next_response = ContractResponse(**page_data)
                response.result.contracts.extend(next_response.result.contracts)
        else:
            for p in range(page + 1, response.meta.pages + 1):
                params.page = p
                next_data = self.client.get("/savings/contracts", params.model_dump(exclude_none=True), handle_response)
                next_response = ContractResponse(**next_data)
                response.result.contracts.extend(next_response.result.contracts)
                

        response.meta.total_results = len(response.result.contracts)
        response.meta.pages = ceil(len(response.result.contracts) / per_page)
        
        if output_pydantic:
            return response 
        else: 
            return handle_dict(response.model_dump(exclude_none=True))

    def get_leases(self, *, sort_by=None, sort_order=None, page=1, per_page=100):
        """
        Retrieve canceled or terminated government leases.

        Parameters
        ----------
        
        sort_by : str, optional
            Field to sort by. Options: 'sq_ft', 'value', or 'agency'.
            
        sort_order : str, optional
            Sort direction: 'asc' or 'desc'.
            
        page : int, optional
            Page number to retrieve (default is 1).
            
        per_page : int, optional
            Number of results per page (default is 100).

        Returns
        -------
        
        LeaseResponse | dict | httpx.Response
            Parsed model, raw dict, or raw response depending on DogeAPI config.
        """
        fetch_all = self.api.fetch_all
        output_pydantic = self.api.output_pydantic
        handle_response = self.api.handle_response
        run_async_flag = self.api.run_async

        params = LeaseParams(sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page)
        query = params.model_dump(exclude_none=True)
        result = self.client.get("/savings/leases", query, handle_response)

        if not handle_response:
            return result

        response = LeaseResponse(**result)

        if not fetch_all or response.meta.pages <= 1:
            if output_pydantic:
                return response 
            else: 
                return handle_dict(response.model_dump(exclude_none=True))
        
        if run_async_flag:
            data_pages = run_async(_fetch_grants_pages("/savings/leases", params, response.meta.pages))
            for page_data in data_pages:
                if not page_data.get("success"):
                    raise ValueError(f"API returned error: {page_data}")
                next_response = LeaseResponse(**page_data)
                response.result.leases.extend(next_response.result.leases)
        else:
            for p in range(page + 1, response.meta.pages + 1):
                params.page = p
                next_data = self.client.get("/savings/leases", params.model_dump(exclude_none=True), handle_response)
                next_response = LeaseResponse(**next_data)
                response.result.leases.extend(next_response.result.leases)

        response.meta.total_results = len(response.result.leases)
        response.meta.pages = ceil(len(response.result.leases) / per_page)

        if output_pydantic:
            return response 
        else: 
            return handle_dict(response.model_dump(exclude_none=True))
