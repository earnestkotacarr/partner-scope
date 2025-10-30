"""
Company data aggregator and deduplicator.

This module takes company data from multiple providers and:
1. Identifies duplicate companies across sources
2. Merges information from multiple sources
3. Produces a unified list of unique companies
"""
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
import re
from urllib.parse import urlparse


@dataclass
class CompanyRecord:
    """
    Unified company record aggregated from multiple sources.
    """
    name: str
    website: str = ""
    description: str = ""
    industry: str = ""
    size: str = ""
    location: str = ""
    linkedin_url: str = ""
    twitter_url: str = ""
    facebook_url: str = ""
    instagram_url: str = ""
    contact_info: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)  # List of provider names
    raw_data_by_source: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    confidence_score: float = 0.0  # How confident we are in the match

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'website': self.website,
            'description': self.description,
            'industry': self.industry,
            'size': self.size,
            'location': self.location,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'facebook_url': self.facebook_url,
            'instagram_url': self.instagram_url,
            'contact_info': self.contact_info,
            'sources': self.sources,
            'confidence_score': self.confidence_score,
        }


class CompanyAggregator:
    """
    Aggregates and deduplicates company data from multiple providers.
    """

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize aggregator.

        Args:
            similarity_threshold: Threshold for considering two companies as duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold

    def aggregate(self, company_lists: Dict[str, List[Dict[str, Any]]]) -> List[CompanyRecord]:
        """
        Aggregate company data from multiple providers.

        Args:
            company_lists: Dictionary mapping provider name to list of companies
                          e.g., {'crunchbase': [...], 'cbinsights': [...]}

        Returns:
            List of deduplicated CompanyRecord objects
        """
        # TODO: Flatten all companies into a single list with source tracking
        # TODO: Sort companies to process in consistent order
        # TODO: Group companies that are likely duplicates
        # TODO: Merge duplicate companies using merge_companies()
        # TODO: Calculate confidence scores based on:
        #   - Number of sources confirming the company
        #   - Completeness of information
        #   - Consistency across sources
        # TODO: Return deduplicated list

        raise NotImplementedError("Company aggregation not yet implemented")

    def are_duplicates(self, company1: Dict[str, Any], company2: Dict[str, Any]) -> bool:
        """
        Determine if two company records are duplicates.

        Args:
            company1: First company dictionary
            company2: Second company dictionary

        Returns:
            True if companies are likely duplicates
        """
        # TODO: Compare companies using multiple signals:
        #   1. Exact website domain match (strongest signal)
        #   2. Company name similarity (fuzzy matching)
        #   3. LinkedIn URL match
        #   4. Location + name combination
        # TODO: Use weighted scoring approach
        # TODO: Return True if similarity score > threshold

        raise NotImplementedError("Duplicate detection not yet implemented")

    def merge_companies(self, companies: List[Dict[str, Any]]) -> CompanyRecord:
        """
        Merge multiple company records that represent the same company.

        Args:
            companies: List of company dictionaries to merge

        Returns:
            Merged CompanyRecord
        """
        # TODO: Select best value for each field:
        #   - Prefer non-empty values
        #   - For conflicts, prefer data from more reliable sources
        #   - Concatenate descriptions if different
        #   - Union all social media URLs
        #   - Merge contact information
        # TODO: Track all sources
        # TODO: Calculate confidence score

        raise NotImplementedError("Company merging not yet implemented")

    def normalize_domain(self, url: str) -> str:
        """
        Normalize a website URL to its domain for comparison.

        Args:
            url: Website URL

        Returns:
            Normalized domain (e.g., "example.com")
        """
        # TODO: Parse URL and extract domain
        # TODO: Remove www. prefix
        # TODO: Convert to lowercase
        # TODO: Handle None/empty values

        if not url:
            return ""

        try:
            parsed = urlparse(url if url.startswith('http') else f'http://{url}')
            domain = parsed.netloc or parsed.path
            domain = domain.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two company names.

        Args:
            name1: First company name
            name2: Second company name

        Returns:
            Similarity score between 0 and 1
        """
        # TODO: Normalize names (lowercase, remove punctuation, remove common suffixes like Inc, LLC)
        # TODO: Use fuzzy string matching (e.g., Levenshtein distance, or simple token overlap)
        # TODO: Handle abbreviations and variations
        # TODO: Return similarity score

        raise NotImplementedError("Name similarity calculation not yet implemented")

    def save_to_markdown(self, companies: List[CompanyRecord], output_path: str):
        """
        Save aggregated companies to a markdown file for debugging.

        Args:
            companies: List of CompanyRecord objects
            output_path: Path to output markdown file
        """
        # TODO: Format companies as markdown
        # TODO: Include all fields in readable format
        # TODO: Show sources and confidence scores
        # TODO: Write to file

        raise NotImplementedError("Markdown export not yet implemented")
