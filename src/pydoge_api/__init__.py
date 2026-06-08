"""
DOGE API SDK

Python SDK for interacting with the Department of Government Efficiency (DOGE) APIs.
Provides fully typed, paginated, and export-ready access to savings, payments,
and contract-related endpoints.
"""

from .analytic import DogeAnalytics
from .api import DogeAPI
from .client import DogeAPIClient, DogeAPIRequestError
from .endpoints.payments import PaymentsAPI
from .endpoints.savings import SavingsAPI

__all__ = [
    "DogeAPI",
    "DogeAPIClient",
    "DogeAPIRequestError",
    "DogeAnalytics",
    "SavingsAPI",
    "PaymentsAPI",
]
