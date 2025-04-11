# Quickstart Guide

## Standard Synchronous Usage

```python
from pydoge_api import DogeAPI

api = DogeAPI(
    fetch_all=True,
    output_pydantic=False,
    handle_response=True,
    run_async=False
)

# Get Grants and sorted by savings
grants = api.savings.get_grants(sort_by="savings")

# Get Contracts and sorted by agency
contracts = api.savings.get_contracts(sort_by="agency")

# Get Leases
leases = api.savings.get_leases()

# Get Payments and filter payments by agency
payments = api.payments.get_payments(filter="agency", filter_value="NASA")

# Export to CSV
grants.export("grants_q1", format="csv")

# Show summary in terminal
grants.summary(verbose=True)

# Save the summary as markdown
grants.summary(save_as="logs/grants_summary.md")
```

## Async Usage Example

```python
api = DogeAPI(
    fetch_all=True,
    output_pydantic=True,
    run_async=True
)

grants = api.savings.get_grants(sort_by="value")

grants.export("grants_report", format="xlsx")
```

## Config Flags

|Flag|Description|
|----|-----------|
|fetch_all|	Fetch all paginated results|
|output_pydantic|Return Pydantic models if True|
|handle_response|Return parsed data or raw httpx.Response|
|run_async|Use async parallel fetching if True|

## Export Formats

```python
response.export("filename", format="csv")
response.export("filename", format="xlsx")
response.export("filename", format="json")
```