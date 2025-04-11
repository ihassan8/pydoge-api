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

grants = api.savings.get_grants(sort_by="savings")
payments = api.payments.get_payments(filter="agency", filter_value="GSA")

# Export to CSV
grants.export("grants_q1", format="csv")
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