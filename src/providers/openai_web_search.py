"""
OpenAI Web Search Provider - 5-Phase Deep Research Architecture

This provider implements PartnerScope's intelligent partner search using:
- Multi-phase query refinement
- Strategic reflection to find non-obvious partners
- Need decomposition for comprehensive coverage
- Batch processing for consistent scoring
- Selective enrichment for complete data

TUNABLE SECTIONS ARE MARKED WITH:
    # === TUNABLE: [section name] ===
"""
import os
import re
from typing import List, Dict, Any
from dataclasses import dataclass, field
from openai import OpenAI
from .base import BaseProvider


# OpenAI Pricing (per 1M tokens) - Standard tier as of Jan 2026
OPENAI_PRICING = {
    'gpt-4.1.2': {'input': 1.75, 'output': 14.00},
    'gpt-4.1': {'input': 2.00, 'output': 8.00},
    'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
}
WEB_SEARCH_COST_PER_CALL = 0.01


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
        pricing = OPENAI_PRICING.get(self.model, {'input': 0.15, 'output': 0.60})
        return (self.input_tokens / 1_000_000) * pricing['input']

    @property
    def output_cost(self) -> float:
        pricing = OPENAI_PRICING.get(self.model, {'input': 0.15, 'output': 0.60})
        return (self.output_tokens / 1_000_000) * pricing['output']

    @property
    def web_search_cost(self) -> float:
        return self.web_search_calls * WEB_SEARCH_COST_PER_CALL

    @property
    def total_cost(self) -> float:
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
    def total_cost(self) -> float:
        return sum(c.total_cost for c in self.calls)

    @property
    def total_input_cost(self) -> float:
        return sum(c.input_cost for c in self.calls)

    @property
    def total_output_cost(self) -> float:
        return sum(c.output_cost for c in self.calls)

    @property
    def total_web_search_cost(self) -> float:
        return sum(c.web_search_cost for c in self.calls)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'model': self.model,
            'total_api_calls': len(self.calls),
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_tokens,
            'total_web_search_calls': self.total_web_search_calls,
            'costs': {
                'input_tokens': sum(c.input_cost for c in self.calls),
                'output_tokens': sum(c.output_cost for c in self.calls),
                'web_search': sum(c.web_search_cost for c in self.calls),
                'total': self.total_cost,
            },
        }


# =============================================================================
# Batch Processing with External State Management
# =============================================================================
# Inspired by insights from arXiv:2512.24601 (Recursive Language Models)
# Key insight: Don't stuff all candidates into one LLM context (causes "context rot")
# Solution: Store candidates externally, process in small batches, aggregate programmatically
# Note: This is iterative batch processing, not true recursive LLM calls.
# =============================================================================

class CandidateREPL:
    """
    External state container for batch candidate processing.

    Instead of stuffing all candidates into one LLM context (causing "context rot"),
    we store them externally and process in iterative batches.

    This is NOT true RLM (recursive self-calls), but applies the same insight:
    - Store state externally (not in LLM context)
    - Process in small batches
    - Aggregate results programmatically
    """

    def __init__(self, candidates: List[Dict]):
        self.candidates = candidates
        self.scores = {}  # candidate_id -> score
        self.reasoning = {}  # candidate_id -> reasoning

    def get_batch(self, start: int, size: int) -> List[Dict]:
        """Get a batch of candidates starting at index."""
        return self.candidates[start:start + size]

    def store_scores(self, batch_scores: Dict[int, tuple]):
        """Store scores from a batch evaluation. batch_scores: {idx: (score, reasoning)}"""
        for idx, (score, reasoning) in batch_scores.items():
            self.scores[idx] = score
            self.reasoning[idx] = reasoning

    def get_top_k(self, k: int) -> List[Dict]:
        """Return top-k candidates sorted by score."""
        scored = []
        for idx, candidate in enumerate(self.candidates):
            score = self.scores.get(idx, 5)  # Default to 5 if not scored
            candidate['validation_score'] = score
            candidate['validation_reasoning'] = self.reasoning.get(idx, '')
            scored.append((score, idx, candidate))

        # Sort by score descending
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [item[2] for item in scored[:k]]

    def __len__(self):
        return len(self.candidates)


