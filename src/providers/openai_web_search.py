"""
OpenAI Web Search Provider for company information.
Uses OpenAI's web search capability to find and extract company details.
"""
import os
from typing import List, Dict, Any
from openai import OpenAI
from .base import BaseProvider


class OpenAIWebSearchProvider(BaseProvider):
    """Provider that uses OpenAI web search to find company information."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the OpenAI Web Search provider.

        Args:
            config: Configuration dictionary, should include 'api_key' or use env variable
        """
        super().__init__(config)
        api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key must be provided in config or OPENAI_API_KEY environment variable")

        self.client = OpenAI(api_key=api_key)
        # gpt-4o-mini is cheaper and supports web search
        self.model = self.config.get('model', 'gpt-4o-mini')

    def _search_companies_list(self, user_requirements: str, max_companies: int = 10) -> List[str]:
        """
        Search for a list of company names based on user requirements.

        Args:
            user_requirements: User's description of partner company needs
            max_companies: Maximum number of companies to return

        Returns:
            List of company names
        """
        prompt = f"""Based on the following user requirements, find up to {max_companies} real companies that would be suitable partners:

User Requirements:
{user_requirements}

Search the web and provide a list of {max_companies} real, currently operating companies that match these requirements.

IMPORTANT: Return ONLY the company names in a numbered list format like this:
1. Company Name A
2. Company Name B
3. Company Name C

Do NOT include any introductory text, explanations, or descriptions. Just the numbered list of company names."""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        # Parse company names from response
        content = response.output_text.strip()
        companies = []

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Skip lines that don't start with a number (introduction text)
            if not line[0].isdigit():
                continue

            # Remove numbering (e.g., "1. ", "1) ", etc.)
            if '. ' in line:
                line = line.split('. ', 1)[1]
            elif ') ' in line:
                line = line.split(') ', 1)[1]

            company_name = line.strip()

            # Filter out invalid company names
            # Skip if too long (likely a sentence, not a company name)
            if len(company_name) > 100:
                continue
            # Skip if empty
            if not company_name:
                continue

            companies.append(company_name)

        return companies[:max_companies]

    def _get_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Search for detailed information about a specific company using web search.

        Args:
            company_name: Name of the company

        Returns:
            Dictionary with company information
        """
        prompt = f"""Search the web for detailed information about the company "{company_name}".

Provide the following information in a structured format:
- Company Name: (official name)
- Website: (official website URL)
- Description: (2-3 sentences about what the company does)
- Industry: (primary industry/sector)
- Size: (approximate number of employees, e.g., "10-50", "50-200", "200-500", "500+")
- Location: (headquarters city and country)

