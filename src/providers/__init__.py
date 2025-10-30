"""
Data providers for partner search.

This module contains integrations with various data sources:
- Crunchbase (API)
- CB Insights (web scraping)
- LinkedIn (API/web scraping)
- Generic web search
"""

from .base import BaseProvider
from .crunchbase import CrunchbaseProvider
from .cbinsights import CBInsightsProvider
from .linkedin import LinkedInProvider
from .web_search import WebSearchProvider

__all__ = [
    'BaseProvider',
    'CrunchbaseProvider',
    'CBInsightsProvider',
    'LinkedInProvider',
    'WebSearchProvider',
]
