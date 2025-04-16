from math import ceil
from .async_tools import run_async, _fetch_grants_pages
from .exporter import handle_dict


def _fetch_paginated(
    *,
    api,
    client,
    endpoint: str,
    params,
    initial_response,
    key: str,
    model_cls
):
    """
    DRY pagination logic for any savings endpoint.

    Parameters
    ----------
    api : DogeAPI
        Source of runtime flags.
    client : DogeAPIClient
        Used to perform .get requests.
    endpoint : str
        Full API route (e.g. "/savings/grants").
    params : BaseModel
        Pydantic model for request query.
    initial_response : Pydantic model
        Page 1 already parsed response.
    key : str
        Attribute under `.result` (e.g. "grants").
    model_cls : Type[BaseModel]
        The Pydantic model to instantiate each page.

    Returns
    -------
    Pydantic or dict
        Final paginated merged response.
    """
    if not api.fetch_all or getattr(initial_response.meta, "pages", 1) <= 1:
        return (
            initial_response if api.output_pydantic
            else handle_dict(initial_response.model_dump(exclude_none=True))
        )

    all_items = getattr(initial_response.result, key)
    per_page = params.per_page
    page = params.page
    total_pages = initial_response.meta.pages

    if api.run_async:
        async def fetch_all():
            return await _fetch_grants_pages(endpoint, params, total_pages)

        page_results = run_async(fetch_all())
        for page_data in page_results:
            if not page_data.get("success"):
                raise ValueError(f"API error: {page_data}")
            page_model = model_cls(**page_data)
            all_items.extend(getattr(page_model.result, key))
    else:
        for p in range(page + 1, total_pages + 1):
            params.page = p
            next_data = client.get(endpoint, params=params.model_dump(exclude_none=True), decode=True)
            next_model = model_cls(**next_data)
            all_items.extend(getattr(next_model.result, key))

    # Patch meta
    setattr(initial_response.result, key, all_items)
    initial_response.meta.total_results = len(all_items)
    initial_response.meta.pages = ceil(len(all_items) / per_page)

    return (
        initial_response if api.output_pydantic
        else handle_dict(initial_response.model_dump(exclude_none=True))
    )
