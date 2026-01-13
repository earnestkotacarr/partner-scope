"""
Specialized Agents for Multi-Dimensional Evaluation (Phase 2).

Each specialized agent is responsible for evaluating candidates
on a specific dimension, providing independent scoring and reasoning.
"""

import json
from abc import abstractmethod
from typing import Dict, List, Any, Optional

from .base import BaseAgent, AgentResponse
from ..models import (
    EvaluationDimension,
    DimensionScore,
    StartupProfile,
)


class SpecializedAgent(BaseAgent):
    """
    Base class for specialized evaluation agents.

    Each specialized agent:
    - Focuses on a single evaluation dimension
    - Retrieves and analyzes relevant candidate data
    - Produces independent scores and justifications
    """

    dimension: EvaluationDimension

    def __init__(
        self,
        dimension: EvaluationDimension,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
    ):
        super().__init__(
            name=f"specialized_{dimension.value}",
            model=model,
            temperature=temperature,
            max_tokens=4096,
        )
        self.dimension = dimension

    @abstractmethod
    def get_evaluation_criteria(self) -> List[str]:
        """Return the specific criteria this agent evaluates."""
        pass

    @abstractmethod
    def get_data_requirements(self) -> List[str]:
        """Return the data fields required for evaluation."""
        pass

    def get_system_prompt(self) -> str:
        dim_name = self.dimension.value.replace("_", " ").title()
        criteria = "\n".join(f"- {c}" for c in self.get_evaluation_criteria())
        data_reqs = ", ".join(self.get_data_requirements())

        return f"""You are a specialized evaluation agent focused on assessing {dim_name}.

Your evaluation criteria:
{criteria}

Required data points: {data_reqs}

Guidelines:
- Score candidates from 0 to 100 based on your specific dimension
- Provide confidence level (0.0 to 1.0) based on data availability
- List specific evidence supporting your score
- Be objective and consistent across all candidates
- Identify both strengths and weaknesses

Always respond in JSON format with detailed reasoning."""

    async def execute(
        self,
        startup_profile: StartupProfile,
        candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Evaluate all candidates on this agent's dimension.

        Args:
            startup_profile: Profile of the startup for context
            candidates: List of candidate data to evaluate
            context: Additional context for evaluation

        Returns:
            AgentResponse containing dimension scores for all candidates
        """
        return self.evaluate_candidates(startup_profile, candidates, context)

    def evaluate_candidates(
        self,
        startup_profile: StartupProfile,
        candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Evaluate all candidates and return dimension scores."""

        prompt = self._build_evaluation_prompt(startup_profile, candidates, context)

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        try:
            response, input_tokens, output_tokens = self._call_llm(messages)
            parsed = self._parse_json_response(response)

            if not parsed or "evaluations" not in parsed:
                return AgentResponse(
                    success=False,
                    data={},
                    message="Failed to parse evaluation response",
                    tokens_used=input_tokens + output_tokens,
                )

            # Build dimension scores
            dimension_scores = []
            for eval_data in parsed.get("evaluations", []):
                try:
                    score = DimensionScore(
                        dimension=self.dimension,
                        score=float(eval_data.get("score", 0)),
                        confidence=float(eval_data.get("confidence", 0.5)),
                        evidence=eval_data.get("evidence", []),
                        reasoning=eval_data.get("reasoning", ""),
                        data_sources=eval_data.get("data_sources", []),
                    )
                    dimension_scores.append({
                        "candidate_id": eval_data.get("candidate_id", ""),
                        "candidate_name": eval_data.get("candidate_name", ""),
                        "score": score,
                    })
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Skipping invalid evaluation: {eval_data}, error: {e}")

            return AgentResponse(
                success=True,
                data={
                    "dimension": self.dimension.value,
                    "scores": dimension_scores,
                    "summary": parsed.get("summary", ""),
                    "top_performers": parsed.get("top_performers", []),
                },
                message=f"Evaluated {len(dimension_scores)} candidates on {self.dimension.value}",
                reasoning=parsed.get("overall_reasoning", ""),
                tokens_used=input_tokens + output_tokens,
            )

        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            return AgentResponse(
                success=False,
                data={},
                message=f"Evaluation failed: {str(e)}",
            )

    def _build_evaluation_prompt(
        self,
        startup_profile: StartupProfile,
        candidates: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build the evaluation prompt for this dimension."""

        dim_name = self.dimension.value.replace("_", " ").title()

        # Format candidates
        candidates_text = []
        for i, candidate in enumerate(candidates):
            candidate_id = candidate.get("id", f"candidate_{i}")
            candidate_name = candidate.get("name", candidate.get("company_name", f"Candidate {i}"))
            candidates_text.append(f"""
Candidate {i + 1}:
- ID: {candidate_id}
- Name: {candidate_name}
- Data: {json.dumps(candidate, indent=2)}
""")

        return f"""Evaluate the following candidates on {dim_name} for this startup:

STARTUP CONTEXT:
- Name: {startup_profile.name}
- Industry: {startup_profile.industry}
- Stage: {startup_profile.stage}
- Partner Needs: {startup_profile.partner_needs}
- Description: {startup_profile.description}

CANDIDATES TO EVALUATE:
{''.join(candidates_text)}

{f'ADDITIONAL CONTEXT: {json.dumps(context)}' if context else ''}

For each candidate, provide:
1. Score (0-100) on {dim_name}
2. Confidence level (0.0-1.0) based on data availability
3. Evidence supporting the score
4. Brief reasoning

Respond in JSON format:
{{
    "evaluations": [
        {{
            "candidate_id": "...",
            "candidate_name": "...",
            "score": 85,
            "confidence": 0.8,
            "evidence": ["specific evidence 1", "specific evidence 2"],
            "reasoning": "Why this score was given",
            "data_sources": ["source1", "source2"]
        }}
    ],
    "summary": "Brief summary of evaluation results",
    "top_performers": ["names of top 3 performers on this dimension"],
    "overall_reasoning": "Overall observations about candidates on this dimension"
}}"""


# Concrete implementations for each evaluation dimension

class MarketCompatibilityAgent(SpecializedAgent):
    """Agent for evaluating market compatibility."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.MARKET_COMPATIBILITY, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Target market overlap and synergy",
            "Customer segment alignment",
            "Market positioning compatibility",
            "Competitive landscape fit",
            "Go-to-market strategy alignment",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["industry", "target_market", "customer_segments", "products", "market_position"]


class FinancialHealthAgent(SpecializedAgent):
    """Agent for evaluating financial health."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.FINANCIAL_HEALTH, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Revenue and growth trajectory",
            "Funding status and runway",
            "Profitability indicators",
            "Financial stability",
            "Investment capacity for partnerships",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["revenue", "funding_total", "funding_rounds", "employees", "growth_rate"]


class TechnicalSynergyAgent(SpecializedAgent):
    """Agent for evaluating technical synergy."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.TECHNICAL_SYNERGY, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Technology stack compatibility",
            "API and integration capabilities",
            "Technical innovation potential",
            "Data compatibility and sharing",
            "Technical team expertise alignment",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["tech_stack", "products", "technical_capabilities", "api_availability"]


class OperationalCapacityAgent(SpecializedAgent):
    """Agent for evaluating operational capacity."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.OPERATIONAL_CAPACITY, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Supply chain capabilities",
            "Manufacturing or service delivery capacity",
            "Logistics and distribution network",
            "Operational scalability",
            "Quality control processes",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["operations", "supply_chain", "manufacturing", "logistics", "scale"]


class GeographicCoverageAgent(SpecializedAgent):
    """Agent for evaluating geographic coverage."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.GEOGRAPHIC_COVERAGE, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Regional presence and offices",
            "Distribution network coverage",
            "Local market expertise",
            "Regulatory knowledge by region",
            "Geographic expansion potential",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["headquarters", "offices", "regions", "markets", "distribution"]


class StrategicAlignmentAgent(SpecializedAgent):
    """Agent for evaluating strategic alignment."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.STRATEGIC_ALIGNMENT, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Business vision alignment",
            "Long-term goal compatibility",
            "Partnership value proposition",
            "Strategic priority match",
            "Mutual benefit potential",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["mission", "vision", "strategy", "goals", "partnerships"]


class CulturalFitAgent(SpecializedAgent):
    """Agent for evaluating cultural fit."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.CULTURAL_FIT, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Organizational culture compatibility",
            "Communication style alignment",
            "Decision-making process fit",
            "Values and ethics alignment",
            "Collaboration history and style",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["culture", "values", "team_size", "leadership", "work_style"]


class ResourceComplementarityAgent(SpecializedAgent):
    """Agent for evaluating resource complementarity."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.RESOURCE_COMPLEMENTARITY, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Complementary capabilities",
            "Resource gaps that can be filled",
            "Expertise sharing potential",
            "Asset and IP complementarity",
            "Network and relationship access",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["capabilities", "resources", "expertise", "assets", "networks"]


class GrowthPotentialAgent(SpecializedAgent):
    """Agent for evaluating growth potential."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.GROWTH_POTENTIAL, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Market expansion opportunities",
            "Revenue growth potential from partnership",
            "Scalability of collaboration",
            "Innovation and product development synergy",
            "Long-term partnership value",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["growth_rate", "market_size", "expansion_plans", "innovation", "scalability"]


class RiskProfileAgent(SpecializedAgent):
    """Agent for evaluating risk profile."""

    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(EvaluationDimension.RISK_PROFILE, model)

    def get_evaluation_criteria(self) -> List[str]:
        return [
            "Financial risk indicators",
            "Operational risks",
            "Reputational considerations",
            "Dependency risks",
            "Regulatory and compliance risks",
        ]

    def get_data_requirements(self) -> List[str]:
        return ["risk_factors", "compliance", "reputation", "dependencies", "legal"]


# Factory function to create specialized agents
def create_specialized_agent(
    dimension: EvaluationDimension, model: str = "gpt-4o-mini"
) -> SpecializedAgent:
    """Factory function to create the appropriate specialized agent for a dimension."""

    agent_classes = {
        EvaluationDimension.MARKET_COMPATIBILITY: MarketCompatibilityAgent,
        EvaluationDimension.FINANCIAL_HEALTH: FinancialHealthAgent,
        EvaluationDimension.TECHNICAL_SYNERGY: TechnicalSynergyAgent,
        EvaluationDimension.OPERATIONAL_CAPACITY: OperationalCapacityAgent,
        EvaluationDimension.GEOGRAPHIC_COVERAGE: GeographicCoverageAgent,
        EvaluationDimension.STRATEGIC_ALIGNMENT: StrategicAlignmentAgent,
        EvaluationDimension.CULTURAL_FIT: CulturalFitAgent,
        EvaluationDimension.RESOURCE_COMPLEMENTARITY: ResourceComplementarityAgent,
        EvaluationDimension.GROWTH_POTENTIAL: GrowthPotentialAgent,
        EvaluationDimension.RISK_PROFILE: RiskProfileAgent,
    }

    agent_class = agent_classes.get(dimension)
    if not agent_class:
        raise ValueError(f"Unknown evaluation dimension: {dimension}")

    return agent_class(model=model)