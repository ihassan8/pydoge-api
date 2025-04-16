"""
DOGE API SDK

Python SDK for interacting with the Department of Government Efficiency (DOGE) APIs.
Provides fully typed, paginated, and export-ready access to savings, payments,
and contract-related endpoints.
"""

from .client import DogeAPIClient, DogeAPIRequestError
from .api import DogeAPI
from .analytic import DogeAnalytics
from .endpoints.savings import SavingsAPI
from .endpoints.payments import PaymentsAPI

__all__ = [
    "DogeAPI",
    "DogeAPIClient",
    "DogeAPIRequestError",
    "DogeAnalytics",
    "SavingsAPI",
    "PaymentsAPI",
]
