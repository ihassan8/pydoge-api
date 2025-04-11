# 💾 Exporting & Summarizing Data

Every response returned by the PyDoge SDK — whether a Pydantic model or plain dictionary — supports:

- `.export()` — Save data to CSV, Excel, or JSON
- `.to_dataframe()` — Get a Pandas DataFrame
- `.summary()` — See an analytics-style report in terminal

These methods are available on all major responses:
- Grants
- Payments
- Contracts
- Leases

---

## 📤 `.export()`

```python
grants = api.savings.get_grants()
grants.export("grants_q2", format="csv")
grants.export("grants_q2", format="xlsx")
grants.export("grants_q2", format="json")
```
This saves a timestamped file like:

```
grants_q2_20250410_172308.csv
```
✅ Works for both output_pydantic=True and False.


## 📊 `.to_dataframe()`

```python
df = grants.to_dataframe()
print(df.shape)
df.plot("date_closed", "savings")
```
This is helpful for:

- Analytics
- Plotting
- Custom filters

## 📈 `.summary(verbose=True)`

```python
grants.summary()
grants.summary(verbose=True)

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