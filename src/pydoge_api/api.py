from typing import Optional

from .client import DogeAPIClient
from .endpoints.payments import PaymentsAPI
from .endpoints.savings import SavingsAPI


class DogeAPI:
    """
    Unified entrypoint for interacting with all DOGE endpoints.

    Attributes
    ----------
    client : DogeAPIClient
        Shared client instance used across all endpoint classes.
    savings : SavingsAPI
        Access to /savings endpoints.
    payments : PaymentsAPI
        Access to /payments endpoints.
    """

    def __init__(
        self,
        fetch_all: bool = False,
        output_pydantic: bool = True,
        handle_response: bool = True,
        run_async: bool = False,
        client: Optional[DogeAPIClient] = None,
        **client_kwargs,
    ):
        """
        Initialize DogeAPI with a shared DogeAPIClient and global endpoint config flags.

        Parameters
        ----------
        fetch_all : bool
            Automatically fetch all pages for paginated endpoints.
        output_pydantic : bool
            If True, return Pydantic models. If False, return plain dicts with .export().
        handle_response : bool
            If True, decode responses. If False, return raw httpx.Response.
        run_async : bool
            If True, use asyncio-based pagination (if supported).
        client : DogeAPIClient, optional
            Reuse an existing client. When provided, `close()` will **not** close it
            (the caller owns its lifecycle) and `**client_kwargs` are ignored.
        **client_kwargs : dict
            Passed to DogeAPIClient (e.g. base_url, timeout, headers) when `client`
            is not supplied.
        """
        self.fetch_all = fetch_all
        self.output_pydantic = output_pydantic
        self.handle_response = handle_response
        self.run_async = run_async

        if client is not None:
            self.client = client
            self._owns_client = False
        else:
            self.client = DogeAPIClient(**client_kwargs)
            self._owns_client = True

        self.savings = SavingsAPI(client=self.client, api=self)
        self.payments = PaymentsAPI(client=self.client, api=self)

    def close(self):
        """Close the internal client session (unless an external client was injected)."""
        if self._owns_client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
