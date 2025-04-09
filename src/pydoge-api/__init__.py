from .client import DogeAPIClient
from .endpoints.savings import SavingsEndpoint
from .endpoints.payments import PaymentsEndpoint

class DogeAPI:
    """
    Entry point for the DOGE API SDK.

    Parameters
    ----------
    
    fetch_all: bool
        Automatically fetch all pages (True) or just one page (False).
        
    output_pydantic: bool
        Return data as pydantic models (True) or as plain dicts (False).
        
    handle_response: bool
        If False, return raw httpx.Response.
        
    run_async: bool
        Enable async parallel pagination if True.
    """
    def __init__(self, *, fetch_all=False, output_pydantic=False, handle_response=True, run_async=False):
        self._client = DogeAPIClient()
        self.fetch_all = fetch_all
        self.output_pydantic = output_pydantic
        self.handle_response = handle_response
        self.run_async = run_async
        self.savings = SavingsEndpoint(self._client, self)
        self.payments = PaymentsEndpoint(self._client, self)