class OpenAIWebSearchProvider(BaseProvider):
    """
    PartnerScope Search Provider - 5-Phase Deep Research Architecture

    Implements intelligent partner discovery through:
    - Phase 1: Initial Discovery (multi-angle queries)
    - Phase 2: Strategic Reflection (find non-obvious partners)
    - Phase 3: Need Decomposition (comprehensive coverage)
    - Phase 4: Batch Filtering (consistent scoring)
    - Phase 5: Enrichment (complete data)

    The goal: find partners that genuinely help startups succeed.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=api_key, timeout=300.0)
        self.model = self.config.get('model', 'gpt-4.1')
        self._current_search_usage: SearchUsageSummary = None
        self._last_search_usage: SearchUsageSummary = None

    def _extract_usage(self, response, operation: str) -> TokenUsage:
        """Extract token usage from OpenAI response."""
        usage = TokenUsage(
            model=self.model,
            operation=operation,
            web_search_calls=1,
        )
        if hasattr(response, 'usage') and response.usage:
            usage.input_tokens = getattr(response.usage, 'input_tokens', 0)
            usage.output_tokens = getattr(response.usage, 'output_tokens', 0)
        return usage

    # =========================================================================
    # === TUNABLE: Phase 1 - Query Generation ===
    # =========================================================================
    def _generate_search_queries(self, partner_needs: str, startup_context: dict = None) -> List[str]:
        """
        Generate search query variations.

        EXPERIMENT IDEAS:
        - Try different numbers of queries (3, 5, 8?)
        - Try different angles (competitor analysis, adjacent markets?)
        - Try asking for query + reasoning pairs
        - Try generating queries in multiple rounds
        """
        if not startup_context:
            return [partner_needs]

        startup_name = startup_context.get('startup_name', '')
        industry = startup_context.get('industry', '')
        description = startup_context.get('description', '')
        keywords = startup_context.get('keywords', [])
        investment_stage = startup_context.get('investment_stage', '')
        product_stage = startup_context.get('product_stage', '')

        # === TUNABLE PROMPT ===
        # NOTE: Simple, short queries work better with web search than complex boolean queries
        prompt = f"""Generate 4 web search queries to find partner companies for this startup:

Startup: {startup_name} ({industry})
Stage: {investment_stage}
Looking for: {partner_needs}

