# 🏢 Agency-Level Analytics

This page covers the `DogeAnalytics` methods used to rank agencies by financial metrics.
All of them return a ranked `pandas.DataFrame`.

!!! note
    `top_agencies_by_savings`, `top_agencies_by_contracts`, and `top_agencies_by_leases`
    all aggregate the **`savings`** field of their respective endpoints — the dollar value
    saved by the cancellation/termination.

---

## 💰 `top_agencies_by_savings(top_n=10)`

### Description
Returns the top N agencies by **total reported savings** from `/savings/grants`.

### Parameters

| Name   | Type | Description                  |
|--------|------|------------------------------|
| `top_n`| int  | Number of agencies to return |

### Returns

`pandas.DataFrame` with columns `Agency`, `Total Savings`.

### Example

```python
with DogeAnalytics(fetch_all=True) as da:
    top_savings = da.top_agencies_by_savings(top_n=10)
    print(top_savings)
```

---

## 📜 `top_agencies_by_contracts(top_n=10)`

### Description
Returns the top N agencies by **total contract savings** from `/savings/contracts`
(rows with a null `savings` value are dropped before aggregating).

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| `top_n` | int | Number of agencies to return |

### Returns

`pandas.DataFrame` with columns `agency`, `savings`.

### Example

```python
with DogeAnalytics(fetch_all=True) as da:
    top_contracts = da.top_agencies_by_contracts()
    print(top_contracts)
```

---

## 🏢 `top_agencies_by_leases(top_n=10)`

### Description
Returns the top N agencies by **total lease savings** from `/savings/leases`
(rows with a null `savings` value are dropped before aggregating).

### Parameters

| Name | Type | Description |
| --- | --- | --- |
| `top_n` | int | Number of agencies to return |

### Returns

`pandas.DataFrame` with columns `agency`, `savings`.

### Example

```python
with DogeAnalytics(fetch_all=True) as da:
    top_leases = da.top_agencies_by_leases(top_n=3)
    print(top_leases)
```

---

## 🔁 Customizing the Aggregation

`DogeAnalytics` exposes the underlying `SavingsAPI` as `.savings`, so you can build your
own groupings from a full DataFrame:

```python
with DogeAnalytics(fetch_all=True) as da:
    df = da.savings.get_contracts().to_dataframe()
    top_vendors = df.groupby("vendor")["savings"].sum().sort_values(ascending=False).head(5)
    print(top_vendors)
```

---

## 📤 Exporting the Rankings

```python
da.export_dataset(top_savings, "top_savings_by_agency", format="xlsx")
```
