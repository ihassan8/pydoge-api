from math import ceil
from typing import Any, Type, TypeVar, Union

from pydantic import BaseModel

from .async_tools import _fetch_grants_pages, run_async
from .exporter import handle_dict

ModelT = TypeVar("ModelT", bound=BaseModel)


def _fetch_paginated(
    *,
    api,
    client,
    endpoint: str,
    params,
    initial_response: ModelT,
    key: str,
    model_cls: Type[ModelT],
) -> Union[ModelT, dict]:
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
    # `.meta` / `.result` live on the concrete response models, not on the generic
    # BaseModel bound. View the instance as Any for attribute access while keeping the
    # public return type precise (Union[ModelT, dict]).
    resp: Any = initial_response

    if not api.fetch_all or getattr(resp.meta, "pages", 1) <= 1:
        return (
            initial_response if api.output_pydantic
            else handle_dict(resp.model_dump(exclude_none=True))
        )

    all_items = getattr(resp.result, key)
    per_page = params.per_page
    page = params.page
    total_pages = resp.meta.pages

    if api.run_async:
        async def fetch_all():
            return await _fetch_grants_pages(client, endpoint, params, total_pages)

        page_results = run_async(fetch_all())
        for page_data in page_results:
            if not page_data.get("success"):
                raise ValueError(f"API error: {page_data}")
            page_model: Any = model_cls(**page_data)
            all_items.extend(getattr(page_model.result, key))
    else:
        for p in range(page + 1, total_pages + 1):
            params.page = p
            next_data = client.get(endpoint, params=params.model_dump(exclude_none=True), decode=True)
            next_model: Any = model_cls(**next_data)
            all_items.extend(getattr(next_model.result, key))

    # Patch meta
    setattr(resp.result, key, all_items)
    resp.meta.total_results = len(all_items)
    resp.meta.pages = ceil(len(all_items) / per_page)

    return (
        initial_response if api.output_pydantic
        else handle_dict(resp.model_dump(exclude_none=True))
    )
