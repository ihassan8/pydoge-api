# 🔒 Logging

PyDOGE API logs through [PyLogShield](https://github.com/ihassan8/pylogshield) rather than
the bare standard library. You get secure logging for free: cloud-credential scrubbing on
every record and opt-in masking of sensitive values.

The SDK's internal client emits log records (retries, network errors, max-retry failures)
through a single shared logger named `pydoge_api`. You can reuse and configure that same
logger in your own code.

---

## How it works

- The logger is created **lazily** — on the first log call, not at import time. Simply
  running `import pydoge_api` has no filesystem or console side effects.
- On first use, PyLogShield writes a log file at `~/.logs/pydoge_api.log` **and** prints to
  the console. Pass `log_directory` / `add_console=False` to change this (see below).
- `enable_context_scrubber=True` is on by default, so any `AWS_`, `AZURE_`, `GCP_`,
  `GOOGLE_`, or `TOKEN` prefixed values are stripped from records automatically.

---

## Getting the logger

```python
from pydoge_api._logging import get_logger

# Returns the same singleton "pydoge_api" logger the SDK uses internally.
log = get_logger()
log.info("Fetching savings data")
```

`get_logger(name="pydoge_api", **kwargs)` forwards any keyword arguments to PyLogShield on
first creation. Common options:

| Option | Description |
|--------|-------------|
| `log_level` | `"DEBUG"`, `"INFO"`, … (default `INFO`) |
| `add_console` | Print to the console (default `True`) |
| `log_directory` | Directory for the log file (default `~/.logs`) |
| `log_file` | Log file name (default `<name>.log`) |
| `enable_json` | Emit structured JSON instead of plain text |
| `use_rich` | Pretty console output via `rich` |
| `enable_context_scrubber` | Strip cloud-credential prefixes (default `True`) |

!!! note
    Options only take effect the **first** time a logger of a given name is created;
    later `get_logger("pydoge_api")` calls return the existing instance.

---

## Masking sensitive values

Pass `mask=True` to any log call to redact `key=value` / `key: value` secrets in the
message string:

```python
log = get_logger()
log.warning("requesting with api_key=SECRET123", mask=True)
# -> requesting with api_key=***
```

---

## Quieter, file-only logging

```python
from pydoge_api._logging import get_logger

log = get_logger(add_console=False, log_directory="./logs", log_level="WARNING")
```

## Structured JSON logging

Useful for shipping logs to ELK, Splunk, or CloudWatch:

```python
from pydoge_api._logging import get_logger

log = get_logger(enable_json=True)
log.info("savings fetch complete", extra={"rows": 2450})
```

---

## Routing the SDK's own logs

Because the SDK logs to the `pydoge_api` logger, configuring it before your first call lets
you control how the client's retry/error messages are emitted:

```python
from pydoge_api import DogeAPI
from pydoge_api._logging import get_logger

# Configure once, up front (e.g. JSON, no console noise).
get_logger(enable_json=True, add_console=False)

with DogeAPI(fetch_all=True) as api:
    grants = api.savings.get_grants(sort_by="savings")
```

For the full set of PyLogShield features (rate limiting, rotation, async queues, context
propagation, FastAPI middleware), see the
[PyLogShield documentation](https://ihassan8.github.io/pylogshield).
