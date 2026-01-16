"""Refinement Assistant - helps users iterate on search results."""

import os
import json
from openai import OpenAI
from .prompts import REFINEMENT_PROMPT
from ..utils.cost_tracker import calculate_cost


class RefinementAssistant:
    """Conversational assistant for iteratively refining search results."""

    def __init__(self):
        self._client = None
        self.model = "gpt-4.1"
        self._last_cost = None  # Track cost of last operation

    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def refine_results(
        self,
        messages: list,
        current_message: str,
        current_results: list,
        scenario: dict
    ) -> dict:
        """
        Process a refinement request and return updated results.

        Args:
            messages: Refinement conversation history
            current_message: The new refinement request
            current_results: Current list of partner matches
            scenario: Original search scenario/template

        Returns:
            dict with 'response', 'refined_results', 'applied_filters', 'action_taken'
            If action_taken is 'search', also includes 'search_query' for new search
        """
        # Build detailed results list for the LLM
        results_detail = self._format_results_for_llm(current_results)
        results_stats = self._get_result_statistics(current_results)

        # Build refinement prompt that handles filtering, search expansion, AND undo
        system_prompt = f"""{REFINEMENT_PROMPT}

## Current Context

Original search was for: {scenario.get('startup_name', 'a startup')}
Industry: {scenario.get('industry', 'Unknown')}
Looking for: {scenario.get('partner_needs', 'partners')}

## Result Statistics (USE THIS TO DECIDE!)
{results_stats}

## Current Results (indexed 0-{len(current_results)-1}):
{results_detail}

## Your Task
Analyze the user's request and decide the best action.

**CRITICAL: Before choosing, CHECK THE STATISTICS ABOVE!**
- If user wants "only in Japan" but Japan: 0 in statistics → use refine_search (NOT filter!)
- If user wants "only healthcare" but Healthcare: 0 → use refine_search (NOT filter!)
- Only use filter if the constraint ALREADY EXISTS in current results!

**Option A - FILTER/REORDER existing results:**
Use ONLY when filtering will keep at least 2 results. Check statistics first!
Examples: "top 5", "remove consulting firms" (if consulting exists), "only US companies" (if US exists)
{{
    "action_type": "filter",
    "keep_indices": [0, 2, 5],
    "response": "Filtered to X results matching your criteria"
}}

**Option B - NEW SEARCH (different partner types):**
Use when user wants completely DIFFERENT types of partners.
Examples: "find hospitals instead", "search for manufacturing companies"
{{
    "action_type": "search",
    "search_query": "specific search query",
    "search_focus": "what kind of partners",
    "merge_mode": "add" | "replace",
    "response": "I'll search for [type] partners..."
}}

**Option C - REFINE SEARCH (MOST COMMON - re-run with constraints):**
Use when user wants to CONSTRAIN the original search to a location, industry, size, etc.
This RE-RUNS the original search WITH the constraint added.
Examples: "only in Japan", "need partners in Europe", "must be enterprise", "I need them in California"
{{
    "action_type": "refine_search",
    "constraint": "in Japan" | "healthcare sector" | "enterprise companies" | etc.,
    "response": "I'll search for partners matching your original criteria but [constraint]..."
}}

**Option D - UNDO/RESET:**
Use when user wants to revert or start over.
Examples: "undo", "go back", "revert", "start over", "reset"
{{
    "action_type": "undo",
    "response": "Reverting to previous results..."
}}

**Option E - CLARIFY:**
Use when the request is too vague to act on.
Examples: "make it better", "improve results", unclear commands
{{
    "action_type": "clarify",
    "response": "Could you be more specific? For example, you could say 'only in Japan' or 'remove consulting firms'..."
}}

## DECISION CHECKLIST:
1. Does user mention a LOCATION (Japan, Europe, USA, etc.)?
   → Check statistics: Is that location in current results?
   → If NO or very few: use refine_search
   → If YES with many results: use filter

2. Does user say "only X" or "must be X"?
   → Check statistics: Does X exist in current results?
   → If NO: use refine_search
   → If YES: use filter

3. Does user want different TYPE of partner (hospitals, lawyers, etc.)?
   → Use search

4. Does user say "undo", "go back", "revert"?
   → Use undo

5. Is request vague or unclear?
   → Use clarify

## IMPORTANT: OUTPUT FORMAT
You MUST respond with ONLY a JSON object. No explanations, no text before or after.
Just output the JSON object matching one of the formats above.

Example for "only in Japan" with no Japan results in statistics:
{{"action_type": "refine_search", "constraint": "in Japan", "response": "I'll search for partners in Japan..."}}"""

        # Build messages for OpenAI
        openai_messages = [{"role": "system", "content": system_prompt}]

        for msg in messages:
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        openai_messages.append({
            "role": "user",
            "content": current_message
        })

        # Get the LLM's refinement decision (force JSON output)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        llm_response = response.choices[0].message.content
        print(f"[Refinement LLM] Response: {llm_response[:200]}...")

        # Extract cost information
        cost_data = None
        if response.usage:
            cost_data = calculate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=self.model
            )
            self._last_cost = cost_data

        # Parse the LLM's response
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                decision = json.loads(json_match.group())
                action_type = decision.get('action_type', 'filter')
                assistant_response = decision.get('response', 'Results have been refined.')

                # Handle NEW SEARCH action
                if action_type == 'search':
                    return {
                        "response": assistant_response,
                        "refined_results": current_results,  # Keep current for now
                        "applied_filters": [],
                        "action_taken": "search",
                        "search_query": decision.get('search_query', scenario.get('partner_needs', '')),
                        "search_focus": decision.get('search_focus', ''),
                        "merge_mode": decision.get('merge_mode', 'add'),
                        "cost": cost_data
                    }

                # Handle REFINE SEARCH action (re-run original search with constraints)
                if action_type == 'refine_search':
                    constraint = decision.get('constraint', '')
                    original_needs = scenario.get('partner_needs', '')
                    # Combine original search with constraint
                    combined_query = f"{original_needs} {constraint}".strip()
                    return {
                        "response": assistant_response,
                        "refined_results": current_results,  # Keep current for now
                        "applied_filters": [],
                        "action_taken": "refine_search",
                        "search_query": combined_query,
                        "search_focus": constraint,
                        "merge_mode": "replace",  # Replace results since this is a refined search
                        "cost": cost_data
                    }

                # Handle UNDO action
                if action_type == 'undo':
                    return {
                        "response": assistant_response,
                        "refined_results": current_results,  # Frontend will handle undo
                        "applied_filters": [],
                        "action_taken": "undo",
                        "cost": cost_data
                    }

                # Handle CLARIFY action (request is too vague)
                if action_type == 'clarify':
                    return {
                        "response": assistant_response,
                        "refined_results": current_results,  # Keep current results
                        "applied_filters": [],
                        "action_taken": "clarify",
                        "cost": cost_data
                    }

                # Handle FILTER action - with validation
                keep_indices = decision.get('keep_indices', list(range(len(current_results))))

                # VALIDATION: If filter would return 0 or too few results, convert to refine_search
                if len(keep_indices) == 0 and len(current_results) > 0:
                    # LLM said filter but would return nothing - try refine_search instead
                    print(f"[Refinement] Filter would return 0 results, converting to refine_search")
                    # Extract constraint from the original message
                    return {
                        "response": "I'll search for partners matching that constraint instead of filtering.",
                        "refined_results": current_results,
                        "applied_filters": [],
                        "action_taken": "refine_search",
                        "search_query": f"{scenario.get('partner_needs', '')} {current_message}",
                        "search_focus": current_message,
                        "merge_mode": "replace",
                        "cost": cost_data
                    }

                # Apply the refinement by selecting only kept indices
                refined_results = []
                for idx in keep_indices:
                    if 0 <= idx < len(current_results):
                        refined_results.append(current_results[idx])

                # If nothing would be kept, return original
                if not refined_results:
                    refined_results = current_results
                    assistant_response = "I couldn't apply that filter without removing all results. Keeping original results."
                    action_type = 'unchanged'

                return {
                    "response": assistant_response,
                    "refined_results": refined_results,
                    "applied_filters": [],
                    "action_taken": action_type if action_type != 'filter' else 'filtered',
                    "cost": cost_data
                }
            else:
                # Fallback: keep all results
                return {
                    "response": llm_response,
                    "refined_results": current_results,
                    "applied_filters": [],
                    "action_taken": "unchanged",
                    "cost": cost_data
                }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[Refinement] JSON parse error: {e}")
            # On parse error, keep all results
            return {
                "response": llm_response,
                "refined_results": current_results,
                "applied_filters": [],
                "action_taken": "unchanged",
                "cost": cost_data
            }

    def _format_results_for_llm(self, results: list) -> str:
        """Format results in a way the LLM can understand and reference by index."""
        lines = []
        for i, r in enumerate(results[:30]):  # Limit to 30 for context
            name = r.get('company_name', 'Unknown')
            info = r.get('company_info', {})
            industry = info.get('industry', 'Unknown')
            location = info.get('location', 'Unknown')
            score = r.get('match_score', 0)
            rationale = r.get('rationale', '')[:100]
            lines.append(f"[{i}] {name} | Industry: {industry} | Location: {location} | Score: {score} | {rationale}...")
        return "\n".join(lines)

    def _get_result_statistics(self, results: list) -> str:
        """Generate statistics about current results to help LLM make informed decisions."""
        if not results:
            return "No results currently."

        # Extract and count countries/regions from locations
        countries = {}
        industries = {}

        country_keywords = {
            'japan': 'Japan', 'tokyo': 'Japan', 'osaka': 'Japan', 'kyoto': 'Japan',
            'usa': 'USA', 'united states': 'USA', 'california': 'USA', 'new york': 'USA',
            'texas': 'USA', 'boston': 'USA', 'san francisco': 'USA', 'seattle': 'USA',
            'china': 'China', 'beijing': 'China', 'shanghai': 'China', 'shenzhen': 'China',
            'germany': 'Germany', 'berlin': 'Germany', 'munich': 'Germany',
            'uk': 'UK', 'united kingdom': 'UK', 'london': 'UK', 'england': 'UK',
            'france': 'France', 'paris': 'France',
            'india': 'India', 'bangalore': 'India', 'mumbai': 'India',
            'canada': 'Canada', 'toronto': 'Canada', 'vancouver': 'Canada',
            'australia': 'Australia', 'sydney': 'Australia', 'melbourne': 'Australia',
            'singapore': 'Singapore',
            'korea': 'South Korea', 'south korea': 'South Korea', 'seoul': 'South Korea',
            'europe': 'Europe', 'asia': 'Asia',
        }

        for r in results:
            info = r.get('company_info', {})
            location = (info.get('location', '') or '').lower()
            industry = info.get('industry', 'Unknown')

            # Detect country from location string
            detected_country = 'Unknown'
            for keyword, country in country_keywords.items():
                if keyword in location:
                    detected_country = country
                    break

            countries[detected_country] = countries.get(detected_country, 0) + 1

            # Simplify industry (take first part if comma-separated)
            simple_industry = industry.split(',')[0].strip()[:30] if industry else 'Unknown'
            industries[simple_industry] = industries.get(simple_industry, 0) + 1

        # Format statistics
        stats_parts = [f"Total: {len(results)} results"]

        # Countries breakdown
        country_list = sorted(countries.items(), key=lambda x: x[1], reverse=True)
        country_str = ", ".join([f"{c}: {n}" for c, n in country_list])
        stats_parts.append(f"Countries: {country_str}")

        # Industries breakdown
        industry_list = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]
        industry_str = ", ".join([f"{i}: {n}" for i, n in industry_list])
        stats_parts.append(f"Industries: {industry_str}")

        return "\n".join(stats_parts)

    def _summarize_results(self, results: list) -> str:
        """Create a summary of current results for context."""
        if not results:
            return "No results currently."

        # Count by industry
        industries = {}
        locations = {}

        for r in results[:20]:  # Limit to first 20 for summary
            info = r.get('company_info', {})
            industry = info.get('industry', 'Unknown')
            location = info.get('location', 'Unknown')

            industries[industry] = industries.get(industry, 0) + 1
            locations[location] = locations.get(location, 0) + 1

        summary_parts = []

        if industries:
            top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]
            ind_str = ", ".join([f"{k}: {v}" for k, v in top_industries])
            summary_parts.append(f"Industries: {ind_str}")

        if locations:
            top_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
            loc_str = ", ".join([f"{k}: {v}" for k, v in top_locations])
            summary_parts.append(f"Locations: {loc_str}")

        # List top companies
        top_companies = [r.get('company_name', 'Unknown') for r in results[:5]]
        summary_parts.append(f"Top matches: {', '.join(top_companies)}")

        return "\n".join(summary_parts)

    def _apply_refinement(
        self,
        request: str,
        results: list,
        scenario: dict
    ) -> tuple:
        """
        Apply the refinement request to the results.

        Returns:
            (action_type, refined_results)
        """
        request_lower = request.lower()

        # Detect action type and apply
        if any(word in request_lower for word in ['remove', 'exclude', 'filter out', 'no ', 'without']):
            return self._apply_filter(request_lower, results)

        elif any(word in request_lower for word in ['prioritize', 'prefer', 'first', 'top', 'rank']):
            return self._apply_reorder(request_lower, results)

        elif any(word in request_lower for word in ['only', 'just', 'focus']):
            return self._apply_narrow(request_lower, results)

        elif any(word in request_lower for word in ['also', 'add', 'more', 'expand']):
            # For expand, we'd need to trigger a new search - for now just return current
            return ("expanded", results)

        else:
            # Try to interpret as a filter
            return self._apply_filter(request_lower, results)

    def _apply_filter(self, request: str, results: list) -> tuple:
        """Filter out results based on request."""
        filtered = []

        for r in results:
            info = r.get('company_info', {})
            industry = (info.get('industry', '') or '').lower()
            location = (info.get('location', '') or '').lower()
            description = (info.get('description', '') or '').lower()
            name = (r.get('company_name', '') or '').lower()

            # Check if this result should be excluded
            exclude = False

            # Check for industry-based exclusions
            if 'software' in request and 'software' in industry:
                exclude = True
            if 'hardware' in request and 'hardware' not in industry and 'manufacturing' not in industry:
                exclude = True

            # Check for location-based exclusions
            common_locations = ['us', 'usa', 'united states', 'china', 'japan', 'europe', 'asia']
            for loc in common_locations:
                if f'exclude {loc}' in request or f'no {loc}' in request or f'not {loc}' in request:
                    if loc in location:
                        exclude = True
                if f'only {loc}' in request or f'just {loc}' in request:
                    if loc not in location:
                        exclude = True

            if not exclude:
                filtered.append(r)

        # If we filtered too aggressively, return original
        if len(filtered) < 2 and len(results) > 2:
            return ("filtered", results)

        return ("filtered", filtered)

    def _apply_reorder(self, request: str, results: list) -> tuple:
        """Reorder results based on request."""
        # Simple scoring based on keyword matches
        def score_result(r):
            score = 0
            info = r.get('company_info', {})
            industry = (info.get('industry', '') or '').lower()
            description = (info.get('description', '') or '').lower()
            name = (r.get('company_name', '') or '').lower()

            # Check for priority keywords in request
            priority_keywords = ['robotics', 'healthcare', 'manufacturing', 'technology',
                               'software', 'hardware', 'research', 'medical']

            for keyword in priority_keywords:
                if keyword in request:
                    if keyword in industry or keyword in description or keyword in name:
                        score += 10

            return score

        # Sort by score (descending), then by original match_score
        sorted_results = sorted(
            results,
            key=lambda r: (score_result(r), r.get('match_score', 0)),
            reverse=True
        )

        return ("reordered", sorted_results)

    def _apply_narrow(self, request: str, results: list) -> tuple:
        """Narrow results to a specific subset."""
        # Check for "top N" pattern
        import re
        top_match = re.search(r'top (\d+)', request)
        if top_match:
            n = int(top_match.group(1))
            return ("narrowed", results[:n])

        # Otherwise apply as filter
        return self._apply_filter(request, results)
