"""
Partner Scope - VC Partner Matching Pipeline

A system for finding and ranking potential corporate partners for startups.
"""

__version__ = '0.1.0'

from .pipeline import PartnerPipeline
from .core import StartupProfile, PartnerMatch, CompanyRecord
from .providers import (
    CrunchbaseProvider,
    CBInsightsProvider,
    LinkedInProvider,
    WebSearchProvider,
)

__all__ = [
    'PartnerPipeline',
    'StartupProfile',
    'PartnerMatch',
    'CompanyRecord',
    'CrunchbaseProvider',
    'CBInsightsProvider',
    'LinkedInProvider',
    'WebSearchProvider',
]
