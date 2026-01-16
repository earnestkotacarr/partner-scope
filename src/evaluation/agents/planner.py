"""
Planner Agent for Strategy Formulation & User Alignment (Phase 1).

The Planner Agent analyzes startup profiles and partner requirements to:
1. Decompose the evaluation problem
2. Propose evaluation dimensions with weights
3. Generate a strategy for user confirmation
4. Handle user modifications to the strategy
"""

import json
from typing import Dict, List, Any, Optional

from .base import BaseAgent, AgentResponse
from ..models import (
    EvaluationDimension,
    DimensionWeight,
    EvaluationStrategy,
    StartupProfile,
)


class PlannerAgent(BaseAgent):
    """
    Planner Agent for strategy formulation.

    Responsibilities:
    - Analyze startup profile and partner requirements
    - Propose relevant evaluation dimensions
    - Assign initial importance weights
    - Handle user feedback and strategy modifications
    """

    def __init__(self, model: str = "gpt-4.1", temperature: float = 0.3):
        super().__init__(
            name="planner",
            model=model,
            temperature=temperature,
            max_tokens=4096,
        )

    def get_system_prompt(self) -> str:
        return """You are a strategic planning agent for partner evaluation.

Your role is to analyze startup profiles and partner requirements, then propose an evaluation strategy with appropriate dimensions and weights.

Available evaluation dimensions:
1. market_compatibility - Market alignment, customer segments, positioning
2. financial_health - Financial stability, revenue, funding status
3. technical_synergy - Technology compatibility and integration potential
4. operational_capacity - Supply chain, logistics, operational capabilities
5. geographic_coverage - Geographic presence and regional expertise
6. strategic_alignment - Business goals and long-term vision alignment
7. cultural_fit - Organizational culture compatibility
8. resource_complementarity - Complementary resources and expertise
9. growth_potential - Mutual growth and scalability potential
10. risk_profile - Risk factors and potential challenges

Guidelines:
- Select 4-6 most relevant dimensions based on the startup's needs
- Weights must sum to 1.0
- Provide clear rationale for each dimension and weight
- Consider exclusion criteria when planning strategy
- Be concise but thorough in your reasoning

Always respond in JSON format."""

    async def execute(
        self,
        startup_profile: StartupProfile,
        partner_requirements: Dict[str, Any],
        num_candidates: int,
    ) -> AgentResponse:
        """
        Generate an evaluation strategy based on startup profile and requirements.

        Args:
            startup_profile: Profile of the startup seeking partners
            partner_requirements: Specific partner requirements and preferences
            num_candidates: Total number of candidates to evaluate

        Returns:
            AgentResponse containing the proposed EvaluationStrategy
        """
        return self.propose_strategy(startup_profile, partner_requirements, num_candidates)

    def propose_strategy(
        self,
        startup_profile: StartupProfile,
        partner_requirements: Dict[str, Any],
        num_candidates: int,
    ) -> AgentResponse:
        """Generate an initial evaluation strategy proposal."""

        prompt = self._build_strategy_prompt(
            startup_profile, partner_requirements, num_candidates
        )

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        try:
            response, input_tokens, output_tokens = self._call_llm(messages)
            parsed = self._parse_json_response(response)

            if not parsed:
                return AgentResponse(
                    success=False,
                    data={},
                    message="Failed to parse strategy response",
                    tokens_used=input_tokens + output_tokens,
                )

            # Build the strategy from parsed response
            strategy = self._build_strategy_from_response(parsed, num_candidates)

            return AgentResponse(
                success=True,
                data={
                    "strategy": strategy.to_dict(),
                    "explanation": parsed.get("explanation", ""),
                    "recommended_focus": parsed.get("recommended_focus", []),
                },
                message=parsed.get("summary", "Strategy generated successfully"),
                reasoning=parsed.get("reasoning", ""),
                tokens_used=input_tokens + output_tokens,
            )

        except Exception as e:
            self.logger.error(f"Strategy generation failed: {e}")
            return AgentResponse(
                success=False,
                data={},
                message=f"Strategy generation failed: {str(e)}",
            )

    def modify_strategy(
        self,
        current_strategy: EvaluationStrategy,
        user_modification: str,
        startup_profile: StartupProfile,
    ) -> AgentResponse:
        """
        Modify an existing strategy based on user feedback.

        Args:
            current_strategy: The current evaluation strategy
            user_modification: User's modification request in natural language
            startup_profile: Context about the startup

        Returns:
            AgentResponse containing the modified strategy
        """
        prompt = f"""Current evaluation strategy:
{json.dumps(current_strategy.to_dict(), indent=2)}

User modification request: "{user_modification}"

Startup context:
- Name: {startup_profile.name}
- Industry: {startup_profile.industry}
- Partner needs: {startup_profile.partner_needs}

Please modify the strategy according to the user's request. Ensure:
1. Weights still sum to 1.0
2. The modification aligns with the startup's needs
3. Explain what changes were made and why

Respond in JSON format:
{{
    "dimensions": [
        {{"dimension": "dimension_name", "weight": 0.XX, "priority": N, "rationale": "..."}}
    ],
    "changes_made": ["list of changes"],
    "explanation": "explanation of modifications",
    "warnings": ["any concerns about the changes"]
}}"""

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        try:
            response, input_tokens, output_tokens = self._call_llm(messages)
            parsed = self._parse_json_response(response)

            if not parsed or "dimensions" not in parsed:
                return AgentResponse(
                    success=False,
                    data={"current_strategy": current_strategy.to_dict()},
                    message="Failed to parse modified strategy",
                    tokens_used=input_tokens + output_tokens,
                )

            # Build modified strategy
            modified_strategy = self._build_strategy_from_response(
                parsed, current_strategy.total_candidates
            )
            modified_strategy.user_modifications = (
                current_strategy.user_modifications + [user_modification]
            )
            modified_strategy.confirmed_by_user = False

            return AgentResponse(
                success=True,
                data={
                    "strategy": modified_strategy.to_dict(),
                    "changes_made": parsed.get("changes_made", []),
                    "warnings": parsed.get("warnings", []),
                },
                message=parsed.get("explanation", "Strategy modified successfully"),
                tokens_used=input_tokens + output_tokens,
            )

        except Exception as e:
            self.logger.error(f"Strategy modification failed: {e}")
            return AgentResponse(
                success=False,
                data={"current_strategy": current_strategy.to_dict()},
                message=f"Strategy modification failed: {str(e)}",
            )

    def _build_strategy_prompt(
        self,
        startup_profile: StartupProfile,
        partner_requirements: Dict[str, Any],
        num_candidates: int,
    ) -> str:
        """Build the prompt for strategy generation."""

        return f"""Analyze the following startup profile and partner requirements to propose an evaluation strategy.

STARTUP PROFILE:
- Name: {startup_profile.name}
- Industry: {startup_profile.industry}
- Stage: {startup_profile.stage}
- Tech Stack: {', '.join(startup_profile.tech_stack) if startup_profile.tech_stack else 'Not specified'}
- Team Size: {startup_profile.team_size or 'Not specified'}
- Location: {startup_profile.location or 'Not specified'}
- Description: {startup_profile.description}

PARTNER REQUIREMENTS:
- Partner Needs: {startup_profile.partner_needs}
- Preferred Geography: {', '.join(startup_profile.preferred_geography) if startup_profile.preferred_geography else 'No preference'}
- Exclusion Criteria: {', '.join(startup_profile.exclusion_criteria) if startup_profile.exclusion_criteria else 'None'}
- Additional Requirements: {json.dumps(partner_requirements) if partner_requirements else 'None'}

NUMBER OF CANDIDATES TO EVALUATE: {num_candidates}

Please propose an evaluation strategy with:
1. 4-6 most relevant evaluation dimensions
2. Appropriate weights (must sum to 1.0)
3. Priority ranking for each dimension
4. Rationale for each dimension selection

Respond in JSON format:
{{
    "dimensions": [
        {{
            "dimension": "dimension_name",
            "weight": 0.XX,
            "priority": 1,
            "rationale": "Why this dimension is important for this startup"
        }}
    ],
    "reasoning": "Overall reasoning for this strategy",
    "summary": "Brief summary of the proposed strategy",
    "recommended_focus": ["Key areas to focus on during evaluation"],
    "exclusion_criteria": ["List of exclusion criteria if any"],
    "explanation": "Detailed explanation for the user"
}}"""

    def _build_strategy_from_response(
        self, parsed: Dict[str, Any], num_candidates: int
    ) -> EvaluationStrategy:
        """Build an EvaluationStrategy from the parsed LLM response."""

        dimensions = []
        for dim_data in parsed.get("dimensions", []):
            try:
                dimension = EvaluationDimension(dim_data["dimension"])
                weight = float(dim_data["weight"])
                priority = int(dim_data.get("priority", len(dimensions) + 1))
                rationale = dim_data.get("rationale", "")

                dimensions.append(
                    DimensionWeight(
                        dimension=dimension,
                        weight=weight,
                        priority=priority,
                        rationale=rationale,
                    )
                )
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Skipping invalid dimension: {dim_data}, error: {e}")
                continue

        # Normalize weights if they don't sum to 1.0
        total_weight = sum(d.weight for d in dimensions)
        if total_weight > 0 and abs(total_weight - 1.0) > 0.01:
            self.logger.info(f"Normalizing weights from {total_weight} to 1.0")
            for d in dimensions:
                d.weight = d.weight / total_weight

        return EvaluationStrategy(
            dimensions=dimensions,
            total_candidates=num_candidates,
            top_k=min(5, num_candidates),
            exclusion_criteria=parsed.get("exclusion_criteria", []),
            inclusion_criteria=parsed.get("inclusion_criteria", []),
            confirmed_by_user=False,
        )

    def generate_strategy_summary(self, strategy: EvaluationStrategy) -> str:
        """Generate a human-readable summary of the strategy for user presentation."""

        lines = ["Based on your requirements, I propose the following evaluation strategy:\n"]

        # Sort dimensions by priority
        sorted_dims = sorted(strategy.dimensions, key=lambda x: x.priority)

        for dw in sorted_dims:
            percentage = int(dw.weight * 100)
            dim_name = dw.dimension.value.replace("_", " ").title()
            lines.append(f"• **{dim_name}** ({percentage}%)")
            if dw.rationale:
                lines.append(f"  _{dw.rationale}_")

        lines.append(f"\nThis strategy will evaluate {strategy.total_candidates} candidates ")
        lines.append(f"and return the top {strategy.top_k} recommendations.")

        if strategy.exclusion_criteria:
            lines.append(f"\nExclusion criteria: {', '.join(strategy.exclusion_criteria)}")

        lines.append("\nWould you like to adjust any of these weights or dimensions?")

        return "\n".join(lines)
