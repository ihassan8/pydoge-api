<div align="center">
<img src="./img/logo_main.PNG" alt="PyDOGE Logo" width= "176">
<p>A Python library to interact with Department of Government Efficiency (DOGE) API.</p>
</div>

<br>

<details open="true">
  <summary><strong> 🧾 Table of Contents</strong></summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#features">Features</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
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
- `savings.all()` — one tidy DataFrame across grants, contracts & leases
- Modern `pydoge` CLI (Typer + Rich) for fetch / export / summary
- Built-in charts (bar, time-series, distribution, US-state choropleth) via the `[viz]` extra
- Secure logging powered by [PyLogShield](https://github.com/ihassan8/pylogshield) (credential scrubbing + on-demand masking)

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

## 👪 Contributors
All contributions are welcome. If you have a suggestion that would make this better, please fork the repo and create a merge request. You can also simply open an issue with the label 'enhancement'.

Don't forget to give the project a star! Thanks again!


## 👏 Acknowledgments
Inspiration, code snippets, etc.
