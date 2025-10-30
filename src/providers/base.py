"""
Base provider interface for partner search data sources.
All provider implementations should inherit from this base class.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseProvider(ABC):
    """Base class for all data providers (API and web scraping)."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the provider with configuration.

        Args:
            config: Provider-specific configuration (API keys, rate limits, etc.)
        """
        self.config = config or {}

    @abstractmethod
    def search_companies(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for companies based on query and filters.

        Args:
            query: Search query string (e.g., startup name, industry, partner needs)
            filters: Additional filters (industry, location, size, etc.)

        Returns:
            List of company dictionaries with standardized schema:
            {
                'name': str,
                'website': str,
                'description': str,
                'industry': str,
                'size': str,
                'location': str,
                'linkedin_url': str,
                'twitter_url': str,
                'facebook_url': str,
                'instagram_url': str,
                'contact_info': dict,
                'source': str,  # Provider name
                'raw_data': dict  # Original data from provider
            }
        """
        pass

    @abstractmethod
    def get_company_details(self, company_identifier: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific company.

        Args:
            company_identifier: Company identifier (name, domain, or provider-specific ID)

        Returns:
            Detailed company information dictionary with standardized schema
        """
        pass

    def normalize_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw provider data to standardized schema.
        Override this method for provider-specific normalization logic.

        Args:
            raw_data: Raw data from provider

        Returns:
            Normalized company dictionary
        """
        # TODO: Implement default normalization logic
        return raw_data
