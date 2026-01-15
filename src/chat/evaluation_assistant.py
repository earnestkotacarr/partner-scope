"""
Evaluation Chat Assistant

Handles conversational evaluation workflow through chat interface.
Integrates with the multi-agent evaluation framework.
"""

import os
import json
import uuid
from openai import OpenAI
from ..utils.cost_tracker import calculate_cost


EVALUATION_CHAT_PROMPT = """You are an AI partner evaluation assistant. You help startups evaluate potential partners using a multi-dimensional analysis framework.

## Your Role
You guide users through a structured evaluation process:
1. **Strategy Planning** - Propose and refine evaluation dimensions and weights
2. **Evaluation Execution** - Run multi-dimensional assessments
3. **Results & Insights** - Present rankings, explain decisions, handle refinements

## Evaluation Dimensions Available
- market_compatibility: Market alignment, customer segments, positioning
- financial_health: Financial stability, revenue, funding status
- technical_synergy: Technology compatibility and integration potential
- operational_capacity: Supply chain, logistics, operational capabilities
- geographic_coverage: Geographic presence and regional expertise
- strategic_alignment: Business goals and long-term vision alignment
- cultural_fit: Organizational culture compatibility
- resource_complementarity: Complementary resources and expertise
- growth_potential: Mutual growth and scalability potential
- risk_profile: Risk factors and potential challenges

## Response Guidelines
- Be concise but informative
- Use markdown formatting for better readability
- When showing rankings, use numbered lists
- Explain your reasoning when making recommendations
- Be proactive in suggesting next steps

## Current Phase: {phase}
"""


