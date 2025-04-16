from typing import List, Optional
from pydantic import BaseModel, Field
from ..utils.exporter import ExportMixin

# === PARAM MODELS ===

class GrantParams(BaseModel):
    sort_by: Optional[str] = Field(
        default=None, description="Field to sort by: 'savings', 'value', or 'date'."
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

class ContractParams(BaseModel):
    sort_by: Optional[str] = Field(
        default=None, description="Field to sort by: 'savings', 'value', or 'agency'."
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

class LeaseParams(BaseModel):
    sort_by: Optional[str] = Field(
        default=None, description="Field to sort by: 'sq_ft', 'value', or 'agency'."
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


# === RESPONSE MODELS ===

class Grant(BaseModel):
    date: str = Field(..., description="The cancellation date of the grant")
    agency: str = Field(..., description="The agency that awarded the grant.")
    recipient: str = Field(..., description="The recipient of the grant.")
    value: float = Field(..., description="The dollar value of the grant.")
    savings: float = Field(..., description="The total savings from the cancelled grant.")
    link: Optional[str] = Field(None, description="The link to the grant on usaspending.gov")
    description: Optional[str] = Field(None, description="The description of the grant")

class ResultGrants(BaseModel):
    grants: List[Grant] = Field(..., description="List of cancelled grants.")

class Contract(BaseModel):
    piid: str = Field(..., description="Procurement Instrument Identifier (PIID) of the contract.")
    agency: str = Field(..., description="Agency that issued the contract.")
    vendor: str = Field(..., description="The vendor of the contract")
    value: float = Field(..., description="The value of the contract")
    description: Optional[str] = Field(None, description="The description of the contract")
    fpds_status: Optional[str] = Field(None, description="The status of the contract in FPDS")
    fpds_link: Optional[str] = Field(None, description="The link to the contract in FPDS")
    deleted_date: Optional[str] = Field(None, description="The date the contract was deleted")
    savings: float = Field(..., description="Savings from cancellation.")

class ResultContracts(BaseModel):
    contracts: List[Contract] = Field(..., description="List of cancelled contracts.")

class Lease(BaseModel):
    date: str = Field(..., description="The cancelled date of the lease")
    location: str = Field(..., description="The rough city and state of the lease")
    sq_ft: float = Field(..., description="The square footage of the property")
    description: Optional[str] = Field(None, description="The description of the status of the lease")
    value: float = Field(..., description="The dollar value of the lease for the next year")
    savings: float = Field(..., description="The dollar value remaining on the lease at the time cancellation is effective")
    agency: str = Field(..., description="The agency using the property")

class ResultLeases(BaseModel):
    leases: List[Lease] = Field(..., description="List of terminated or cancelled leases.")

class Meta(BaseModel):
    total_results: int = Field(..., description="The total amount of results")
    pages: int = Field(..., description="The total amount of pages at current per_page limit")

class GrantResponse(BaseModel, ExportMixin):
    success: bool
    result: ResultGrants
    meta: Meta

class ContractResponse(BaseModel, ExportMixin):
    success: bool
    result: ResultContracts
    meta: Meta

class LeaseResponse(BaseModel, ExportMixin):
    success: bool
    result: ResultLeases
    meta: Meta
