"""
Core modules for partner matching pipeline.

Includes:
- Aggregator: Deduplicates and merges company data from multiple sources
- Ranker: Ranks potential partners using LLM-based analysis
"""

from .aggregator import CompanyAggregator, CompanyRecord
from .ranker import PartnerRanker, StartupProfile, PartnerMatch

__all__ = [
    'CompanyAggregator',
    'CompanyRecord',
    'PartnerRanker',
    'StartupProfile',
    'PartnerMatch',
]