class EvaluationChatAssistant:
    """Conversational assistant for partner evaluation."""

    def __init__(self):
        self._client = None
        self.model = "gpt-4o-mini"

    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            self._client = OpenAI(api_key=api_key)
        return self._client

    def chat(
        self,
        messages: list,
        current_message: str,
        session_id: str = None,
        phase: str = "init",
        candidates: list = None,
        startup_profile: dict = None,
        strategy: dict = None,
        evaluation_result: dict = None,
        action_hint: str = None,
    ) -> dict:
        """
        Process a chat message and return response with updated state.

        Args:
            action_hint: Explicit action from frontend buttons (e.g., 'start', 'confirm')
                        Takes precedence over string-based detection.

        Returns:
            dict with 'response', 'session_id', 'phase', 'strategy', 'evaluation_result', 'cost'
        """
        candidates = candidates or []
        startup_profile = startup_profile or {}

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Priority 1: Handle explicit action hints from frontend buttons
        if action_hint:
            if action_hint in ['start', 'propose_strategy']:
                return self._handle_start_evaluation(
                    session_id, candidates, startup_profile
                )
            if action_hint in ['confirm', 'confirm_and_run', 'run', 'execute']:
                return self._handle_run_evaluation(
                    session_id, candidates, startup_profile, strategy
                )

        # Priority 2: Determine action based on message content (fallback)
        message_lower = current_message.lower().strip()

        # Handle "start" command
        if message_lower in ['start', 'begin', 'go', 'start evaluation']:
            return self._handle_start_evaluation(
                session_id, candidates, startup_profile
            )

        # Handle strategy modification requests
        if phase in ['init', 'planning'] and any(
            kw in message_lower for kw in ['adjust', 'change', 'modify', 'weight', 'focus', 'more', 'less']
        ):
            return self._handle_strategy_modification(
                session_id, current_message, candidates, startup_profile, strategy
            )

        # Handle confirm and run
        if phase == 'planning' and any(
            kw in message_lower for kw in ['confirm', 'run', 'execute', 'proceed', 'looks good', 'ok', 'yes']
        ):
            return self._handle_run_evaluation(
                session_id, candidates, startup_profile, strategy
            )

        # Handle result queries and refinements (in complete phase)
        if phase == 'complete' and evaluation_result:
            # Check if this is a refinement request
            if self._is_refinement_request(current_message):
                return self._handle_result_refinement(
                    session_id, current_message, evaluation_result, strategy
                )
            # Otherwise handle as a query
            return self._handle_result_query(
                session_id, current_message, evaluation_result, strategy
            )

        # Default: general conversation
        return self._handle_general_conversation(
            session_id, phase, current_message, messages,
            candidates, startup_profile, strategy, evaluation_result
        )

    def _handle_start_evaluation(
        self, session_id: str, candidates: list, startup_profile: dict
    ) -> dict:
        """Generate initial strategy proposal."""

        # Build context about candidates
        candidate_summary = self._summarize_candidates(candidates)

        prompt = f"""Based on this startup and candidates, propose an evaluation strategy.

STARTUP PROFILE:
- Name: {startup_profile.get('name', 'Unknown')}
- Industry: {startup_profile.get('industry', 'Unknown')}
- Stage: {startup_profile.get('stage', 'Unknown')}
- Partner Needs: {startup_profile.get('partner_needs', 'Not specified')}

CANDIDATES SUMMARY ({len(candidates)} total):
{candidate_summary}

Create a focused evaluation strategy with 4-5 most relevant dimensions.
Weights must sum to 1.0.

Respond in JSON format:
{{
    "strategy": {{
        "dimensions": [
            {{"dimension": "dimension_key", "weight": 0.25, "priority": 1, "rationale": "Why important"}}
        ],
        "total_candidates": {len(candidates)},
        "top_k": 5,
        "exclusion_criteria": []
    }},
    "response": "Your natural language explanation of the strategy to show to the user"
}}
"""

        response, cost = self._call_llm(prompt)

        try:
            parsed = self._parse_json_response(response)
            strategy = parsed.get('strategy', {})
            text_response = parsed.get('response', self._format_strategy_response(strategy))
        except:
            # Fallback to default strategy
            strategy = self._get_default_strategy(len(candidates), startup_profile)
            text_response = self._format_strategy_response(strategy)

        return {
            "response": text_response,
            "session_id": session_id,
            "phase": "planning",
            "strategy": strategy,
            "evaluation_result": None,
            "cost": cost,
        }

    def _handle_strategy_modification(
        self, session_id: str, request: str, candidates: list,
        startup_profile: dict, current_strategy: dict
    ) -> dict:
        """Modify strategy based on user request."""

        prompt = f"""Modify this evaluation strategy based on the user's request.

CURRENT STRATEGY:
{json.dumps(current_strategy, indent=2) if current_strategy else 'No strategy yet'}

USER REQUEST: "{request}"

CONTEXT:
- Industry: {startup_profile.get('industry', 'Unknown')}
- Partner Needs: {startup_profile.get('partner_needs', 'Not specified')}
- Candidates: {len(candidates)}

Modify the strategy accordingly. Ensure weights still sum to 1.0.

Respond in JSON format:
{{
    "strategy": {{
        "dimensions": [
            {{"dimension": "dimension_key", "weight": 0.25, "priority": 1, "rationale": "Why important"}}
        ],
        "total_candidates": {len(candidates)},
        "top_k": 5,
        "exclusion_criteria": []
    }},
    "changes": ["List of changes made"],
    "response": "Explanation of changes for the user"
}}
"""

        response, cost = self._call_llm(prompt)

        try:
            parsed = self._parse_json_response(response)
            strategy = parsed.get('strategy', current_strategy)
            text_response = parsed.get('response', 'Strategy updated.')
        except:
            strategy = current_strategy
            text_response = "I couldn't process that modification. The strategy remains unchanged."

        return {
            "response": text_response,
            "session_id": session_id,
            "phase": "planning",
            "strategy": strategy,
            "evaluation_result": None,
            "cost": cost,
        }

    def _handle_run_evaluation(
        self, session_id: str, candidates: list,
        startup_profile: dict, strategy: dict
    ) -> dict:
        """Run the multi-dimensional evaluation using batch processing."""

        dimensions = strategy.get('dimensions', []) if strategy else []
        top_k = strategy.get('top_k', 10) if strategy else 10

        # Batch evaluation: process candidates in batches of 5
        batch_size = 5
        all_evaluations = []
        total_cost = {"input_tokens": 0, "output_tokens": 0, "total_cost": 0}

        print(f"[EvaluationChat] Starting batch evaluation of {len(candidates)} candidates")

        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i + batch_size]
            batch_num = i // batch_size + 1
            print(f"[EvaluationChat] Processing batch {batch_num}: candidates {i+1}-{i+len(batch)}")

            batch_results, batch_cost = self._evaluate_batch(
                batch, startup_profile, dimensions, start_index=i
            )

            all_evaluations.extend(batch_results)

            # Accumulate cost
            if batch_cost:
                total_cost["input_tokens"] += batch_cost.get("input_tokens", 0)
                total_cost["output_tokens"] += batch_cost.get("output_tokens", 0)
                total_cost["total_cost"] += batch_cost.get("total_cost", 0)

        # Sort all evaluations by final_score and assign ranks
        all_evaluations.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        for rank, eval_item in enumerate(all_evaluations, 1):
            eval_item['rank'] = rank

        # Generate summary and insights
        summary, insights, summary_cost = self._generate_evaluation_summary(
            all_evaluations[:top_k], startup_profile, strategy
        )

        if summary_cost:
            total_cost["input_tokens"] += summary_cost.get("input_tokens", 0)
            total_cost["output_tokens"] += summary_cost.get("output_tokens", 0)
            total_cost["total_cost"] += summary_cost.get("total_cost", 0)

        evaluation_result = {
            "top_candidates": all_evaluations[:top_k],
            "total_evaluated": len(all_evaluations),
            "summary": summary,
            "insights": insights,
            "conflicts_resolved": [],
        }

        text_response = self._format_evaluation_summary(evaluation_result)

        return {
            "response": text_response,
            "session_id": session_id,
            "phase": "complete",
            "strategy": strategy,
            "evaluation_result": evaluation_result,
            "cost": total_cost,
        }

    def _evaluate_batch(
        self, batch: list, startup_profile: dict, dimensions: list, start_index: int = 0
    ) -> tuple:
        """Evaluate a batch of candidates."""

        prompt = f"""Evaluate these {len(batch)} candidates for partnership potential.

STARTUP:
- Name: {startup_profile.get('name', 'Unknown')}
- Industry: {startup_profile.get('industry', 'Unknown')}
- Partner Needs: {startup_profile.get('partner_needs', 'Not specified')}

EVALUATION DIMENSIONS:
{json.dumps(dimensions, indent=2)}

CANDIDATES:
{self._format_candidates_for_eval(batch)}

For EACH candidate, provide:
1. Score on each dimension (0-100) with confidence (0-1)
2. Calculate weighted final score
3. List 1-2 strengths and 1-2 weaknesses
4. One recommendation

Respond in JSON format:
{{
    "evaluations": [
        {{
            "candidate_id": "id",
            "candidate_name": "Name",
            "candidate_info": {{"industry": "...", "location": "...", "description": "..."}},
            "final_score": 85,
            "dimension_scores": [
                {{"dimension": "dimension_key", "score": 90, "confidence": 0.8, "evidence": ["brief evidence"]}}
            ],
            "strengths": ["strength1"],
            "weaknesses": ["weakness1"],
            "recommendations": ["recommendation1"],
            "flags": []
        }}
    ]
}}
"""

        response, cost = self._call_llm(prompt, max_tokens=3000)

        try:
            parsed = self._parse_json_response(response)
            evaluations = parsed.get('evaluations', [])

            # Ensure each evaluation has required fields
            for eval_item in evaluations:
                if 'final_score' not in eval_item:
                    # Calculate final score from dimension scores if missing
                    eval_item['final_score'] = self._calculate_final_score(
                        eval_item.get('dimension_scores', []), dimensions
                    )

            return evaluations, cost

        except Exception as e:
            print(f"[EvaluationChat] Batch parse error: {e}")
            # Fallback: create basic evaluations for this batch
            fallback_evals = []
            for i, c in enumerate(batch):
                info = c.get('company_info', {})
                fallback_evals.append({
                    "candidate_id": c.get('id', c.get('company_name', f'candidate_{start_index + i}')),
                    "candidate_name": c.get('company_name', 'Unknown'),
                    "candidate_info": info,
                    "final_score": 50,
                    "dimension_scores": [
                        {"dimension": d['dimension'], "score": 50, "confidence": 0.5}
                        for d in dimensions[:5]
                    ],
                    "strengths": ["Data available"],
                    "weaknesses": ["Limited information"],
                    "recommendations": ["Further review recommended"],
                    "flags": [],
                })
            return fallback_evals, cost

    def _calculate_final_score(self, dimension_scores: list, dimensions: list) -> float:
        """Calculate weighted final score from dimension scores."""
        if not dimension_scores or not dimensions:
            return 50.0

        # Create weight lookup
        weights = {d['dimension']: d.get('weight', 0.2) for d in dimensions}

        total_weighted = 0
        total_weight = 0

        for ds in dimension_scores:
            dim = ds.get('dimension', '')
            score = ds.get('score', 50)
            confidence = ds.get('confidence', 0.7)
            weight = weights.get(dim, 0.2)

            total_weighted += score * weight * confidence
            total_weight += weight * confidence

        if total_weight == 0:
            return 50.0

        return round(total_weighted / total_weight, 1)

    def _generate_evaluation_summary(
        self, top_candidates: list, startup_profile: dict, strategy: dict
    ) -> tuple:
        """Generate summary and insights for the evaluation."""

        top_names = [c.get('candidate_name', 'Unknown') for c in top_candidates[:5]]

        # Build candidate data for the prompt
        candidate_data = [
            {"name": c.get("candidate_name"), "score": c.get("final_score"), "strengths": c.get("strengths", [])}
            for c in top_candidates[:5]
        ]

        prompt = f"""Based on this evaluation, generate a brief summary and insights.

STARTUP: {startup_profile.get('name', 'Unknown')} - {startup_profile.get('industry', 'Unknown')}

TOP CANDIDATES:
{json.dumps(candidate_data, indent=2)}

Respond in JSON:
{{
    "summary": "Brief 1-2 sentence summary of the evaluation results",
    "insights": ["Insight 1 about patterns or recommendations", "Insight 2", "Insight 3"]
}}
"""

        response, cost = self._call_llm(prompt, max_tokens=500)

        try:
            parsed = self._parse_json_response(response)
            return parsed.get('summary', ''), parsed.get('insights', []), cost
        except:
            return f"Evaluated candidates. Top recommendation: {top_names[0] if top_names else 'N/A'}", [], cost

    def _handle_result_query(
        self, session_id: str, query: str, evaluation_result: dict, strategy: dict
    ) -> dict:
        """Handle queries about evaluation results."""

        prompt = f"""Answer this question about the evaluation results.

QUESTION: "{query}"

EVALUATION RESULTS:
{json.dumps(evaluation_result, indent=2)}

STRATEGY USED:
{json.dumps(strategy, indent=2) if strategy else 'Default strategy'}

Provide a helpful, concise answer. Use markdown formatting.
"""

        response, cost = self._call_llm(prompt)

        return {
            "response": response,
            "session_id": session_id,
            "phase": "complete",
            "strategy": strategy,
            "evaluation_result": evaluation_result,
            "cost": cost,
        }

    def _is_refinement_request(self, message: str) -> bool:
        """Detect if a message is a refinement request vs a simple query."""
        message_lower = message.lower()

        refinement_keywords = [
            'exclude', 'remove', 'drop', 'filter out', 'without',
            'reweight', 're-weight', 'change weight', 'adjust weight',
            'focus more', 'focus less', 'prioritize', 'deprioritize',
            'recalculate', 're-rank', 'rerank', 'sort by',
            'only show', 'just the', 'top 3', 'top 5', 'best 3',
        ]

        return any(kw in message_lower for kw in refinement_keywords)

    def _handle_result_refinement(
        self, session_id: str, request: str, evaluation_result: dict, strategy: dict
    ) -> dict:
        """Handle post-evaluation refinement requests."""

        top_candidates = evaluation_result.get('top_candidates', [])
        dimensions = strategy.get('dimensions', []) if strategy else []

        prompt = f"""The user wants to refine evaluation results. Determine and apply the refinement.

CURRENT RESULTS ({len(top_candidates)} candidates):
{json.dumps([{"name": c.get("candidate_name"), "rank": c.get("rank"), "score": c.get("final_score")} for c in top_candidates], indent=2)}

CURRENT DIMENSIONS:
{json.dumps([{"dimension": d.get("dimension"), "weight": d.get("weight")} for d in dimensions], indent=2)}

USER REQUEST: "{request}"

Determine what refinement is needed:
1. EXCLUDE - Remove specific candidates and re-rank remaining
2. REWEIGHT - Adjust dimension weights and recalculate scores
3. FOCUS - Provide deeper analysis on specific aspect
4. FILTER - Show subset (e.g., "top 3")

Respond in JSON:
{{
    "action": "exclude|reweight|focus|filter",
    "details": {{
        "exclude_names": ["names to exclude"] OR
        "new_weights": {{"dimension": weight}} OR
        "focus_aspect": "aspect" OR
        "filter_count": 3
    }},
    "response": "Explanation of what was done",
    "modified_candidates": [] // If action requires modification, return the updated candidate list
}}
"""

        response, cost = self._call_llm(prompt, max_tokens=2000)

        try:
            parsed = self._parse_json_response(response)
            action = parsed.get('action', 'focus')
            details = parsed.get('details', {})
            text_response = parsed.get('response', 'Refinement applied.')

            modified_result = evaluation_result.copy()

            if action == 'exclude':
                # Remove excluded candidates and re-rank
                exclude_names = [n.lower() for n in details.get('exclude_names', [])]
                filtered = [
                    c for c in top_candidates
                    if c.get('candidate_name', '').lower() not in exclude_names
                ]
                # Re-rank
                for i, c in enumerate(filtered, 1):
                    c['rank'] = i
                modified_result['top_candidates'] = filtered

            elif action == 'reweight':
                # Recalculate scores with new weights
                new_weights = details.get('new_weights', {})
                if new_weights:
                    # Update strategy weights
                    updated_dims = []
                    for d in dimensions:
                        dim_name = d['dimension']
                        new_weight = new_weights.get(dim_name, d.get('weight', 0.2))
                        updated_dims.append({**d, 'weight': new_weight})

                    # Normalize weights to sum to 1.0
                    total = sum(d['weight'] for d in updated_dims)
                    if total > 0:
                        for d in updated_dims:
                            d['weight'] = d['weight'] / total

                    # Recalculate final scores
                    for c in top_candidates:
                        c['final_score'] = self._calculate_final_score(
                            c.get('dimension_scores', []), updated_dims
                        )

                    # Re-sort and re-rank
                    top_candidates.sort(key=lambda x: x.get('final_score', 0), reverse=True)
                    for i, c in enumerate(top_candidates, 1):
                        c['rank'] = i

                    modified_result['top_candidates'] = top_candidates
                    strategy['dimensions'] = updated_dims

            elif action == 'filter':
                # Show subset
                filter_count = details.get('filter_count', 5)
                modified_result['top_candidates'] = top_candidates[:filter_count]

            # For 'focus', just return the text response without modifying results

            return {
                "response": text_response,
                "session_id": session_id,
                "phase": "complete",
                "strategy": strategy,
                "evaluation_result": modified_result,
                "cost": cost,
            }

        except Exception as e:
            print(f"[EvaluationChat] Refinement parse error: {e}")
            return {
                "response": f"I understood you want to refine the results, but I had trouble processing that. Could you be more specific? For example:\n- \"Exclude [company name]\"\n- \"Focus more on technical synergy\"\n- \"Show only the top 3\"",
                "session_id": session_id,
                "phase": "complete",
                "strategy": strategy,
                "evaluation_result": evaluation_result,
                "cost": cost,
            }

    def _handle_general_conversation(
        self, session_id: str, phase: str, message: str, history: list,
        candidates: list, startup_profile: dict, strategy: dict, evaluation_result: dict
    ) -> dict:
        """Handle general conversation in any phase."""

        context = f"""
Current Phase: {phase}
Candidates: {len(candidates)}
Startup: {startup_profile.get('name', 'Unknown')} - {startup_profile.get('industry', 'Unknown')}
Has Strategy: {bool(strategy)}
Has Results: {bool(evaluation_result)}
"""

        system_prompt = EVALUATION_CHAT_PROMPT.format(phase=phase) + f"\n\nContext:\n{context}"

        # Build conversation
        openai_messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-10:]:  # Last 10 messages for context
            openai_messages.append({"role": msg["role"], "content": msg["content"]})

        openai_messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=1000
        )

        text_response = response.choices[0].message.content

        cost = None
        if response.usage:
            cost = calculate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=self.model
            )

        return {
            "response": text_response,
            "session_id": session_id,
            "phase": phase,
            "strategy": strategy,
            "evaluation_result": evaluation_result,
            "cost": cost,
        }

    def _call_llm(self, prompt: str, max_tokens: int = 2000) -> tuple:
        """Make an LLM call and return (response, cost)."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an evaluation assistant. Always respond in valid JSON when requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )

        text = response.choices[0].message.content

        cost = None
        if response.usage:
            cost = calculate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=self.model
            )

        return text, cost

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from LLM response."""
        import re

        # Try direct parse
        try:
            return json.loads(response)
        except:
            pass

        # Try extracting from markdown
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Try finding JSON object
        brace_start = response.find('{')
        brace_end = response.rfind('}') + 1
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(response[brace_start:brace_end])
            except:
                pass

        raise ValueError("Could not parse JSON from response")

    def _summarize_candidates(self, candidates: list) -> str:
        """Create a summary of candidates for context."""
        if not candidates:
            return "No candidates available."

        industries = {}
        for c in candidates[:20]:
            info = c.get('company_info', {})
            industry = info.get('industry', 'Unknown')
            industries[industry] = industries.get(industry, 0) + 1

        top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]
        industry_str = ", ".join([f"{k}: {v}" for k, v in top_industries])

        top_names = [c.get('company_name', 'Unknown') for c in candidates[:5]]

        return f"Industries: {industry_str}\nTop candidates: {', '.join(top_names)}"

    def _format_candidates_for_eval(self, candidates: list) -> str:
        """Format candidates for evaluation prompt."""
        lines = []
        for i, c in enumerate(candidates):
            name = c.get('company_name', 'Unknown')
            info = c.get('company_info', {})
            lines.append(f"""
Candidate {i+1}: {name}
- ID: {c.get('id', name)}
- Industry: {info.get('industry', 'Unknown')}
- Location: {info.get('location', 'Unknown')}
- Description: {info.get('description', 'No description')[:200]}
- Website: {info.get('website', 'N/A')}
""")
        return "\n".join(lines)

    def _get_default_strategy(self, num_candidates: int, profile: dict) -> dict:
        """Generate a default evaluation strategy."""
        return {
            "dimensions": [
                {"dimension": "market_compatibility", "weight": 0.25, "priority": 1, "rationale": "Alignment with target market"},
                {"dimension": "technical_synergy", "weight": 0.25, "priority": 2, "rationale": "Technology compatibility"},
                {"dimension": "strategic_alignment", "weight": 0.20, "priority": 3, "rationale": "Business goals alignment"},
                {"dimension": "growth_potential", "weight": 0.15, "priority": 4, "rationale": "Partnership growth opportunity"},
                {"dimension": "risk_profile", "weight": 0.15, "priority": 5, "rationale": "Risk assessment"},
            ],
            "total_candidates": num_candidates,
            "top_k": min(5, num_candidates),
            "exclusion_criteria": [],
            "confirmed_by_user": False,
        }

    def _format_strategy_response(self, strategy: dict) -> str:
        """Format strategy as readable text."""
        dims = strategy.get('dimensions', [])
        lines = ["Here's my proposed evaluation strategy:\n"]

        for i, d in enumerate(sorted(dims, key=lambda x: x.get('priority', 99))):
            name = d['dimension'].replace('_', ' ').title()
            weight = int(d.get('weight', 0) * 100)
            rationale = d.get('rationale', '')
            lines.append(f"**{i+1}. {name}** ({weight}%)")
            if rationale:
                lines.append(f"   _{rationale}_\n")

        lines.append(f"\nThis will evaluate **{strategy.get('total_candidates', 0)} candidates** and return the top {strategy.get('top_k', 5)}.")
        lines.append("\nWould you like to adjust any weights, or shall I **run the evaluation**?")

        return "\n".join(lines)

    def _format_evaluation_summary(self, result: dict) -> str:
        """Format evaluation result as readable text."""
        top = result.get('top_candidates', [])
        total_evaluated = result.get('total_evaluated', len(top))
        summary = result.get('summary', '')
        insights = result.get('insights', [])

        lines = [f"## Evaluation Complete!\n"]
        lines.append(f"Evaluated **{total_evaluated}** candidates.\n")

        if summary:
            lines.append(summary + "\n")

        lines.append("### Top Recommended Partners\n")

        for c in top[:5]:
            rank = c.get('rank', '?')
            name = c.get('candidate_name', 'Unknown')
            score = round(c.get('final_score', 0))
            lines.append(f"**{rank}. {name}** - Score: {score}")

            strengths = c.get('strengths', [])[:2]
            if strengths:
                lines.append(f"   + {', '.join(strengths)}")

        if insights:
            lines.append("\n### Key Insights")
            for insight in insights[:3]:
                lines.append(f"- {insight}")

        lines.append("\nClick on any candidate to view details, or ask me for comparisons!")

        return "\n".join(lines)

    def _generate_simple_ranking(self, candidates: list, dimensions: list) -> dict:
        """Generate simple ranking when LLM parsing fails."""
        top_candidates = []

        for i, c in enumerate(candidates[:10]):
            info = c.get('company_info', {})
            top_candidates.append({
                "candidate_id": c.get('id', c.get('company_name', f'candidate_{i}')),
                "candidate_name": c.get('company_name', 'Unknown'),
                "candidate_info": info,
                "final_score": max(50, 95 - i * 5),
                "rank": i + 1,
                "dimension_scores": [
                    {"dimension": d['dimension'], "score": max(50, 90 - i * 3), "confidence": 0.7}
                    for d in dimensions[:5]
                ],
                "strengths": ["Data available for evaluation"],
                "weaknesses": [],
                "recommendations": ["Review company details"],
                "flags": [],
            })

        return {
            "top_candidates": top_candidates,
            "summary": f"Ranked {len(top_candidates)} candidates based on available data.",
            "insights": ["Further detailed analysis recommended"],
            "conflicts_resolved": [],
        }
