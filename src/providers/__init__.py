"""
Data providers for partner search.

This module contains integrations with various data sources:
- Crunchbase (API)
- CB Insights (web scraping)
- LinkedIn (API/web scraping)
- Generic web search
- OpenAI Web Search (5-phase deep research)
"""

from .base import BaseProvider
from .crunchbase import CrunchbaseProvider
from .cbinsights import CBInsightsProvider
from .linkedin import LinkedInProvider
from .web_search import WebSearchProvider
from .mock_crunchbase import MockCrunchbaseProvider
from .openai_web_search import OpenAIWebSearchProvider

__all__ = [
    'BaseProvider',
    'CrunchbaseProvider',
    'MockCrunchbaseProvider',
    'CBInsightsProvider',
    'LinkedInProvider',
    'WebSearchProvider',
    'OpenAIWebSearchProvider',
]
