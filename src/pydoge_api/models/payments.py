from typing import Optional, List
from pydantic import BaseModel, Field
from ..utils.exporter import ExportMixin

class PaymentParams(BaseModel):
    sort_by: Optional[str] = Field(
        default=None, description="Field to sort by. Options include 'amount', 'post_date'."
    )
    sort_order: Optional[str] = Field(
        default=None, description="Sort direction: 'asc' or 'desc'."
    )
    page: Optional[int] = Field(
        default=1, description="Page number to retrieve."
    )
    per_page: Optional[int] = Field(
        default=100, description="The number of items per page from 1 to 500 (max: 500)."
    )
    filter: Optional[str] = Field(
        default=None, description="Filter key (e.g. 'agency', 'org_name', or 'post_date')."
    )
    filter_value: Optional[str] = Field(
        default=None, description="The value to filter by"
    )

class Payment(BaseModel):
    agency: str = Field(..., description="The agency which made this payment")
    org_name: str = Field(..., description="Who made this payment")
    description: Optional[str] = Field(None, description="A description of this payment, if available")
    amount: float = Field(..., description="The dollar value of the payment")
    post_date: str = Field(..., description="The date the payment was posted")
    status_description: Optional[str] = Field(None, description="The status of this payment")

class ResultPayments(BaseModel):
    payments: List[Payment] = Field(..., description="List of payment records.")

class Meta(BaseModel):
    total_results: int = Field(..., description="Total number of results available.")
    pages: int = Field(..., description="Total number of pages available.")

class PaymentResponse(BaseModel, ExportMixin):
    success: bool
    result: ResultPayments
    meta: Meta
