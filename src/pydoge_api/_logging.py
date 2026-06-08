"""Logging backend for PyDOGE API, powered by PyLogShield.

This module is the single place where the SDK obtains its logger. Instead of the
standard library ``logging.getLogger`` it uses
[PyLogShield](https://github.com/ihassan8/pylogshield), so every log record the
client emits automatically benefits from PyLogShield's security features:

- **Context scrubbing** (``enable_context_scrubber=True``) strips cloud credential
  prefixes (``AWS_``, ``AZURE_``, ``GCP_``, ``GOOGLE_``, ``TOKEN``) from records.
- **Sensitive-data masking** is available on demand by passing ``mask=True`` to any
  log call (e.g. ``logger.warning(msg, mask=True)``) — handy when a request URL or
  payload may contain a token or key.

Notes
-----
PyLogShield always writes a log file at ``~/.logs/<name>.log`` (there is no off
switch in its constructor). Pass ``log_directory`` / ``add_console`` through
:func:`get_logger` to change that behaviour.
"""

from __future__ import annotations

from typing import Any, Optional

from pylogshield import get_logger as _pls_get_logger
from pylogshield.core import PyLogShield

DEFAULT_LOGGER_NAME = "pydoge_api"


def get_logger(name: str = DEFAULT_LOGGER_NAME, **kwargs: Any) -> PyLogShield:
    """Return the PyLogShield logger used by the SDK.

    Parameters
    ----------
    name : str, optional
        Logger name. Defaults to ``"pydoge_api"``.
    **kwargs : Any
        Forwarded to :func:`pylogshield.get_logger` /
        :class:`pylogshield.core.PyLogShield` on first creation — e.g.
        ``log_level``, ``enable_json``, ``add_console``, ``log_directory``,
        ``use_queue``. Ignored on subsequent calls that return the cached
        instance for ``name``.

    Returns
    -------
    pylogshield.core.PyLogShield
        A configured, reusable logger instance.

    Examples
    --------
    >>> from pydoge_api._logging import get_logger
    >>> log = get_logger(log_level="DEBUG")
    >>> log.info("request sent")
    """
    kwargs.setdefault("enable_context_scrubber", True)
    return _pls_get_logger(name, **kwargs)


class _LazyLogger:
    """Defers PyLogShield creation until the first log call.

    PyLogShield opens a log file (``~/.logs/<name>.log``) and attaches handlers in
    its constructor. Creating it eagerly at import time would give every
    ``import pydoge_api`` those filesystem/console side effects. This proxy holds
    off until something is actually logged, so a happy-path run that emits no log
    records never touches the filesystem.
    """

    __slots__ = ()
    _instance: Optional[PyLogShield] = None

    def _resolve(self) -> PyLogShield:
        if _LazyLogger._instance is None:
            _LazyLogger._instance = get_logger()
        return _LazyLogger._instance

    def __getattr__(self, name: str) -> Any:
        return getattr(self._resolve(), name)


#: Module-level logger shared across the SDK's internal modules (lazily created).
logger = _LazyLogger()