If any information is not available, indicate it as "Not available".
Provide only factual, verified information from reliable sources."""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        # Parse the response into structured data
        content = response.output_text.strip()

        # Extract information using parsing
        info = {
            'name': company_name,
            'website': self._extract_website(content),
            'description': self._extract_field(content, ['description'], is_multiline=True),
            'industry': self._extract_field(content, ['industry', 'sector']),
            'size': self._extract_field(content, ['company size', 'size', 'employees', 'number of employees']),
            'location': self._extract_field(content, ['location', 'headquarters', 'hq', 'head office']),
            'source': 'openai_web_search',
            'raw_data': {'search_result': content}
        }

        return info

    def _extract_website(self, text: str) -> str:
        """
        Extract website URL from text.

        Args:
            text: Text to search in

        Returns:
            Website URL or "Not available"
        """
        import re

        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Look for website field
            if 'website' in line_lower or 'url' in line_lower:
                # Try to find URL in same line
                url_match = re.search(r'https?://[^\s\)]+', line)
                if url_match:
                    return url_match.group(0).rstrip('.,;:')

                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    url_match = re.search(r'https?://[^\s\)]+', next_line)
                    if url_match:
                        return url_match.group(0).rstrip('.,;:')

        # Fallback: find any URL in the text
        url_match = re.search(r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s\)]*', text)
        if url_match:
            url = url_match.group(0).rstrip('.,;:')
            # Filter out reference URLs
            if 'wikipedia' not in url and 'linkedin' not in url and 'utm_source' not in url:
                return url

        return "Not available"

    def _extract_field(self, text: str, field_names: List[str], is_multiline: bool = False) -> str:
        """
        Extract a field value from text by looking for field name patterns.

        Args:
            text: Text to search in
            field_names: List of possible field name variations
            is_multiline: If True, collect multiple lines for the field (e.g., description)

        Returns:
            Extracted value or "Not available"
        """
        import re

        # List of all possible field headers to detect section boundaries
        all_field_headers = ['website', 'description', 'industry', 'size', 'location',
                            'company name', 'headquarters', 'employees', 'sector', 'hq']

        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            # Remove markdown formatting for matching
            line_clean = re.sub(r'\*+', '', line_lower)

            for field_name in field_names:
                # Check if line contains the field name as a header
                if field_name.lower() in line_clean:
                    # Try to extract value from same line after colon
                    if ':' in line:
                        value = line.split(':', 1)[1].strip()
                        value = self._clean_value(value)
                        if value:
                            # For multiline fields, continue collecting
                            if is_multiline:
                                collected = [value]
                                for j in range(i + 1, min(i + 5, len(lines))):
                                    next_line = lines[j].strip()
                                    # Stop if we hit another field header
                                    if any(h in next_line.lower() for h in all_field_headers):
                                        break
                                    if next_line.startswith('•') or next_line.startswith('-'):
                                        cleaned = self._clean_value(next_line.lstrip('•-* '))
                                        if cleaned:
                                            collected.append(cleaned)
                                return ' '.join(collected)
                            return value

                    # Check following lines for value (common in markdown format)
                    collected_values = []
                    for j in range(i + 1, min(i + 6, len(lines))):
                        next_line = lines[j].strip()
                        if not next_line:
                            continue

                        # Stop if we hit another field header
                        next_line_lower = next_line.lower()
                        if any(h in next_line_lower for h in all_field_headers):
                            break

                        # Handle bullet point format
                        if next_line.startswith('•') or next_line.startswith('-') or next_line.startswith('*'):
                            value = next_line.lstrip('•-* ').strip()
                            value = self._clean_value(value)
                            if value:
                                collected_values.append(value)
                                if not is_multiline:
                                    return value
                        elif collected_values:
                            # Continue collecting for multiline
                            value = self._clean_value(next_line)
                            if value:
                                collected_values.append(value)

                    if collected_values:
                        return ' '.join(collected_values)

        return "Not available"

    def _clean_value(self, value: str) -> str:
        """
        Clean extracted value by removing markdown formatting and citations.

        Args:
            value: Raw extracted value

        Returns:
            Cleaned value string
        """
        import re

        if not value:
            return ""

        # Remove markdown bold/italic
        value = re.sub(r'\*+', '', value)

        # Remove markdown links but keep the text: [text](url) -> text
        value = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', value)

        # Remove standalone URLs in parentheses like (en.wikipedia.org) or (https://...)
        value = re.sub(r'\s*\([^)]*(?:https?://|www\.)[^)]+\)', '', value)
        value = re.sub(r'\s*\([a-z]+\.[a-z]+\.[a-z]+(?:/[^)]+)?\)', '', value)  # (en.wikipedia.org)
        value = re.sub(r'\s*\([a-z]+\.[a-z]+(?:/[^)]+)?\)', '', value)  # (example.com)

        # Remove URLs that start with // (incomplete URLs)
        value = re.sub(r'//[^\s]+', '', value)

        # Remove source citations like (source.com)
        value = re.sub(r'\s*\([^)]*\.(com|org|net|io|aero|gov)[^)]*\)', '', value)

        # Clean up extra whitespace
        value = ' '.join(value.split())

        # Remove trailing punctuation artifacts
        value = value.strip('.,;:')

        # Check if value is meaningful
        if value.lower() in ['not available', 'n/a', 'unknown', '']:
            return ""

        # Skip if value is just a URL or URL fragment
        if value.startswith('http') or value.startswith('//') or value.startswith('www.'):
            return ""

        return value.strip()

    def search_companies(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for companies based on user requirements.

        Args:
            query: User requirements text describing the partner company needs
            filters: Additional filters (e.g., {'max_results': 10})

        Returns:
            List of company dictionaries with schema:
            {
                'name': str,
                'website': str,
                'description': str,
                'industry': str,
                'size': str,
                'location': str,
                'source': str,
                'raw_data': dict
            }
        """
        # Step 1: Get list of company names based on user requirements
        max_companies = filters.get('max_results', 10) if filters else 10
        company_names = self._search_companies_list(query, max_companies)
        print(f"Found {len(company_names)} companies")

        # Step 2: Get detailed information for each company
        companies = []
        for company_name in company_names:
            try:
                company_info = self._get_company_info(company_name)
                companies.append(company_info)
                print(f"Retrieved info for: {company_name}")
            except Exception as e:
                print(f"Error getting info for {company_name}: {str(e)}")
                # Add basic info even if detailed search fails
                companies.append({
                    'name': company_name,
                    'website': 'Not available',
                    'description': 'Not available',
                    'industry': 'Not available',
                    'size': 'Not available',
                    'location': 'Not available',
                    'source': 'openai_web_search',
                    'raw_data': {'error': str(e)}
                })

        return companies

    def get_company_details(self, company_identifier: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific company.

        Args:
            company_identifier: Company name or identifier

        Returns:
            Detailed company information dictionary
        """
        return self._get_company_info(company_identifier)

    def normalize_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw company data to standardized schema.

        Args:
            raw_data: Raw data dictionary

        Returns:
            Normalized company dictionary
        """
        # The data is already normalized in our search methods
        # This method ensures compatibility with the base class interface
        return {
            'name': raw_data.get('name', 'Not available'),
            'website': raw_data.get('website', 'Not available'),
            'description': raw_data.get('description', 'Not available'),
            'industry': raw_data.get('industry', 'Not available'),
            'size': raw_data.get('size', 'Not available'),
            'location': raw_data.get('location', 'Not available'),
            'source': 'openai_web_search',
            'raw_data': raw_data.get('raw_data', {})
        }


# ============================================================================
# TEST CODE
# ============================================================================

def test_smart_aircraft_inspection():
    """
    Test the OpenAI Web Search provider with Smart Aircraft Inspection requirement.
    Saves results to CSV file.
    """
    import csv
    from datetime import datetime

    # Load the user requirement from file
    requirement_file = os.path.join(
        os.path.dirname(__file__),
        '..', '..',
        'test_data',
        'smart_aircraft_inspection_requirement.txt'
    )

    try:
        with open(requirement_file, 'r', encoding='utf-8') as f:
            user_requirement = f.read()
    except FileNotFoundError:
        # Fallback: use inline requirement if file not found
        user_requirement = """
Smart Aircraft Inspection Technology Partners

Qatar Airways and QRDI Council seek innovative partners to modernize aircraft exterior inspections.
Looking for companies specializing in:
- Optical 3D Scanners for high-resolution surface scanning
- AI-Powered defect detection and classification tools
- Drone-Based Inspection Systems for automated aircraft inspection
- Time-of-Flight (ToF) Cameras for precise measurements
- Advanced image processing and multispectral imaging
- Non-destructive testing (NDT) technologies: X-ray, Ultrasound, Infrared, Eddy currents

Key Requirements:
- Technology Readiness Level (TRL) > 3
- Proven track record in aerospace/aviation industry
- Capability to detect defects with 0.1mm resolution
- >99% reliability in defect identification
- Experience with aircraft maintenance systems integration
- Real-time reporting capabilities

Preferred partners:
- Companies with aerospace industry experience
- Technology providers with AI/ML capabilities
- NDT equipment manufacturers
- Drone/robotics companies with aviation applications
"""

    print("="*80)
    print("Testing OpenAI Web Search Provider")
    print("="*80)
    print(f"\nUser Requirement:\n{user_requirement[:500]}...\n")
    print("="*80)

    # Initialize provider
    provider = OpenAIWebSearchProvider()

    # Search for companies (limit to 5 for testing)
    print("\nSearching for companies...\n")
    companies = provider.search_companies(
        query=user_requirement,
        filters={'max_results': 5}
    )

    print(f"\n{'='*80}")
    print(f"Found {len(companies)} companies")
    print(f"{'='*80}\n")

    # Display results
    for i, company in enumerate(companies, 1):
        print(f"\n{i}. {company['name']}")
        print(f"   Website: {company['website']}")
        print(f"   Industry: {company['industry']}")
        print(f"   Size: {company['size']}")
        print(f"   Location: {company['location']}")
        print(f"   Description: {company['description'][:150]}...")
        print(f"   {'-'*76}")

    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'smart_aircraft_inspection_results_{timestamp}.csv'
    csv_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'test_results',
        csv_filename
    )

    # Create test_results directory if it doesn't exist
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'website', 'description', 'industry', 'size', 'location', 'source']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for company in companies:
            writer.writerow({
                'name': company['name'],
                'website': company['website'],
                'description': company['description'],
                'industry': company['industry'],
                'size': company['size'],
                'location': company['location'],
                'source': company['source']
            })

    print(f"\n{'='*80}")
    print(f"Results saved to: {csv_path}")
    print(f"{'='*80}\n")

    return companies


if __name__ == "__main__":
    # Usage example: search for CoVital pilot partners using covital_pilot.md
    import csv
    from pathlib import Path

    provider = OpenAIWebSearchProvider()

    # Load query from covital_pilot.md
    query_file = Path(__file__).parent.parent.parent / 'test_data' / 'md' / 'covital_pilot.md'
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read()

    results = provider.search_companies(query, {'max_results': 10})
    print(f"Found {len(results)} pilot partners")

    # Save results to CSV
    output_dir = Path(__file__).parent.parent.parent / 'test_results' / 'openai_web_search'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'pilot_partners.csv'

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if results:
            fieldnames = ['name', 'description', 'industry', 'location', 'website', 'source']
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)

    print(f"Results saved to: {output_path}")
