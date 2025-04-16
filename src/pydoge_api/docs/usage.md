# Quickstart Guide


## Get Grants and sorted by savings
```python
from pydoge_api import DogeAPI

with DogeAPI(fetch_all=True, run_async=False) as api:
    grants = api.savings.get_grants(sort_by="savings")
    df = grants.to_dataframe()
    print(df.head())

    # Export to CSV
    grants.export("grants_q1", format="csv")
    
    # Show summary in terminal
    grants.summary(verbose=True)
    
    # Save the summary as markdown
    grants.summary(save_as="logs/grants_summary.md")
```

## Get Contracts and sorted by agency
```python
with DogeAPI(fetch_all=True, run_async=False) as api:
    contracts = api.savings.get_contracts(sort_by="agency")
    df = contracts.to_dataframe()
    print(df.head())

    # Export to CSV
    contracts.export("contracts_q1", format="csv")
    
    # Show summary in terminal
    contracts.summary(verbose=True)
    
    # Save the summary as markdown
    contracts.summary(save_as="logs/contracts_summary.md")
```

## Get Leases
```python
with DogeAPI(fetch_all=True, run_async=False) as api:
    leases = api.savings.get_leases()
    df = leases.to_dataframe()
    print(df.head())
    
    # Export to CSV
    leases.export("leases_q1", format="csv")
    
    # Show summary in terminal
    leases.summary(verbose=True)
    
    # Save the summary as markdown
    leases.summary(save_as="logs/leases_summary.md")
```
    
## Get Payments and filter payments by agency
```python
with DogeAPI(fetch_all=True, run_async=False) as api:
    payments = api.payments.get_payments(filter="agency", filter_value="NASA")
    df =payments.to_dataframe()
    print(df.head())
    
    # Export to CSV
    payments.export("payments_q1", format="csv")
    
    # Show summary in terminal
    payments.summary(verbose=True)
    
    # Save the summary as markdown
    payments.summary(save_as="logs/payments_summary.md")
```

## Without using Context Manager
```python
api = DogeAPI(
    fetch_all=True, # Get all records if True. Default False
    run_async=False # For Async set this to True
)

try:
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
    
finally:
    api.close()
    
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