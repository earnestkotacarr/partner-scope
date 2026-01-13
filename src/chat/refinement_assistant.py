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
        self.model = "gpt-4o-mini"
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

        # Build refinement prompt that handles both filtering AND search expansion
        system_prompt = f"""{REFINEMENT_PROMPT}

## Current Context

Original search was for: {scenario.get('startup_name', 'a startup')}
Industry: {scenario.get('industry', 'Unknown')}
Looking for: {scenario.get('partner_needs', 'partners')}

## Current Results (indexed 0-{len(current_results)-1}):
{results_detail}

## Your Task
Analyze the user's request and decide the best action:

**Option A - FILTER/REORDER existing results:**
Use this when the user wants to narrow down, prioritize, or remove items from current results.
Examples: "top 5", "remove consulting firms", "prioritize universities", "only show US companies"

**Option B - NEW SEARCH:**
Use this when the user wants to find NEW/DIFFERENT partners not in the current results.
Examples: "find more hospitals", "search for manufacturing companies", "look for partners in Japan", "add biotech companies"

Respond in this exact JSON format:

For FILTER/REORDER:
{{
    "action_type": "filter",
    "keep_indices": [0, 2, 5],
    "response": "Brief explanation of what was done"
}}

For NEW SEARCH:
{{
    "action_type": "search",
    "search_query": "specific search query for finding new partners",
    "search_focus": "brief description of what kind of partners to find",
    "merge_mode": "add" | "replace",
    "response": "I'll search for more [type] partners..."
}}

Choose wisely based on user intent. If they say "find", "search", "look for", "add more", or mention specific NEW types not in results, use search.
If they say "show", "keep", "remove", "top", "only", use filter."""

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

        # Get the LLM's refinement decision
        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.3,
            max_tokens=500
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

                # Handle FILTER action
                keep_indices = decision.get('keep_indices', list(range(len(current_results))))

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