RULES FOR QUERIES:
- Keep each query SHORT (5-10 words max)
- Use simple natural language (like you'd type into Google)
- NO boolean operators (no OR, AND, quotes)
- Each query should take a different angle

Output exactly 4 queries, one per line, no numbering:"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        # Track usage
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
            if line and line[0].isdigit():
                if '. ' in line:
                    line = line.split('. ', 1)[-1].strip()
            if line and len(line) > 10:
                queries.append(line)

        return queries[:5] if queries else [partner_needs]

    # =========================================================================
    # === TUNABLE: Phase 1 - Search with Details ===
    # =========================================================================
    def _search_with_details(self, query: str, max_companies: int = 7, user_needs: str = None) -> List[Dict]:
        """
        Single API call that returns companies WITH all details.

        EXPERIMENT IDEAS:
        - Try different company counts per query
        - Try asking for more/fewer fields
        - Try asking for confidence scores
        - Try asking for "why NOT this company" as well
        """
        needs_context = ""
        if user_needs:
            needs_context = f"""
THE USER'S SPECIFIC NEEDS:
"{user_needs}"

When evaluating each company, identify which of these specific needs they can satisfy.
"""

        # === TUNABLE PROMPT ===
        # NOTE: Emphasize partnership potential, not just companies in the space
        prompt = f"""Search the web and find up to {max_companies} companies that would be STRONG PARTNERSHIP CANDIDATES for:

{query}
{needs_context}
IMPORTANT: Focus on companies that:
- Have a track record of partnerships or collaborations
- Work with startups or are open to new partnerships
- Have complementary capabilities (not competitors)

For EACH company, provide:

1. Company Name (official name)
2. Website (official URL)
3. Industry/Sector
4. Location (headquarters)
5. Size (employees or revenue tier)
6. Description (2-3 sentences about what they do)
7. NEEDS SATISFIED: Which specific needs this company addresses (short tags)
8. HOW IT HELPS: One sentence on WHY this company is a good partnership fit

Format as numbered list. Only include real, currently operating companies."""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        usage = self._extract_usage(response, f"Search ({max_companies} companies)")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        return self._parse_companies(response.output_text)

    # =========================================================================
    # === TUNABLE: Phase 2 - Strategic Reflection ===
    # =========================================================================
    def _analyze_and_generate_creative_queries(
        self,
        partner_needs: str,
        startup_context: dict,
        companies_found: List[Dict]
    ) -> List[str]:
        """
        Strategic reflection to find gaps and generate smarter queries.

        EXPERIMENT IDEAS:
        - Try different reflection frameworks
        - Try asking "what would an expert do differently?"
        - Try generating counter-examples
        - Try multi-step reasoning chains
        - Try adding a "critique" step before generating new queries
        """
        company_summary = []
        industries_found = set()
        for c in companies_found[:15]:
            name = c.get('name', 'Unknown')
            industry = c.get('industry', 'Unknown')
            industries_found.add(industry)
            company_summary.append(f"- {name} ({industry})")

        companies_text = '\n'.join(company_summary) if company_summary else "None"
        industries_text = ', '.join(list(industries_found)[:10]) if industries_found else "Unknown"

        startup_name = startup_context.get('startup_name', '') if startup_context else ''
        industry = startup_context.get('industry', '') if startup_context else ''
        description = startup_context.get('description', '') if startup_context else ''
        investment_stage = startup_context.get('investment_stage', '') if startup_context else ''
        product_stage = startup_context.get('product_stage', '') if startup_context else ''

        # === TUNABLE PROMPT ===
        # NOTE: Simplified output format for reliable parsing with gpt-4o-mini
        prompt = f"""You are a strategic partnership consultant.

## STARTUP CONTEXT
- Name: {startup_name}
- Industry: {industry}
- Stage: {investment_stage}, {product_stage}
- Description: {description}

## STATED NEED
"{partner_needs}"

## COMPANIES ALREADY FOUND ({len(companies_found)})
Industries covered: {industries_text}
{companies_text}

## YOUR TASK
Think about what's MISSING. The companies above might be too obvious or too narrow.

Consider:
- What's the REAL underlying problem they're trying to solve?
- What types of partners did we NOT search for?
- What adjacent industries or unconventional partners could help?

## OUTPUT (EXACTLY 3 QUERIES)
Output exactly 3 new search queries that explore different angles.
Use this EXACT format (no markdown, no bullets, no numbers):

QUERY: [your first search query here]
QUERY: [your second search query here]
QUERY: [your third search query here]

Each query should be a realistic web search string, 5-15 words."""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        usage = TokenUsage(
            model=self.model,
            operation="Strategic reflection (Phase 2)",
            input_tokens=getattr(response.usage, 'input_tokens', 0) if response.usage else 0,
            output_tokens=getattr(response.usage, 'output_tokens', 0) if response.usage else 0,
            web_search_calls=0
        )
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        # Parse queries from response with robust handling
        content = response.output_text.strip()
        queries = []

        for line in content.split('\n'):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Remove markdown formatting (**, __, `)
            clean_line = line.replace('**', '').replace('__', '').replace('`', '')

            # Remove leading numbers/bullets (1., 2., -, *, •)
            clean_line = re.sub(r'^[\d]+[\.\)]\s*', '', clean_line)
            clean_line = re.sub(r'^[-\*\•]\s*', '', clean_line)
            clean_line = clean_line.strip()

            # Look for QUERY: anywhere in the line (case-insensitive)
            upper_line = clean_line.upper()
            if 'QUERY:' in upper_line:
                # Extract everything after QUERY:
                idx = upper_line.index('QUERY:')
                query = clean_line[idx + 6:].strip().strip('"\'[]')
                if query and len(query) > 10:
                    queries.append(query)

        # Debug output if no queries found
        if not queries:
            print(f"  [Phase 2 Debug] No queries parsed. Response preview:")
            print(f"    {content[:300]}...")

        return queries[:3]

    # =========================================================================
    # === TUNABLE: Phase 3 - Need Decomposition & Targeted Search ===
    # =========================================================================
    def _decompose_needs(self, partner_needs: str) -> List[str]:
        """
        Decompose partner needs into specific, searchable items.

        This enables targeted search for EACH need, ensuring complete coverage.
        Inspired by deep research's task decomposition pattern.
        """
        prompt = f"""Analyze this partner search request and extract 3-4 DISTINCT needs:

"{partner_needs}"

Rules:
- Each need should be specific and searchable
- Needs should be non-overlapping
- Focus on different TYPES of partners/capabilities needed

Output format (one per line, no numbering):
[first distinct need]
[second distinct need]
[third distinct need]"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        usage = TokenUsage(
            model=self.model,
            operation="Need decomposition (Phase 3)",
            input_tokens=getattr(response.usage, 'input_tokens', 0) if response.usage else 0,
            output_tokens=getattr(response.usage, 'output_tokens', 0) if response.usage else 0,
            web_search_calls=0
        )
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        needs = []
        for line in response.output_text.strip().split('\n'):
            line = line.strip()
            if line and len(line) > 5 and not line[0].isdigit():
                needs.append(line)

        return needs[:4]

    def _search_for_specific_need(self, need: str, startup_context: dict, max_companies: int = 5) -> List[Dict]:
        """
        Targeted search for partners addressing a SPECIFIC need.
        """
        startup_name = startup_context.get('startup_name', '') if startup_context else ''
        industry = startup_context.get('industry', '') if startup_context else ''

        prompt = f"""Search for companies that can help a {industry} startup with this SPECIFIC need:

Need: "{need}"
Startup: {startup_name}

Find {max_companies} companies that are KNOWN FOR or SPECIALIZE IN addressing this exact need.
Look for companies with:
- Track record in this area
- Partnership programs
- Startup-friendly approach

For each company provide:
1. Company Name
2. Website
3. Industry/Sector
4. Location
5. Size
6. Description (2-3 sentences)
7. NEEDS SATISFIED: {need}
8. HOW IT HELPS: Why they're good for this specific need

Format as numbered list."""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        usage = self._extract_usage(response, f"Need search: {need[:20]}")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        return self._parse_companies(response.output_text)

    # =========================================================================
    # === TUNABLE: Phase 4 - Batch Filtering & Ranking ===
    # =========================================================================
    # Inspired by arXiv:2512.24601 (Recursive Language Models)
    # Instead of one big context (causes "context rot"), process in batches
    # with external state, aggregating scores programmatically.
    # Note: This is iterative batch processing, not true recursive calls.
    # =========================================================================

    def _score_candidate_batch(
        self,
        batch: List[Dict],
        batch_start_idx: int,
        partner_needs: str,
        startup_context: dict
    ) -> Dict[int, tuple]:
        """
        RLM sub-call: Score a single batch of candidates.

        Each batch is small enough to avoid context rot.
        Returns: {global_idx: (score, reasoning)}
        """
        startup_name = startup_context.get('startup_name', '') if startup_context else ''
        industry = startup_context.get('industry', '') if startup_context else ''

        # Format batch for evaluation (using local indices 1-N)
        candidates_text = ""
        for local_idx, c in enumerate(batch, 1):
            candidates_text += f"""
{local_idx}. {c.get('name', 'Unknown')}
   Industry: {c.get('industry', 'Unknown')}
   Description: {c.get('description', '')[:150]}
   Tags: {', '.join(c.get('needs_satisfied', []))}
"""

        prompt = f"""You are a STRICT partnership evaluator for {startup_name} ({industry}).

THEIR SPECIFIC NEEDS: "{partner_needs}"

BATCH OF {len(batch)} CANDIDATES:
{candidates_text}

TASK: Score each candidate 1-10 on partnership fit.

Scoring Guide:
- 9-10: DIRECTLY addresses multiple stated needs
- 7-8: Addresses at least one stated need well
- 5-6: Tangentially related but not clear fit
- 1-4: Does NOT address the specific needs

BE CRITICAL. Most should score 5-7. Only 8+ for excellent fits.

Output format (one per line, no extra text):
[number]: [score] | [brief reason]"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        usage = TokenUsage(
            model=self.model,
            operation=f"Batch {batch_start_idx//8 + 1}",
            input_tokens=getattr(response.usage, 'input_tokens', 0) if response.usage else 0,
            output_tokens=getattr(response.usage, 'output_tokens', 0) if response.usage else 0,
            web_search_calls=0
        )
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        # Parse batch scores
        batch_scores = {}
        for line in response.output_text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                try:
                    parts = line.split(':')
                    local_idx = int(re.sub(r'[^\d]', '', parts[0]))
                    rest = parts[1].strip()

                    # Parse score and reasoning
                    if '|' in rest:
                        score_str, reasoning = rest.split('|', 1)
                    else:
                        score_str = rest
                        reasoning = ""

                    score = int(re.search(r'\d+', score_str).group())
                    score = min(max(score, 1), 10)  # Clamp 1-10

                    # Convert local index to global index
                    global_idx = batch_start_idx + local_idx - 1
                    batch_scores[global_idx] = (score, reasoning.strip())
                except:
                    continue

        return batch_scores

    def _validate_and_rank_candidates(
        self,
        candidates: List[Dict],
        partner_needs: str,
        startup_context: dict,
        top_k: int = 15
    ) -> List[Dict]:
        """
        Batch filtering with external state management.

        Inspired by arXiv:2512.24601 (Recursive Language Models):
        - Don't stuff all candidates into one LLM context (causes "context rot")
        - Store candidates externally
        - Process in small iterative batches
        - Aggregate scores programmatically

        Note: This is iterative batch processing, not true recursive LLM calls.
        This approach handles 50+ candidates without quality degradation.
        """
        if len(candidates) <= top_k:
            return candidates

        # Initialize REPL environment with all candidates
        repl = CandidateREPL(candidates)

        # Batch size - small enough to avoid context rot
        # Optimal: 8 candidates per batch (fits in ~2K tokens)
        BATCH_SIZE = 8

        print(f"    [Batch] Processing {len(candidates)} candidates in batches of {BATCH_SIZE}")

        # Recursive sub-calls: process each batch
        num_batches = (len(candidates) + BATCH_SIZE - 1) // BATCH_SIZE

        for batch_num in range(num_batches):
            start_idx = batch_num * BATCH_SIZE
            batch = repl.get_batch(start_idx, BATCH_SIZE)

            if not batch:
                continue

            print(f"    [Batch] Batch {batch_num + 1}/{num_batches}: candidates {start_idx + 1}-{start_idx + len(batch)}")

            # Sub-call: score this batch
            batch_scores = self._score_candidate_batch(
                batch, start_idx, partner_needs, startup_context
            )

            # Store results in REPL environment
            repl.store_scores(batch_scores)

        # Aggregate: get top-k by score
        result = repl.get_top_k(top_k)

        print(f"    [Batch] Complete. Top score: {result[0].get('validation_score', 0) if result else 'N/A'}")

        return result

    # =========================================================================
    # === TUNABLE: Phase 5 - Enrichment ===
    # =========================================================================
    def _needs_enrichment(self, company: Dict) -> bool:
        """Check if company needs detail enrichment."""
        website = company.get('website', '') or ''
        description = company.get('description', '') or ''

        website_missing = not website or not website.startswith('http')
        description_poor = not description or len(description) < 30

        return website_missing or description_poor

    def _enrich_company_details(self, company: Dict) -> Dict:
        """Fetch additional details for a company."""
        company_name = company.get('name', 'Unknown')

        prompt = f"""Search the web for verified information about "{company_name}".

Find:
1. Official Website URL
2. Industry/Sector
3. Headquarters Location
4. Company Size
5. Description (2-3 sentences)

Format:
- Website: [URL]
- Industry: [industry]
- Location: [location]
- Size: [size]
- Description: [description]"""

        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search"}],
            input=prompt
        )

        usage = self._extract_usage(response, f"Enrich: {company_name[:20]}")
        if self._current_search_usage:
            self._current_search_usage.calls.append(usage)

        # Parse and update
        content = response.output_text.strip()
        enriched = company.copy()

        for line in content.split('\n'):
            if ':' in line:
                field, value = line.split(':', 1)
                field = field.lower().strip().lstrip('- ')
                value = value.strip()

                if 'website' in field and value.startswith('http'):
                    enriched['website'] = value
                elif 'industry' in field and value:
                    enriched['industry'] = value
                elif 'location' in field and value:
                    enriched['location'] = value
                elif 'size' in field and value:
                    enriched['size'] = value
                elif 'description' in field and len(value) > 20:
                    enriched['description'] = value

        enriched['enriched'] = True
        return enriched

    # =========================================================================
    # === TUNABLE: Company Parsing ===
    # =========================================================================
    def _parse_companies(self, text: str) -> List[Dict]:
        """Parse company data from LLM response."""
        import re

        companies = []
        current_company = None

        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            # New company header
            company_match = re.match(r'^\d+\.\s*\*?\*?([^*\n]+)\*?\*?\s*$', line)
            if company_match:
                if current_company and current_company.get('name'):
                    companies.append(current_company)

                name = re.sub(r'\*+', '', company_match.group(1)).strip()
                current_company = {
                    'name': name,
                    'website': '',
                    'description': '',
                    'industry': '',
                    'size': '',
                    'location': '',
                    'needs_satisfied': [],
                    'how_it_helps': '',
                    'source': 'openai_web_search',
                }
                continue

            # Parse fields
            if current_company and ':' in line:
                if line.startswith('- ') or line.startswith('• '):
                    line = line[2:].strip()

                field, value = line.split(':', 1)
                field = field.lower().strip()
                value = value.strip()

                if 'website' in field:
                    url_match = re.search(r'https?://[^\s\)]+', value)
                    if url_match:
                        current_company['website'] = url_match.group(0).rstrip('.,;:')
                elif 'industry' in field or 'sector' in field:
                    current_company['industry'] = value
                elif 'location' in field:
                    current_company['location'] = value
                elif 'size' in field:
                    current_company['size'] = value
                elif 'description' in field:
                    current_company['description'] = value
                elif 'needs' in field and 'satisf' in field:
                    tags = [t.strip() for t in value.split(',') if t.strip()]
                    current_company['needs_satisfied'] = tags
                elif 'how' in field and 'help' in field:
                    current_company['how_it_helps'] = value

        if current_company and current_company.get('name'):
            companies.append(current_company)

        return companies

    # =========================================================================
    # === MAIN SEARCH METHOD ===
    # =========================================================================
    def search_companies(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Search - 5-Phase Deep Research Architecture.

        Current architecture:
        - Phase 1: Initial Discovery (4 queries × 6 companies = ~24 candidates)
        - Phase 2: Strategic Reflection (3 creative queries = ~18 candidates)
        - Phase 3: Need Decomposition (3-4 sub-needs × 4 companies = ~16 candidates)
        - Phase 4: Batch Filtering (iterative batch scoring, top-k selection)
        - Phase 5: Selective Enrichment (fill missing data for up to 10 companies)

        References:
        - Batch processing: arXiv:2512.24601
        - PartnerMAS evaluation: arXiv:2509.24046
        """
        self._current_search_usage = SearchUsageSummary(model=self.model)

        max_results = filters.get('max_results', 20) if filters else 20
        startup_context = filters.get('startup_context') if filters else None
        progress_callback = filters.get('progress_callback') if filters else None
        companies_per_query = 6

        print(f"\n{'='*70}")
        print(f"[Search] Starting experimental partner search")
        print(f"  Model: {self.model}")
        print(f"  Target: {max_results} companies")
        print(f"{'='*70}")

        all_companies = []
        seen_names = set()

        def add_companies(results: List[Dict], phase: str) -> int:
            new_count = 0
            for company in results:
                name_key = company['name'].lower().strip()
                name_key = name_key.replace(', inc.', '').replace(' llc', '').replace(' corp', '')
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    company['discovery_phase'] = phase
                    all_companies.append(company)
                    new_count += 1
            return new_count

        # =====================================================================
        # PHASE 1: Initial Discovery
        # =====================================================================
        print(f"\n[Phase 1] Initial Discovery")
        print(f"-" * 40)

        queries = self._generate_search_queries(query, startup_context)
        print(f"  Generated {len(queries)} queries")

        for i, search_query in enumerate(queries, 1):
            print(f"\n  [P1-{i}/{len(queries)}] {search_query[:50]}...")
            try:
                results = self._search_with_details(search_query, companies_per_query, query)
                new_count = add_companies(results, 'phase1')
                print(f"    → Found {len(results)}, {new_count} new. Total: {len(all_companies)}")
            except Exception as e:
                print(f"    → ERROR: {str(e)}")

        phase1_count = len(all_companies)
        print(f"\n  [Phase 1 Complete] {phase1_count} unique companies")

        # =====================================================================
        # PHASE 2: Strategic Reflection
        # =====================================================================
        print(f"\n[Phase 2] Strategic Reflection")
        print(f"-" * 40)

        creative_queries = self._analyze_and_generate_creative_queries(query, startup_context, all_companies)
        print(f"  Generated {len(creative_queries)} creative queries")

        for i, search_query in enumerate(creative_queries, 1):
            print(f"\n  [P2-{i}/{len(creative_queries)}] {search_query[:50]}...")
            try:
                results = self._search_with_details(search_query, companies_per_query, query)
                new_count = add_companies(results, 'phase2')
                print(f"    → Found {len(results)}, {new_count} new. Total: {len(all_companies)}")
            except Exception as e:
                print(f"    → ERROR: {str(e)}")

        phase2_new = len(all_companies) - phase1_count
        print(f"\n  [Phase 2 Complete] Added {phase2_new} companies")

        # =====================================================================
        # PHASE 3: Need Decomposition & Targeted Search (NEW - Deep Research)
        # =====================================================================
        print(f"\n[Phase 3] Need-by-Need Targeted Search")
        print(f"-" * 40)

        phase2_start = len(all_companies)

        # Decompose needs into specific items
        specific_needs = self._decompose_needs(query)
        print(f"  Decomposed into {len(specific_needs)} specific needs:")
        for need in specific_needs:
            print(f"    • {need[:60]}...")

        # Search for each specific need
        for i, need in enumerate(specific_needs, 1):
            print(f"\n  [P3-{i}/{len(specific_needs)}] Searching for: {need[:45]}...")
            try:
                results = self._search_for_specific_need(need, startup_context, max_companies=4)
                new_count = add_companies(results, 'phase3')
                print(f"    → Found {len(results)}, {new_count} new. Total: {len(all_companies)}")
            except Exception as e:
                print(f"    → ERROR: {str(e)}")

        phase3_new = len(all_companies) - phase2_start
        print(f"\n  [Phase 3 Complete] Added {phase3_new} companies")

        # =====================================================================
        # PHASE 4: Batch Filtering & Ranking
        # =====================================================================
        # Inspired by arXiv:2512.24601 - process in batches to avoid "context rot"
        # Note: Iterative batch processing, not true recursive LLM calls
        # =====================================================================
        print(f"\n[Phase 4] Batch Filtering & Ranking")
        print(f"-" * 40)
        print(f"  {len(all_companies)} candidates → iterative batch evaluation")

        if len(all_companies) > max_results:
            all_companies = self._validate_and_rank_candidates(
                all_companies, query, startup_context, top_k=max_results
            )
            print(f"  Filtered to top {len(all_companies)} by partnership fit score")
        else:
            print(f"  Skipped (only {len(all_companies)} candidates)")

        # =====================================================================
        # PHASE 5: Selective Enrichment
        # =====================================================================
        print(f"\n[Phase 5] Selective Enrichment")
        print(f"-" * 40)

        needs_enrichment = [c for c in all_companies if self._needs_enrichment(c)]
        print(f"  {len(needs_enrichment)}/{len(all_companies)} need enrichment")

        if needs_enrichment:
            max_enrichments = min(len(needs_enrichment), 10)
            to_enrich = needs_enrichment[:max_enrichments]

            for i, company in enumerate(to_enrich, 1):
                print(f"  [{i}/{len(to_enrich)}] {company['name'][:35]}...", end=" ")
                try:
                    enriched = self._enrich_company_details(company)
                    idx = all_companies.index(company)
                    all_companies[idx] = enriched
                    print("✓")
                except Exception as e:
                    print(f"✗ {str(e)[:25]}")

        # =====================================================================
        # SUMMARY
        # =====================================================================
        self._last_search_usage = self._current_search_usage
        self._current_search_usage = None

        p1 = sum(1 for c in all_companies if c.get('discovery_phase') == 'phase1')
        p2 = sum(1 for c in all_companies if c.get('discovery_phase') == 'phase2')
        p3 = sum(1 for c in all_companies if c.get('discovery_phase') == 'phase3')

        print(f"\n{'='*70}")
        print(f"[Deep Research Search Complete]")
        print(f"  Phase 1 (Discovery): {p1} companies")
        print(f"  Phase 2 (Reflection): {p2} companies")
        print(f"  Phase 3 (Targeted): {p3} companies")
        print(f"  Phase 4 (Filtered): top {len(all_companies)}")
        print(f"  Total: {len(all_companies)} companies")
        print(f"  Cost: ${self._last_search_usage.total_cost:.2f}")
        print(f"{'='*70}\n")

        if progress_callback:
            progress_callback('complete', f'Found {len(all_companies)} partners',
                            self._last_search_usage.total_cost)

        return all_companies[:max_results]

    def get_last_usage(self) -> SearchUsageSummary:
        """Get token usage from last search."""
        return self._last_search_usage

    def get_company_details(self, company_identifier: str) -> Dict[str, Any]:
        """Get detailed info for a specific company."""
        return self._enrich_company_details({'name': company_identifier})

    def normalize_company_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw company data."""
        return {
            'name': raw_data.get('name', ''),
            'website': raw_data.get('website', ''),
            'description': raw_data.get('description', ''),
            'industry': raw_data.get('industry', ''),
            'size': raw_data.get('size', ''),
            'location': raw_data.get('location', ''),
            'source': 'openai_web_search',
        }
