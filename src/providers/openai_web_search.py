"""
OpenAI Web Search Provider for company information.
Uses OpenAI's web search capability to find and extract company details.
"""
import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from openai import OpenAI
from .base import BaseProvider


# OpenAI Pricing (per 1M tokens) - Standard tier as of Jan 2025
OPENAI_PRICING = {
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-4.1': {'input': 2.00, 'output': 8.00},
    'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
    'gpt-4': {'input': 30.00, 'output': 60.00},  # Legacy
}
WEB_SEARCH_COST_PER_CALL = 0.01  # $0.01 per web search tool call


@dataclass
class TokenUsage:
    """Track token usage for a single API call."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    web_search_calls: int = 0
    model: str = ""
    operation: str = ""

    @property
    def input_cost(self) -> float:
        """Calculate input token cost."""
        pricing = OPENAI_PRICING.get(self.model, {'input': 0.15, 'output': 0.60})
        return (self.input_tokens / 1_000_000) * pricing['input']

    @property
    def output_cost(self) -> float:
        """Calculate output token cost."""
        pricing = OPENAI_PRICING.get(self.model, {'input': 0.15, 'output': 0.60})
        return (self.output_tokens / 1_000_000) * pricing['output']

    @property
    def web_search_cost(self) -> float:
        """Calculate web search tool cost."""
        return self.web_search_calls * WEB_SEARCH_COST_PER_CALL

    @property
    def total_cost(self) -> float:
        """Calculate total cost for this call."""
        return self.input_cost + self.output_cost + self.web_search_cost


@dataclass
class SearchUsageSummary:
    """Aggregate token usage for an entire search operation."""
    model: str = ""
    calls: List[TokenUsage] = field(default_factory=list)

    @property
    def total_input_tokens(self) -> int:
        return sum(c.input_tokens for c in self.calls)

    @property
    def total_output_tokens(self) -> int:
        return sum(c.output_tokens for c in self.calls)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_web_search_calls(self) -> int:
        return sum(c.web_search_calls for c in self.calls)

    @property
    def total_input_cost(self) -> float:
        return sum(c.input_cost for c in self.calls)

    @property
    def total_output_cost(self) -> float:
        return sum(c.output_cost for c in self.calls)

    @property
    def total_web_search_cost(self) -> float:
        return sum(c.web_search_cost for c in self.calls)

    @property
    def total_cost(self) -> float:
        return sum(c.total_cost for c in self.calls)

    def print_summary(self):
        """Print a formatted summary of token usage and costs."""
        print("\n" + "="*70)
        print("TOKEN USAGE & COST SUMMARY")
        print("="*70)
        print(f"Model: {self.model}")
        print(f"Total API calls: {len(self.calls)}")
        print("-"*70)
        print(f"{'Category':<25} {'Tokens':>12} {'Cost':>12}")
        print("-"*70)
        print(f"{'Input tokens':<25} {self.total_input_tokens:>12,} ${self.total_input_cost:>10.6f}")
        print(f"{'Output tokens':<25} {self.total_output_tokens:>12,} ${self.total_output_cost:>10.6f}")
        print(f"{'Web search calls':<25} {self.total_web_search_calls:>12} ${self.total_web_search_cost:>10.6f}")
        print("-"*70)
        print(f"{'TOTAL':<25} {self.total_tokens:>12,} ${self.total_cost:>10.6f}")
        print("="*70)

        # Breakdown by operation
        print("\nBreakdown by operation:")
        print("-"*70)
        for i, call in enumerate(self.calls, 1):
            print(f"  {i}. {call.operation:<30} "
                  f"in:{call.input_tokens:>6,} out:{call.output_tokens:>5,} "
                  f"${call.total_cost:.6f}")
        print("="*70 + "\n")

    def to_dict(self) -> Dict[str, Any]:
        """Return usage data as a dictionary for programmatic access."""
        return {
            'model': self.model,
            'total_api_calls': len(self.calls),
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_tokens,
            'total_web_search_calls': self.total_web_search_calls,
            'costs': {
                'input_tokens': self.total_input_cost,
                'output_tokens': self.total_output_cost,
                'web_search': self.total_web_search_cost,
                'total': self.total_cost,
            },
            'calls': [
                {
                    'operation': c.operation,
                    'input_tokens': c.input_tokens,
                    'output_tokens': c.output_tokens,
                    'web_search_calls': c.web_search_calls,
                    'cost': c.total_cost,
                }
                for c in self.calls
            ]
        }


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

        # Token usage tracking
        self._current_search_usage: SearchUsageSummary = None
        self._last_search_usage: SearchUsageSummary = None

    def _extract_usage(self, response, operation: str) -> TokenUsage:
        """
        Extract token usage from an OpenAI Responses API response.

        Args:
            response: The response object from OpenAI
            operation: Description of the operation (for logging)

        Returns:
            TokenUsage object with extracted data
        """
        usage = TokenUsage(
            model=self.model,
            operation=operation,
            web_search_calls=1,  # Each call uses web search once
        )

        # Extract usage from response
        # The Responses API returns usage in response.usage
        if hasattr(response, 'usage') and response.usage:
            usage.input_tokens = getattr(response.usage, 'input_tokens', 0)
            usage.output_tokens = getattr(response.usage, 'output_tokens', 0)
            usage.total_tokens = getattr(response.usage, 'total_tokens',
                                         usage.input_tokens + usage.output_tokens)

        return usage

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

        # Track token usage
        usage = self._extract_usage(response, f"Company list search (max {max_companies})")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)
        print(f"  [Tokens] in:{usage.input_tokens:,} out:{usage.output_tokens:,} cost:${usage.total_cost:.6f}")

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

        # Track token usage
        usage = self._extract_usage(response, f"Company details: {company_name[:25]}")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

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
            filters: Additional filters (e.g., {'max_results': 10, 'track_usage': True})

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

        Note:
            After calling this method, access token usage via:
            - provider.get_last_usage() -> SearchUsageSummary object
            - provider.get_last_usage().to_dict() -> dict for JSON serialization
            - provider.get_last_usage().print_summary() -> prints formatted summary
        """
        # Initialize usage tracking for this search
        self._current_search_usage = SearchUsageSummary(model=self.model)

        # Step 1: Get list of company names based on user requirements
        max_companies = filters.get('max_results', 10) if filters else 10
        print(f"\n[Token Tracking] Starting search for up to {max_companies} companies...")
        company_names = self._search_companies_list(query, max_companies)
        print(f"Found {len(company_names)} companies")

        # Step 2: Get detailed information for each company
        companies = []
        for i, company_name in enumerate(company_names, 1):
            try:
                print(f"  [{i}/{len(company_names)}] Retrieving: {company_name}...", end=" ")
                company_info = self._get_company_info(company_name)
                companies.append(company_info)
                # Print inline token info
                if self._current_search_usage.calls:
                    last_call = self._current_search_usage.calls[-1]
                    print(f"in:{last_call.input_tokens:,} out:{last_call.output_tokens:,}")
                else:
                    print("done")
            except Exception as e:
                print(f"ERROR: {str(e)}")
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

        # Store usage for retrieval and print summary
        self._last_search_usage = self._current_search_usage
        self._current_search_usage = None

        # Print summary
        self._last_search_usage.print_summary()

        return companies

    def get_last_usage(self) -> SearchUsageSummary:
        """
        Get the token usage summary from the last search operation.

        Returns:
            SearchUsageSummary object with detailed token usage and costs.
            Returns None if no search has been performed yet.

        Example:
            >>> provider = OpenAIWebSearchProvider()
            >>> results = provider.search_companies("AI startups", {'max_results': 5})
            >>> usage = provider.get_last_usage()
            >>> print(f"Total cost: ${usage.total_cost:.4f}")
            >>> print(f"Total tokens: {usage.total_tokens:,}")
        """
        return self._last_search_usage

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
