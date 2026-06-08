# 💾 Exporting & Summarizing Data

Every response returned by the PyDoge SDK — whether a Pydantic model or plain dictionary — supports:

- `.export()` — Save data to CSV, Excel, or JSON
- `.to_dataframe()` — Get a Pandas DataFrame
- `.summary()` — Generate analytic summaries: rows, nulls, types, stats

These methods are available on all major responses:
- Grants
- Payments
- Contracts
- Leases

---

## 📤 `.export()`

```python
with DogeAPI(fetch_all=True) as api:
    grants = api.savings.get_grants()
    path = grants.export("grants_q1", format="csv")
    print(f"Saved to: {path}")
```
This saves a timestamped file like:

```
grants_q2_20250410_172308.csv
```

**Supported Formats**
- csv → grants_q1_YYYYMMDD_HHMMSS.csv
- xlsx → Excel spreadsheet
- json → JSON array (records-style)

## 📊 `.to_dataframe()`

Convert any result into a Pandas DataFrame for analysis:

```python
with DogeAPI() as api:
    df = api.savings.get_contracts().to_dataframe()
    print(df.head())
    print(df.shape)
    # e.g. plot the highest-value contracts
    df.nlargest(10, "value").plot.bar(x="vendor", y="savings")
```

!!! tip "Date columns are parsed automatically"
    `to_dataframe()` coerces `date`, `payment_date`, and `deleted_date` from date strings to
    `datetime64` by default — so resampling and time-series plots work immediately. Pass
    `to_dataframe(parse_dates=False)` to keep the raw strings. See
    [Visualization](visualization.md) for charting helpers.
This is helpful for:

- Analytics
- Plotting
- Custom filters

## 📈 `.summary(verbose=True)`

Get a full analytical breakdown of your dataset:

```python
with DogeAPI() as api:
    grants.summary()

    # Show summary in terminal
    grants.summary(verbose=True)

    # Save the summary as markdown
    grants.summary(save_as="logs/grants_summary.md")
```
**Output:**

- Total rows and columns
- Nulls by column
- Dtypes
- Numeric stats (mean, min, max)
- Top categories
- Optional .head() preview

🧪 Example Output

```python
📊 PyDoge Data Summary
========================================
🧾 Rows       : 2450
🧬 Columns    : 8
🕳️  Total NaNs : 17

📑 Column Data Types:
id              int64
agency         object
savings       float64

📉 Nulls by Column:
savings     7
status      10

📈 Numeric Column Stats:
         count      mean      std     min       max
savings  2443.0  151234.3  98231.4  100.0   998500.0

🔠 Top Categories:
[status]
completed     1300
cancelled      900
pending        250

📋 Sample Preview:
   id agency status savings
0   1   NASA   completed  100000.0
...

```