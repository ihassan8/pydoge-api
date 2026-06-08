"""Tests for the PyLogShield-backed logging shim."""

from __future__ import annotations

from pylogshield.core import PyLogShield

from pydoge_api._logging import get_logger, logger


def test_module_logger_proxies_to_pylogshield():
    # `logger` is a lazy proxy; touching an attribute resolves the real logger.
    assert logger.name == "pydoge_api"


def test_get_logger_returns_pylogshield(tmp_path):
    log = get_logger("pydoge_test_logger", log_directory=str(tmp_path), add_console=False)
    assert isinstance(log, PyLogShield)
    # Should not raise — exercises the configured handlers.
    log.info("hello from tests")


def test_get_logger_is_cached():
    first = get_logger("pydoge_cached_logger")
    second = get_logger("pydoge_cached_logger")
    assert first is second
