# 🏢 Agency-Level Analytics

This page covers the `DogeAnalytics` methods used to rank agencies based on financial metrics like savings, contracts, and leases.

All methods return a ranked `pandas.DataFrame` with the agency name and the aggregated total value.

---

## 💰 `top_agencies_by_savings(top_n=5)`

### Description
Returns the top N agencies by **total reported savings** from the `/savings/grants` endpoint.

### Parameters

| Name   | Type | Description                      |
|--------|------|----------------------------------|
| `top_n`| int  | Number of agencies to return     |

### Returns

`pandas.DataFrame` with columns:

- `agency`
- `savings`

### Example

```python
with DogeAnalytics(fetch_all=True) as da:
    top_savings = da.top_agencies_by_savings(top_n=10)
    print(top_savings)
```


📜 `top_agencies_by_contracts(top_n=5)`
---------------------------------------

### Description

Returns the top N agencies based on **total contract value** from the `/savings/contracts` endpoint.

Assumes the field is named `contract_value` in the API response.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| `top_n` | int | Number of agencies to return |

### Returns

`pandas.DataFrame` with columns:

*   `agency`
*   `savings`
    

### Example

```python
with DogeAnalytics(fetch_all=True) as da:
    top_contracts = da.top_agencies_by_contracts()
    print(top_contracts)
```

🏢 `top_agencies_by_leases(top_n=5)`
------------------------------------

### Description

Returns the top N agencies by **total lease cost** from the `/savings/leases` endpoint.

Assumes the field is named `lease_cost` in the API response.

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| `top_n` | int | Number of agencies to return |

### Returns

`pandas.DataFrame` with columns:

*   `agency`
*   `savings`
    

### Example

```python
with DogeAnalytics(fetch_all=True) as da:
    top_leases = da.top_agencies_by_leases(top_n=3)
    print(top_leases)
```


🔁 Customizing the Aggregation
------------------------------

You can easily write your own metric-based groupings:

```python
df = da.contracts_dataframe()
top = df.groupby("agency")["contract_type_A"].sum().sort_values(ascending=False).head(5)
print(top)
```

* * *

📤 Exporting the Rankings
-------------------------

```python
da.export_dataset(top_savings, "top_savings_by_agency", format="xlsx")
```