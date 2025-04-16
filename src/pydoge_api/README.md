<div align="center">
<img src="docs/img/logo_main.PNG" alt="PyDOGE Logo" width= "176">
<p>A Python library to interact with Department of Government Efficiency (DOGE) API.</p>
</div>

<br>

<details open="true">
  <summary><strong> 🧾 Table of Contents</strong></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#highlights">Highlights</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a>
      <ul>
        <li><a href="#get-grants-and-sorted-by-savings">Get Grants and sorted by savings</a></li>
        <li><a href="#get-contracts-and-sorted-by-agency">Get Contracts and sorted by agency</a></li>
        <li><a href="#get-leases">Get Leases</a></li>
        <li><a href="#get-payments-and-filter-payments-by-agency">Get Payments and filter payments by agency</a></li>
        <li><a href="#without-using-context-manager">Without using Context Manager</a></li>
      </ul>
    </li>
    <li><a href="#contributors">Contributors </a></li>
    <li><a href="#acknowledgments">Acknowledgements </a></li>
  </ol>
</details>

## 🐍 About The Project
PyDOGE API is an advanced, Python wrapper for interacting with the public-facing API of the **Department of Government Efficiency (DOGE)** — a federal initiative aimed at increasing transparency and fiscal accountability by sharing detailed datasets on:

- 💸 Cancelled grants
- 📑 Contract terminations
- 🏢 Lease reductions
- 🧾 Payment transactions

## 🚀 Features

- Auto-pagination (sync or async, fetch all pages if needed)
- `.export()` to CSV, Excel, or JSON with timestamped filenames  
- `.to_dataframe()` for Pandas users 
- `.summary()` with analytics (rows, nulls, dtypes, stats)  
- `summary(save_as="...")` for file logging  
- Returns Pydantic models & dict output
- Retry-safe client with 429 handling

This package enables data scientists and analysts to **programmatically access and analyze** the data with ease.

<!--Getting Started-->
## 📌 Getting Started

### Installation

Install:
```bash
pip install pydoge-api
```
Upgrade:
```
pip install --upgrade pydoge-api
```

**Documentation**

Full developer docs with API reference, usage, and model schema:

- 👉 [Docs and Examples (PyDOGE)](https://ihassan8.github.io/pydoge-api/)
- 👉 [Official Swagger Page](https://api.doge.gov/docs)

## 📚 Usage

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
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 👪 Contributors
All contributions are welcome. If you have a suggestion that would make this better, please fork the repo and create a merge request. You can also simply open an issue with the label 'enhancement'.

Don't forget to give the project a star! Thanks again!


## 👏 Acknowledgments
Inspiration, code snippets, etc.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
