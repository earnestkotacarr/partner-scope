"""
OpenAI Web Search Provider for company information.
Uses OpenAI's web search capability to find and extract company details.
"""
import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from openai import OpenAI
from .base import BaseProvider


# OpenAI Pricing (per 1M tokens) - Standard tier as of Jan 2026
OPENAI_PRICING = {
    # GPT-5 Series (Standard tier)
    'gpt-4.1.2': {'input': 1.75, 'output': 14.00},
    'gpt-4.1': {'input': 1.25, 'output': 10.00},
    'gpt-4.1-mini': {'input': 0.25, 'output': 2.00},
    # GPT-4.1 Series
    'gpt-4.1': {'input': 2.00, 'output': 8.00},
    'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
    # GPT-4o Series
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    # Legacy
    'gpt-4': {'input': 30.00, 'output': 60.00},
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

        # Set longer timeout for GPT-5 quality mode (can take 60-90s per call)
        self.client = OpenAI(api_key=api_key, timeout=300.0)
        # gpt-4.1 is the strongest model that supports web search (gpt-5 for quality mode)
        self.model = self.config.get('model', 'gpt-4.1')
        # Default timeout for API calls (can be overridden per-call)
        self.api_timeout = self.config.get('timeout', 300.0)

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

    def _generate_search_queries(self, partner_needs: str, startup_context: dict = None) -> List[str]:
        """
        Generate 3-5 search query variations based on user's discovery context.

        Args:
            partner_needs: Main partner search requirement
            startup_context: Dict with startup_name, industry, description, keywords, etc.

        Returns:
            List of search query strings
        """
        if not startup_context:
            # Fallback: just use the original query
            return [partner_needs]

        # Extract context from discovery
        startup_name = startup_context.get('startup_name', '')
        industry = startup_context.get('industry', '')
        description = startup_context.get('description', '')
        keywords = startup_context.get('keywords', [])
        investment_stage = startup_context.get('investment_stage', '')
        product_stage = startup_context.get('product_stage', '')

        # Build context string
        context = f"""
Startup: {startup_name}
Industry: {industry}
Description: {description}
Stage: {investment_stage}, {product_stage}
Keywords: {', '.join(keywords) if keywords else 'None'}
Partner Need: {partner_needs}
"""

        prompt = f"""Based on this startup's context and partner search needs:
{context}

Generate 4 different search queries to find potential partner companies.
Each query should explore a different angle based on their specific situation:

1. Direct search based on their stated partner needs
2. Search focused on their industry vertical ({industry})
3. Search based on their keywords/capabilities: {', '.join(keywords[:3]) if keywords else 'their core technology'}
4. Search for companies that typically partner with {investment_stage} startups in this space

Return just the 4 queries, one per line. Make them specific and actionable web searches."""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        # Track usage (no web search for query generation)
        usage = TokenUsage(
            model=self.model,
            operation="Query generation",
            input_tokens=getattr(response.usage, 'input_tokens', 0) if response.usage else 0,
            output_tokens=getattr(response.usage, 'output_tokens', 0) if response.usage else 0,
            web_search_calls=0
        )
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        queries = []
        for line in response.output_text.strip().split('\n'):
            line = line.strip()
            # Remove numbering if present
            if line and line[0].isdigit():
                if '. ' in line:
                    line = line.split('. ', 1)[-1].strip()
                elif ') ' in line:
                    line = line.split(') ', 1)[-1].strip()
            if line and len(line) > 10:  # Skip empty or too short
                queries.append(line)

        return queries[:5] if queries else [partner_needs]

    def _search_with_details(
        self,
        query: str,
        max_companies: int = 7,
        user_needs: str = None
    ) -> List[Dict[str, Any]]:
        """
        Single API call that returns companies WITH all details,
        explicitly mapping each company to the user's specific needs.

        Args:
            query: Search query string
            max_companies: Maximum companies to return
            user_needs: Original user requirements (for need mapping)

        Returns:
            List of company dicts with full details and need satisfaction info
        """
        # Include user needs context if available
        needs_context = ""
        if user_needs:
            needs_context = f"""
THE USER'S SPECIFIC NEEDS:
"{user_needs}"

When evaluating each company, identify which of these specific needs they can satisfy.
"""

        prompt = f"""Search the web and find up to {max_companies} real companies matching this requirement:

{query}
{needs_context}
For EACH company found, provide ALL of the following information:

1. Company Name (official name)
2. Website (official URL)
3. Industry/Sector
4. Location (headquarters city, country)
5. Size (employee count or revenue tier)
6. Description (2-3 sentences about what they do)
7. NEEDS SATISFIED: Which specific user needs this company addresses (use short tags like "Distribution Network", "Healthcare Expertise", "Technology Platform", "Market Access", etc.)
8. HOW IT HELPS: One clear sentence explaining HOW this company's specific offerings/capabilities would help the user achieve their goal. Be specific about what they offer and how it maps to the need.

Format your response as a numbered list. For each company use this EXACT format:

1. **[Company Name]**
   - Website: [url]
   - Industry: [industry]
   - Location: [location]
   - Size: [size]
   - Description: [description]
   - Needs Satisfied: [tag1], [tag2], [tag3]
   - How It Helps: [specific explanation of how this company helps achieve the user's goals]

2. **[Next Company]**
   ...

IMPORTANT:
- Focus on HOW each company can help, not just WHAT they are
- Be specific about what they offer that maps to the user's needs
- Only include real, currently operating companies"""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        # Track token usage
        usage = self._extract_usage(response, f"Search with details ({max_companies} companies)")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        # Parse companies from response
        return self._parse_companies_with_details(response.output_text)

    def _analyze_and_generate_creative_queries(
        self,
        partner_needs: str,
        startup_context: dict,
        companies_found: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Phase 1.5: Strategic reflection and requirement reinterpretation.

        This is NOT just about finding "unconventional" partners. It's a genuine
        strategic reflection that:
        1. Re-examines the original requirements - what do they REALLY need?
        2. Questions the naive assumptions made in Phase 1 queries
        3. Learns from what was found - do these companies actually solve the problem?
        4. Identifies gaps between stated needs and underlying needs
        5. Generates smarter queries based on deeper understanding

        Example transformation:
        - User said: "need healthcare distribution partners"
        - Phase 1 assumed: search for "healthcare distributors" → found McKesson, Cardinal
        - Phase 1.5 reflects: "They want MARKET ACCESS for an AI diagnostic tool.
          Distribution is one path, but they might also need:
          - Clinical validation partners (to prove it works)
          - EHR integration platforms (to embed in workflows)
          - Health system innovation programs (early adopters)
          - Medical professional associations (to drive adoption)"

        Args:
            partner_needs: Original partner search requirement
            startup_context: Dict with startup info
            companies_found: List of companies found in Phase 1

        Returns:
            List of 3 strategically-refined search query strings
        """
        # Build summary of companies found
        company_summary = []
        industries_found = set()
        for c in companies_found[:15]:  # Sample first 15
            name = c.get('name', 'Unknown')
            industry = c.get('industry', 'Unknown')
            industries_found.add(industry)
            desc = c.get('description', '')[:100]
            fit = c.get('fit_reason', '')[:80]
            company_summary.append(f"- {name} ({industry}): {desc}")

        companies_text = '\n'.join(company_summary) if company_summary else "No companies found yet"
        industries_text = ', '.join(list(industries_found)[:10]) if industries_found else "Unknown"

        # Extract startup context
        startup_name = startup_context.get('startup_name', '') if startup_context else ''
        industry = startup_context.get('industry', '') if startup_context else ''
        description = startup_context.get('description', '') if startup_context else ''
        investment_stage = startup_context.get('investment_stage', '') if startup_context else ''
        product_stage = startup_context.get('product_stage', '') if startup_context else ''

        prompt = f"""You are a strategic partnership consultant doing a DEEP REFLECTION on a partner search.

## THE STARTUP
- Name: {startup_name}
- Industry: {industry}
- Stage: {investment_stage}, {product_stage}
- What they do: {description}

## WHAT THEY SAID THEY NEED
"{partner_needs}"

## WHAT OUR INITIAL SEARCH FOUND ({len(companies_found)} companies)
Industries represented: {industries_text}

Sample companies found:
{companies_text}

## YOUR TASK: STRATEGIC REFLECTION

Step 1: RE-READ THE REQUIREMENTS
- What is the UNDERLYING GOAL behind their stated needs?
- What problem are they really trying to solve?
- Example: "need distribution partners" → underlying goal might be "market access" or "revenue channels" or "customer acquisition"

Step 2: QUESTION OUR NAIVE ASSUMPTIONS
- What assumptions did we make when searching?
- Were those assumptions too literal or narrow?
- Example: We searched for "distributors" but maybe they need "go-to-market partners" which is broader

Step 3: EVALUATE WHAT WE FOUND
- Do these companies ACTUALLY address the underlying goal?
- What's MISSING that would better serve their real needs?
- Are there better paths to their goal that we didn't explore?

Step 4: GENERATE SMARTER QUERIES
Based on your reflection, generate exactly 3 NEW search queries that:
1. Address the UNDERLYING NEED in a different way (not just the literal stated need)
2. Explore a path to their goal that our naive searches missed
3. Find partners that solve the REAL problem, not just match keywords

IMPORTANT:
- Don't just add "unconventional" - be STRATEGIC
- Each query should come from a genuine insight about what they actually need
- Explain your reasoning briefly, then give the query

## OUTPUT FORMAT
For each of 3 queries, write:
INSIGHT: [One sentence explaining the strategic insight]
QUERY: [The actual search query]

Example:
INSIGHT: They need market access, not just distribution - health systems with innovation programs are better early adopters than traditional distributors
QUERY: "health system innovation programs" digital health pilot partnerships"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        # Track usage (no web search for analysis)
        usage = TokenUsage(
            model=self.model,
            operation="Strategic reflection (Phase 1.5)",
            input_tokens=getattr(response.usage, 'input_tokens', 0) if response.usage else 0,
            output_tokens=getattr(response.usage, 'output_tokens', 0) if response.usage else 0,
            web_search_calls=0
        )
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        # Parse insights and queries from response
        content = response.output_text.strip()
        queries = []
        insights = []

        lines = content.split('\n')
        current_insight = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for INSIGHT line
            if line.upper().startswith('INSIGHT:'):
                current_insight = line.split(':', 1)[1].strip() if ':' in line else line
            # Check for QUERY line
            elif line.upper().startswith('QUERY:'):
                query = line.split(':', 1)[1].strip() if ':' in line else line
                # Clean up the query (remove quotes if wrapped)
                query = query.strip('"\'')
                if query and len(query) > 10:
                    queries.append(query)
                    insights.append(current_insight or "Strategic insight")
                    current_insight = None
            # Fallback: if line looks like a query (no special prefix)
            elif len(line) > 20 and not line.startswith('#') and not line.startswith('-'):
                # Could be a query without the QUERY: prefix
                if line[0].isdigit() and '. ' in line:
                    line = line.split('. ', 1)[1].strip()
                if len(line) > 10 and not any(line.lower().startswith(x) for x in ['step', 'example', 'important']):
                    # Only add if we don't have enough queries yet
                    if len(queries) < 3:
                        queries.append(line.strip('"\''))
                        insights.append(current_insight or "")
                        current_insight = None

        # Log the strategic insights
        if insights:
            print(f"\n  Strategic Insights from Reflection:")
            for i, (insight, query) in enumerate(zip(insights[:3], queries[:3]), 1):
                if insight:
                    print(f"    {i}. {insight[:80]}{'...' if len(insight) > 80 else ''}")

        return queries[:3]

    def _needs_enrichment(self, company: Dict[str, Any]) -> bool:
        """
        Check if a company needs additional detail enrichment.

        Returns True if critical fields are missing or insufficient.

        Args:
            company: Company dictionary to check

        Returns:
            True if enrichment is needed
        """
        website = company.get('website', '') or ''
        description = company.get('description', '') or ''
        industry = company.get('industry', '') or ''

        # Check website - must be a real URL
        website_missing = (
            not website or
            website == 'Not available' or
            website.lower() == 'n/a' or
            not website.startswith('http')
        )

        # Check description - must be meaningful
        description_poor = (
            not description or
            description == 'Not available' or
            len(description) < 30
        )

        # Need enrichment if website is missing OR description is very poor
        return website_missing or description_poor

    def _enrich_company_details(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific company to fill in missing data.

        Args:
            company: Company dict with at least 'name' field

        Returns:
            Enriched company dictionary
        """
        company_name = company.get('name', 'Unknown')

        prompt = f"""Search the web for detailed, verified information about "{company_name}".

Find and provide:
1. Official Website URL (must be the real company website, not a news article or LinkedIn)
2. Industry/Sector
3. Headquarters Location (city, country)
4. Company Size (employees or revenue tier)
5. Description (2-3 factual sentences about what they do)

Format your response exactly like this:
- Website: [URL]
- Industry: [industry]
- Location: [location]
- Size: [size]
- Description: [description]

Only provide verified, factual information. If you cannot find the official website, say "Website not found"."""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        # Track usage
        usage = self._extract_usage(response, f"Enrich: {company_name[:20]}")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        # Parse response and update company
        content = response.output_text.strip()
        enriched = company.copy()

        # Extract fields from response
        new_website = self._extract_website(content)
        if new_website and new_website != 'Not available':
            enriched['website'] = new_website

        new_desc = self._extract_field(content, ['description'], is_multiline=True)
        if new_desc and new_desc != 'Not available' and len(new_desc) > len(company.get('description', '')):
            enriched['description'] = new_desc

        new_industry = self._extract_field(content, ['industry', 'sector'])
        if new_industry and new_industry != 'Not available':
            enriched['industry'] = new_industry

        new_location = self._extract_field(content, ['location', 'headquarters'])
        if new_location and new_location != 'Not available':
            enriched['location'] = new_location

        new_size = self._extract_field(content, ['size', 'employees'])
        if new_size and new_size != 'Not available':
            enriched['size'] = new_size

        enriched['enriched'] = True
        return enriched

    def _parse_companies_with_details(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse structured company data from LLM response, including need satisfaction info.

        Args:
            text: Raw response text with company details

        Returns:
            List of company dictionaries with fields:
            - name, website, industry, location, size, description
            - needs_satisfied: List of need tags (e.g., ["Distribution Network", "Healthcare Expertise"])
            - how_it_helps: Explanation of how company satisfies the needs
        """
        import re

        companies = []
        current_company = None

        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for new company header (numbered with bold name)
            # Patterns: "1. **Company Name**" or "1. Company Name" or "**Company Name**"
            company_match = re.match(r'^\d+\.\s*\*?\*?([^*\n]+)\*?\*?\s*$', line)
            if company_match:
                # Save previous company
                if current_company and current_company.get('name'):
                    companies.append(current_company)

                # Start new company
                name = company_match.group(1).strip()
                name = re.sub(r'\*+', '', name).strip()  # Remove any remaining asterisks
                current_company = {
                    'name': name,
                    'website': 'Not available',
                    'description': 'Not available',
                    'industry': 'Not available',
                    'size': 'Not available',
                    'location': 'Not available',
                    'fit_reason': '',
                    'needs_satisfied': [],  # List of need tags
                    'how_it_helps': '',     # Explanation of how company helps
                    'source': 'openai_web_search',
                    'raw_data': {}
                }
                continue

            # Parse field lines for current company
            if current_company:
                line_lower = line.lower()

                if line.startswith('- ') or line.startswith('• '):
                    line = line[2:].strip()
                    line_lower = line.lower()

                if ':' in line:
                    field, value = line.split(':', 1)
                    field = field.lower().strip()
                    value = self._clean_value(value.strip())

                    if 'website' in field or 'url' in field:
                        # Extract URL
                        url_match = re.search(r'https?://[^\s\)]+', value)
                        if url_match:
                            current_company['website'] = url_match.group(0).rstrip('.,;:')
                        elif value and value != 'Not available':
                            current_company['website'] = value
                    elif 'industry' in field or 'sector' in field:
                        if value:
                            current_company['industry'] = value
                    elif 'location' in field or 'headquarters' in field or 'hq' in field:
                        if value:
                            current_company['location'] = value
                    elif 'size' in field or 'employees' in field:
                        if value:
                            current_company['size'] = value
                    elif 'description' in field:
                        if value:
                            current_company['description'] = value
                    elif 'fit' in field or 'why' in field or 'match' in field:
                        if value:
                            current_company['fit_reason'] = value
                    elif 'needs' in field and 'satisf' in field:
                        # Parse "Needs Satisfied: tag1, tag2, tag3" into list
                        if value:
                            tags = [tag.strip() for tag in value.split(',')]
                            tags = [t for t in tags if t and len(t) > 2]
                            current_company['needs_satisfied'] = tags
                    elif 'how' in field and ('help' in field or 'it' in field):
                        # Parse "How It Helps: explanation"
                        if value:
                            current_company['how_it_helps'] = value

        # Don't forget the last company
        if current_company and current_company.get('name'):
            companies.append(current_company)

        return companies

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
        3-Phase intelligent partner search with creative exploration and data enrichment.

        Phase 1: Initial Discovery (5 calls)
            - Generate 4 query variations from user context
            - Run searches with details → ~20-25 candidates

        Phase 1.5: Creative Analysis & Expansion (3-4 calls)
            - Analyze results, identify gaps, think unconventionally
            - Run creative/gap-filling searches → ~10-15 more candidates

        Phase 2: Selective Enrichment (variable)
            - Only for companies missing critical data (website, description)
            - Fetch verified details → complete info

        Args:
            query: User requirements text describing the partner company needs
            filters: Additional filters including:
                - max_results: Maximum companies to return (default: 20)
                - startup_context: Dict with startup_name, industry, description, keywords, etc.
                - progress_callback: Optional callback(phase, message, cost) for streaming updates

        Returns:
            List of company dictionaries with complete, verified information
        """
        # Initialize usage tracking for this search
        self._current_search_usage = SearchUsageSummary(model=self.model)

        max_results = filters.get('max_results', 20) if filters else 20
        startup_context = filters.get('startup_context') if filters else None
        progress_callback = filters.get('progress_callback') if filters else None

        # Companies per query for Phase 1 and 1.5
        companies_per_query = 6

        print(f"\n{'='*70}")
        print(f"[3-Phase Search] Starting intelligent partner search")
        print(f"  Model: {self.model}")
        print(f"  Target: {max_results} companies")
        print(f"{'='*70}")

        all_companies = []
        seen_names = set()

        def add_companies(results: List[Dict], phase_name: str) -> int:
            """Helper to merge and deduplicate companies."""
            new_count = 0
            for company in results:
                name_key = company['name'].lower().strip()
                name_key = name_key.replace(', inc.', '').replace(', inc', '')
                name_key = name_key.replace(', llc', '').replace(' llc', '')
                name_key = name_key.replace(' corporation', '').replace(' corp', '')

                if name_key not in seen_names:
                    seen_names.add(name_key)
                    company['discovery_phase'] = phase_name
                    all_companies.append(company)
                    new_count += 1
            return new_count

        # =====================================================================
        # PHASE 1: Initial Discovery
        # =====================================================================
        print(f"\n[Phase 1] Initial Discovery")
        print(f"-" * 40)

        if progress_callback:
            progress_callback('phase1_queries', 'Phase 1: Generating search variations...', None)

        queries = self._generate_search_queries(query, startup_context)
        print(f"  Generated {len(queries)} search queries:")
        for i, q in enumerate(queries, 1):
            print(f"    {i}. {q[:65]}{'...' if len(q) > 65 else ''}")

        for i, search_query in enumerate(queries, 1):
            if progress_callback:
                progress_callback(
                    'phase1_search',
                    f'Phase 1: Search {i}/{len(queries)}',
                    self._current_search_usage.total_cost
                )

            print(f"\n  [P1-Query {i}/{len(queries)}] {search_query[:55]}...")

            try:
                # Pass original user needs for need-satisfaction mapping
                results = self._search_with_details(search_query, companies_per_query, user_needs=query)
                new_count = add_companies(results, 'phase1')

                if self._current_search_usage.calls:
                    last_call = self._current_search_usage.calls[-1]
                    print(f"    → Found {len(results)}, {new_count} new (in:{last_call.input_tokens:,} out:{last_call.output_tokens:,})")
                print(f"    → Running total: {len(all_companies)} unique")

            except Exception as e:
                print(f"    → ERROR: {str(e)}")
                continue

        phase1_count = len(all_companies)
        print(f"\n  [Phase 1 Complete] {phase1_count} unique companies found")

        # =====================================================================
        # PHASE 1.5: Creative Analysis & Expansion
        # =====================================================================
        print(f"\n[Phase 1.5] Creative Analysis & Expansion")
        print(f"-" * 40)

        if progress_callback:
            progress_callback('phase1_5_analysis', 'Phase 1.5: Analyzing results for creative angles...',
                            self._current_search_usage.total_cost)

        print(f"  Analyzing {phase1_count} companies to find gaps and creative angles...")

        creative_queries = self._analyze_and_generate_creative_queries(query, startup_context, all_companies)
        print(f"  Generated {len(creative_queries)} creative queries:")
        for i, q in enumerate(creative_queries, 1):
            print(f"    {i}. {q[:65]}{'...' if len(q) > 65 else ''}")

        for i, search_query in enumerate(creative_queries, 1):
            if progress_callback:
                progress_callback(
                    'phase1_5_search',
                    f'Phase 1.5: Creative search {i}/{len(creative_queries)}',
                    self._current_search_usage.total_cost
                )

            print(f"\n  [P1.5-Query {i}/{len(creative_queries)}] {search_query[:55]}...")

            try:
                # Pass original user needs for need-satisfaction mapping
                results = self._search_with_details(search_query, companies_per_query, user_needs=query)
                new_count = add_companies(results, 'phase1.5_creative')

                if self._current_search_usage.calls:
                    last_call = self._current_search_usage.calls[-1]
                    print(f"    → Found {len(results)}, {new_count} new (in:{last_call.input_tokens:,} out:{last_call.output_tokens:,})")
                print(f"    → Running total: {len(all_companies)} unique")

            except Exception as e:
                print(f"    → ERROR: {str(e)}")
                continue

        phase1_5_new = len(all_companies) - phase1_count
        print(f"\n  [Phase 1.5 Complete] Added {phase1_5_new} new companies (total: {len(all_companies)})")

        # =====================================================================
        # PHASE 2: Selective Enrichment
        # =====================================================================
        print(f"\n[Phase 2] Selective Data Enrichment")
        print(f"-" * 40)

        # Identify companies needing enrichment
        needs_enrichment = [c for c in all_companies if self._needs_enrichment(c)]
        print(f"  {len(needs_enrichment)}/{len(all_companies)} companies need enrichment")

        if needs_enrichment:
            # Limit enrichment to avoid too many calls (prioritize earlier discoveries)
            max_enrichments = min(len(needs_enrichment), 10)
            to_enrich = needs_enrichment[:max_enrichments]

            if progress_callback:
                progress_callback('phase2_enrich', f'Phase 2: Enriching {len(to_enrich)} companies...',
                                self._current_search_usage.total_cost)

            enriched_count = 0
            for i, company in enumerate(to_enrich, 1):
                print(f"  [{i}/{len(to_enrich)}] Enriching: {company['name'][:40]}...", end=" ")

                try:
                    enriched = self._enrich_company_details(company)

                    # Update in place
                    idx = all_companies.index(company)
                    all_companies[idx] = enriched
                    enriched_count += 1

                    # Show what was added
                    added = []
                    if enriched.get('website', '').startswith('http') and not company.get('website', '').startswith('http'):
                        added.append('website')
                    if len(enriched.get('description', '')) > len(company.get('description', '')):
                        added.append('description')
                    print(f"✓ Added: {', '.join(added) if added else 'verified'}")

                except Exception as e:
                    print(f"✗ Error: {str(e)[:30]}")
                    continue

            print(f"\n  [Phase 2 Complete] Enriched {enriched_count} companies")
        else:
            print(f"  All companies have complete data - skipping enrichment")

        # =====================================================================
        # FINAL SUMMARY
        # =====================================================================
        # Store usage for retrieval
        self._last_search_usage = self._current_search_usage
        self._current_search_usage = None

        # Print summary
        self._last_search_usage.print_summary()

        # Count by phase
        p1_count = sum(1 for c in all_companies if c.get('discovery_phase') == 'phase1')
        p15_count = sum(1 for c in all_companies if c.get('discovery_phase') == 'phase1.5_creative')
        enriched_count = sum(1 for c in all_companies if c.get('enriched'))

        print(f"\n{'='*70}")
        print(f"[3-Phase Search Complete]")
        print(f"  Phase 1 (Initial):     {p1_count} companies")
        print(f"  Phase 1.5 (Creative):  {p15_count} companies")
        print(f"  Phase 2 (Enriched):    {enriched_count} companies")
        print(f"  Total unique:          {len(all_companies)} companies")
        print(f"{'='*70}\n")

        if progress_callback:
            progress_callback('complete', f'Found {len(all_companies)} partners',
                            self._last_search_usage.total_cost)

        # Return up to max_results
        return all_companies[:max_results]

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
