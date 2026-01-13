"""
Mock Crunchbase provider for testing with pre-curated CSV files.
Maps partner queries to CSV files from manual CrunchBase searches.
"""
import csv
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseProvider


class MockCrunchbaseProvider(BaseProvider):
    """Mock Crunchbase provider that reads from pre-curated CSV files."""

    # Default keyword mappings for multiple startups
    DEFAULT_MAPPINGS = {
        # CoVital Node - doorway co-regulation robot for loneliness
        'pilot': {
            'keywords': [
                'dorm', 'housing', 'university', 'co-living', 'wellness',
                'wellbeing', 'mental health', 'student-life', 'pilot',
                'apartment', 'employer', 'student', 'employee', 'residence', 'living'
            ],
            'csv_path': 'test_data/csv/covital-pilot-partners.csv'
        },
        'validation': {
            'keywords': [
                'research', 'IRB', 'ethics', 'clinical', 'psych', 'HCI',
                'hospital', 'lab', 'validation', 'study', 'academic',
                'institution', 'psychology', 'loneliness', 'outcome'
            ],
            'csv_path': 'test_data/csv/covital-validation-partners.csv'
        },
        # StellarCore Mining - asteroid resource-mapping AI
        'stellar_datasource': {
            'keywords': [
                'satellite', 'spacecraft', 'smallsat', 'cubesat', 'radar',
                'sensor', 'spectroscopy', 'aerospace', 'rocket', 'space'
            ],
            'csv_path': 'test_data/csv/partner1_space.csv'
        },
        'stellar_validation': {
            'keywords': [
                'planetary', 'science', 'research', 'lab', 'mineralogy',
                'spectroscopy', 'institute', 'geology', 'asteroid', 'validation'
            ],
            'csv_path': 'test_data/csv/partner2_space.csv'
        }
    }

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Mock Crunchbase provider.

        Args:
            config: Configuration including:
                - 'base_path': Base path for CSV files (defaults to project root)
                - 'mappings': Custom keyword-to-CSV mappings (optional)
        """
        super().__init__(config)

        # Get base path for CSV files
        self.base_path = self.config.get('base_path')
        if not self.base_path:
            # Default to project root (two levels up from this file)
            self.base_path = Path(__file__).parent.parent.parent
        else:
            self.base_path = Path(self.base_path)

        # Load mappings from config or use defaults
        self.mappings = self.config.get('mappings', self.DEFAULT_MAPPINGS)

        # Cache for loaded CSV data
        self._csv_cache = {}

    def _match_query_to_csv(self, query: str) -> str:
        """
        Match a query string to the appropriate CSV file based on keyword overlap.

        Args:
            query: Search query string

        Returns:
            Path to the matching CSV file, or None if no match
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))

        best_match = None
        best_score = 0

        for partner_type, mapping in self.mappings.items():
            keywords = [k.lower() for k in mapping['keywords']]

            # Count keyword matches (support multi-word keywords like "mental health")
            score = 0
            for keyword in keywords:
                if ' ' in keyword:
                    # Multi-word keyword - check if present in query
                    if keyword in query_lower:
                        score += 2  # Higher weight for multi-word matches
                else:
                    # Single word keyword
                    if keyword in query_words:
                        score += 1

            if score > best_score:
                best_score = score
                best_match = mapping['csv_path']

        return best_match if best_score > 0 else None

    def _load_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """
        Load and parse a CSV file.

        Args:
            csv_path: Path to CSV file (relative to base_path)

        Returns:
            List of company dictionaries
        """
        # Check cache first
        if csv_path in self._csv_cache:
            return self._csv_cache[csv_path]

        full_path = self.base_path / csv_path

        if not full_path.exists():
            print(f"Warning: CSV file not found: {full_path}")
            return []

        companies = []
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    companies.append(row)
        except Exception as e:
            print(f"Error reading CSV {full_path}: {e}")
            return []

        # Cache the results
        self._csv_cache[csv_path] = companies
        return companies

    def search_companies(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for companies based on query keywords.

        Args:
            query: Search query (matched against keyword mappings)
            filters: Additional filters:
                - 'max_results': Maximum number of results to return
                - 'partner_type': Directly specify 'pilot' or 'validation'

        Returns:
            List of normalized company dictionaries
        """
        filters = filters or {}
        max_results = filters.get('max_results', 50)

        # Allow direct partner type specification
        partner_type = filters.get('partner_type')
        if partner_type and partner_type in self.mappings:
            csv_path = self.mappings[partner_type]['csv_path']
        else:
            # Match query to CSV based on keywords
            csv_path = self._match_query_to_csv(query)

        if not csv_path:
            print(f"No matching CSV found for query: {query}")
            return []

        print(f"Using CSV: {csv_path} for query: {query[:50]}...")

        # Load and normalize companies
        raw_companies = self._load_csv(csv_path)
        normalized = [self.normalize_company_data(c) for c in raw_companies]

        return normalized[:max_results]

    def get_company_details(self, company_identifier: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific company.

        Args:
            company_identifier: Company name to search for

        Returns:
            Company information dictionary, or empty dict if not found
        """
        # Search all CSV files for the company
        for mapping in self.mappings.values():
            companies = self._load_csv(mapping['csv_path'])
            for company in companies:
                name = company.get('Organization Name', '')
                if company_identifier.lower() in name.lower():
                    return self.normalize_company_data(company)

        return {}

    def normalize_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize CrunchBase CSV data to standard schema.

        Args:
            raw_data: Row from CrunchBase CSV export

        Returns:
            Normalized company dictionary
        """
        # Extract website from CrunchBase URL or use direct website if available
        crunchbase_url = raw_data.get('Organization Name URL', '')
        website = self._extract_website_from_cb_url(crunchbase_url)

        return {
            'name': raw_data.get('Organization Name', ''),
            'website': website,
            'description': raw_data.get('Description', ''),
            'industry': raw_data.get('Industries', ''),
            'size': '',  # Not in CSV export
            'location': raw_data.get('Headquarters Location', ''),
            'linkedin_url': '',  # Not in CSV export
            'twitter_url': '',   # Not in CSV export
            'facebook_url': '',  # Not in CSV export
            'instagram_url': '', # Not in CSV export
            'contact_info': {},
            'source': 'crunchbase_mock',
            'raw_data': {
                'crunchbase_url': crunchbase_url,
                'industry_groups': raw_data.get('Industry Groups', ''),
                'cb_rank': raw_data.get('CB Rank (Company)', '')
            }
        }

    def _extract_website_from_cb_url(self, cb_url: str) -> str:
        """
        Extract or infer company website from CrunchBase URL.

        Args:
            cb_url: CrunchBase organization URL

        Returns:
            Company website URL or CrunchBase URL as fallback
        """
        # CrunchBase URLs look like: https://www.crunchbase.com/organization/company-name
        # We return the CB URL as a reference; the actual website would need
        # to be scraped from the CB page or looked up separately
        return cb_url if cb_url else ''

    def get_all_companies(self, partner_type: str = None) -> List[Dict[str, Any]]:
        """
        Get all companies from CSV files.

        Args:
            partner_type: Optional - 'pilot' or 'validation' to filter

        Returns:
            List of all normalized company dictionaries
        """
        all_companies = []

        if partner_type and partner_type in self.mappings:
            mappings_to_load = {partner_type: self.mappings[partner_type]}
        else:
            mappings_to_load = self.mappings

        for mapping in mappings_to_load.values():
            companies = self._load_csv(mapping['csv_path'])
            normalized = [self.normalize_company_data(c) for c in companies]
            all_companies.extend(normalized)

        return all_companies


if __name__ == '__main__':
    # Usage example: search for pilot partners and save results to CSV
    provider = MockCrunchbaseProvider()

    # Search for pilot partners
    results = provider.search_companies("wellness student housing", {'partner_type': 'pilot', 'max_results': 10})
    print(f"Found {len(results)} pilot partners")

    # Save results to CSV
    output_dir = Path(__file__).parent.parent.parent / 'test_results' / 'mock_crunchbase'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'pilot_partners.csv'

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if results:
            fieldnames = ['name', 'description', 'industry', 'location', 'website', 'source']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)

    print(f"Results saved to: {output_path}")
