from pydantic import BaseModel, Field


class Meta(BaseModel):
    """Pagination metadata returned alongside every paginated DOGE response."""

    total_results: int = Field(..., description="The total number of results available.")
    pages: int = Field(..., description="The total number of pages at the current per_page limit.")
