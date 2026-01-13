"""
Supervisor Agent for Aggregation & Iterative Refinement (Phase 3).

The Supervisor Agent:
1. Aggregates outputs from all specialized agents
2. Resolves conflicts between dimension scores
3. Generates final global ranking
4. Handles user refinement requests
"""

import json
from typing import Dict, List, Any, Optional

from .base import BaseAgent, AgentResponse
from ..models import (
    EvaluationDimension,
    EvaluationStrategy,
    DimensionScore,
    CandidateEvaluation,
    EvaluationResult,
    RefinementRequest,
    StartupProfile,
)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent for aggregation and refinement.

    Responsibilities:
    - Aggregate scores from all specialized agents
    - Apply user-confirmed weights
    - Resolve conflicts between dimensions
    - Generate final rankings
    - Handle iterative refinement requests
    """

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        super().__init__(
            name="supervisor",
            model=model,
            temperature=temperature,
            max_tokens=8192,
        )

    def get_system_prompt(self) -> str:
        return """You are a supervisor agent responsible for aggregating partner evaluation results.

Your responsibilities:
1. Combine scores from multiple evaluation dimensions
2. Apply weighted scoring based on the evaluation strategy
3. Identify and resolve conflicts between dimensions
4. Generate insightful final rankings
5. Handle user refinement requests

Guidelines:
- Be objective and transparent in your aggregation logic
- Explain any conflicts or trade-offs clearly
- Provide actionable recommendations
- Support iterative refinement without full re-evaluation

Always respond in JSON format with detailed reasoning."""

    async def execute(
        self,
        strategy: EvaluationStrategy,
        dimension_results: Dict[EvaluationDimension, List[Dict[str, Any]]],
        candidates: List[Dict[str, Any]],
        startup_profile: StartupProfile,
    ) -> AgentResponse:
        """
        Aggregate dimension scores and generate final rankings.

        Args:
            strategy: The confirmed evaluation strategy with weights
            dimension_results: Scores from each specialized agent
            candidates: Original candidate data
            startup_profile: Startup context

        Returns:
            AgentResponse containing the final EvaluationResult
        """
        return self.aggregate_and_rank(
            strategy, dimension_results, candidates, startup_profile
        )

    def aggregate_and_rank(
        self,
        strategy: EvaluationStrategy,
        dimension_results: Dict[EvaluationDimension, List[Dict[str, Any]]],
        candidates: List[Dict[str, Any]],
        startup_profile: StartupProfile,
    ) -> AgentResponse:
        """Aggregate scores and generate final ranking."""

        # First, compute weighted scores
        candidate_scores = self._compute_weighted_scores(strategy, dimension_results, candidates)

        # Use LLM to generate insights and resolve conflicts
        prompt = self._build_aggregation_prompt(
            strategy, dimension_results, candidate_scores, startup_profile
        )

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        try:
            response, input_tokens, output_tokens = self._call_llm(messages)
            parsed = self._parse_json_response(response)

            if not parsed:
                # Fall back to basic aggregation
                return self._create_basic_result(strategy, candidate_scores, input_tokens + output_tokens)

            # Build final evaluation result
            result = self._build_evaluation_result(
                strategy, dimension_results, candidate_scores, parsed
            )

            return AgentResponse(
                success=True,
                data={
                    "result": result.to_dict(),
                    "conflicts": parsed.get("conflicts_resolved", []),
                    "insights": parsed.get("insights", []),
                },
                message=parsed.get("summary", "Evaluation completed successfully"),
                reasoning=parsed.get("reasoning", ""),
                tokens_used=input_tokens + output_tokens,
            )

        except Exception as e:
            self.logger.error(f"Aggregation failed: {e}")
            return AgentResponse(
                success=False,
                data={},
                message=f"Aggregation failed: {str(e)}",
            )

    def refine_results(
        self,
        current_result: EvaluationResult,
        refinement: RefinementRequest,
        startup_profile: StartupProfile,
    ) -> AgentResponse:
        """
        Refine evaluation results based on user feedback.

        Args:
            current_result: The current evaluation result
            refinement: User's refinement request
            startup_profile: Startup context

        Returns:
            AgentResponse containing the refined result
        """
        prompt = self._build_refinement_prompt(current_result, refinement, startup_profile)

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
                    data={"current_result": current_result.to_dict()},
                    message="Failed to parse refinement response",
                    tokens_used=input_tokens + output_tokens,
                )

            # Apply refinement to result
            refined_result = self._apply_refinement(current_result, refinement, parsed)

            return AgentResponse(
                success=True,
                data={
                    "result": refined_result.to_dict(),
                    "changes_applied": parsed.get("changes_applied", []),
                    "new_rankings": parsed.get("new_rankings", []),
                },
                message=parsed.get("explanation", "Results refined successfully"),
                tokens_used=input_tokens + output_tokens,
            )

        except Exception as e:
            self.logger.error(f"Refinement failed: {e}")
            return AgentResponse(
                success=False,
                data={"current_result": current_result.to_dict()},
                message=f"Refinement failed: {str(e)}",
            )

    def _compute_weighted_scores(
        self,
        strategy: EvaluationStrategy,
        dimension_results: Dict[EvaluationDimension, List[Dict[str, Any]]],
        candidates: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Compute weighted scores for each candidate."""

        candidate_scores = {}

        # Create a lookup for candidate data
        candidate_lookup = {}
        for c in candidates:
            cid = c.get("id", c.get("company_name", str(id(c))))
            candidate_lookup[cid] = c

        # Process each dimension's results
        for dimension, results in dimension_results.items():
            weight = strategy.get_dimension_weight(dimension)

            for result in results:
                cid = result.get("candidate_id", "")
                cname = result.get("candidate_name", "")
                score_obj = result.get("score")

                if not cid and cname:
                    # Try to match by name
                    for c in candidates:
                        if c.get("company_name", c.get("name", "")) == cname:
                            cid = c.get("id", cname)
                            break

                if cid not in candidate_scores:
                    candidate_scores[cid] = {
                        "candidate_id": cid,
                        "candidate_name": cname,
                        "candidate_info": candidate_lookup.get(cid, {}),
                        "dimension_scores": [],
                        "weighted_sum": 0.0,
                        "total_weight": 0.0,
                    }

                if score_obj:
                    # Extract score data
                    if isinstance(score_obj, DimensionScore):
                        dim_score = score_obj
                    else:
                        dim_score = DimensionScore(
                            dimension=dimension,
                            score=float(score_obj.get("score", 0) if isinstance(score_obj, dict) else score_obj),
                            confidence=float(score_obj.get("confidence", 0.7) if isinstance(score_obj, dict) else 0.7),
                            evidence=score_obj.get("evidence", []) if isinstance(score_obj, dict) else [],
                            reasoning=score_obj.get("reasoning", "") if isinstance(score_obj, dict) else "",
                        )

                    candidate_scores[cid]["dimension_scores"].append(dim_score)
                    weighted_score = dim_score.score * weight * dim_score.confidence
                    candidate_scores[cid]["weighted_sum"] += weighted_score
                    candidate_scores[cid]["total_weight"] += weight * dim_score.confidence

        # Compute final scores
        for cid, data in candidate_scores.items():
            if data["total_weight"] > 0:
                data["final_score"] = data["weighted_sum"] / data["total_weight"]
            else:
                data["final_score"] = 0.0

        # Assign ranks
        sorted_candidates = sorted(
            candidate_scores.values(), key=lambda x: x["final_score"], reverse=True
        )
        for rank, c in enumerate(sorted_candidates, 1):
            candidate_scores[c["candidate_id"]]["rank"] = rank

        return candidate_scores

    def _build_aggregation_prompt(
        self,
        strategy: EvaluationStrategy,
        dimension_results: Dict[EvaluationDimension, List[Dict[str, Any]]],
        candidate_scores: Dict[str, Dict[str, Any]],
        startup_profile: StartupProfile,
    ) -> str:
        """Build the prompt for LLM aggregation and insights."""

        # Format candidate scores
        scores_text = []
        sorted_candidates = sorted(
            candidate_scores.values(), key=lambda x: x.get("final_score", 0), reverse=True
        )

        for c in sorted_candidates[:10]:  # Top 10 for analysis
            dim_details = []
            for ds in c.get("dimension_scores", []):
                dim_name = ds.dimension.value.replace("_", " ").title()
                dim_details.append(f"    - {dim_name}: {ds.score:.1f} (confidence: {ds.confidence:.2f})")

            scores_text.append(f"""
Candidate: {c['candidate_name']} (ID: {c['candidate_id']})
  Final Score: {c.get('final_score', 0):.1f}
  Dimension Scores:
{chr(10).join(dim_details)}
""")

        return f"""Analyze the following aggregated evaluation results and provide insights.

STARTUP CONTEXT:
- Name: {startup_profile.name}
- Industry: {startup_profile.industry}
- Partner Needs: {startup_profile.partner_needs}

EVALUATION STRATEGY:
{json.dumps(strategy.to_dict(), indent=2)}

CANDIDATE SCORES (Top 10):
{''.join(scores_text)}

Please analyze these results and provide:
1. Summary of top candidates and why they rank highly
2. Any conflicts between dimensions (e.g., high financial score but low cultural fit)
3. Key insights about the candidate pool
4. Specific strengths and weaknesses for top 5 candidates
5. Recommendations for each top candidate

Respond in JSON format:
{{
    "summary": "Overall summary of evaluation results",
    "top_candidates_analysis": [
        {{
            "candidate_id": "...",
            "candidate_name": "...",
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1"],
            "recommendations": ["recommendation1"],
            "flags": ["any warnings or special notes"]
        }}
    ],
    "conflicts_resolved": [
        {{
            "candidate": "...",
            "conflict": "description of conflict",
            "resolution": "how it was resolved"
        }}
    ],
    "insights": ["insight1", "insight2"],
    "reasoning": "Overall reasoning for the ranking"
}}"""

    def _build_refinement_prompt(
        self,
        current_result: EvaluationResult,
        refinement: RefinementRequest,
        startup_profile: StartupProfile,
    ) -> str:
        """Build the prompt for refinement."""

        return f"""Current evaluation results need to be refined based on user feedback.

CURRENT TOP CANDIDATES:
{json.dumps([e.to_dict() for e in current_result.top_candidates], indent=2)}

USER REFINEMENT REQUEST:
- Action: {refinement.action}
- Parameters: {json.dumps(refinement.parameters)}
- Reason: {refinement.reason}

STARTUP CONTEXT:
- Name: {startup_profile.name}
- Partner Needs: {startup_profile.partner_needs}

Please process this refinement and provide:
1. How the rankings should change
2. Which candidates are affected
3. New top 5 ranking after refinement

Respond in JSON format:
{{
    "changes_applied": ["list of changes made"],
    "new_rankings": [
        {{
            "candidate_id": "...",
            "candidate_name": "...",
            "new_rank": 1,
            "previous_rank": 2,
            "score_adjustment": 0,
            "reason": "why this change"
        }}
    ],
    "excluded_candidates": ["list of excluded candidate IDs"],
    "explanation": "Explanation of refinement results"
}}"""

    def _build_evaluation_result(
        self,
        strategy: EvaluationStrategy,
        dimension_results: Dict[EvaluationDimension, List[Dict[str, Any]]],
        candidate_scores: Dict[str, Dict[str, Any]],
        llm_analysis: Dict[str, Any],
    ) -> EvaluationResult:
        """Build the final EvaluationResult object."""

        # Create CandidateEvaluation objects
        evaluations = []
        analysis_lookup = {
            a["candidate_id"]: a
            for a in llm_analysis.get("top_candidates_analysis", [])
        }

        sorted_candidates = sorted(
            candidate_scores.values(), key=lambda x: x.get("final_score", 0), reverse=True
        )

        for c in sorted_candidates:
            analysis = analysis_lookup.get(c["candidate_id"], {})

            evaluation = CandidateEvaluation(
                candidate_id=c["candidate_id"],
                candidate_name=c["candidate_name"],
                candidate_info=c.get("candidate_info", {}),
                dimension_scores=c.get("dimension_scores", []),
                final_score=c.get("final_score", 0),
                rank=c.get("rank", 0),
                strengths=analysis.get("strengths", []),
                weaknesses=analysis.get("weaknesses", []),
                recommendations=analysis.get("recommendations", []),
                flags=analysis.get("flags", []),
            )
            evaluations.append(evaluation)

        # Get top k candidates
        top_candidates = evaluations[: strategy.top_k]

        return EvaluationResult(
            strategy=strategy,
            evaluations=evaluations,
            total_evaluated=len(evaluations),
            top_candidates=top_candidates,
            summary=llm_analysis.get("summary", ""),
            insights=llm_analysis.get("insights", []),
            conflicts_resolved=llm_analysis.get("conflicts_resolved", []),
            evaluation_metadata={
                "reasoning": llm_analysis.get("reasoning", ""),
            },
        )

    def _apply_refinement(
        self,
        current_result: EvaluationResult,
        refinement: RefinementRequest,
        llm_response: Dict[str, Any],
    ) -> EvaluationResult:
        """Apply refinement to the current result."""

        # Create a copy of evaluations to modify
        evaluations = list(current_result.evaluations)

        # Handle exclusion
        if refinement.action == "exclude":
            excluded_ids = set(llm_response.get("excluded_candidates", []))
            excluded_ids.add(refinement.parameters.get("candidate_id", ""))
            evaluations = [e for e in evaluations if e.candidate_id not in excluded_ids]

        # Apply new rankings from LLM
        new_rankings = llm_response.get("new_rankings", [])
        rank_lookup = {r["candidate_id"]: r for r in new_rankings}

        for evaluation in evaluations:
            if evaluation.candidate_id in rank_lookup:
                rank_info = rank_lookup[evaluation.candidate_id]
                evaluation.rank = rank_info.get("new_rank", evaluation.rank)
                # Apply score adjustment if provided
                adjustment = rank_info.get("score_adjustment", 0)
                evaluation.final_score = max(0, min(100, evaluation.final_score + adjustment))

        # Re-sort by new ranks
        evaluations.sort(key=lambda x: x.rank)

        # Update ranks to be consecutive
        for i, e in enumerate(evaluations, 1):
            e.rank = i

        # Get new top candidates
        top_candidates = evaluations[: current_result.strategy.top_k]

        return EvaluationResult(
            strategy=current_result.strategy,
            evaluations=evaluations,
            total_evaluated=len(evaluations),
            top_candidates=top_candidates,
            summary=llm_response.get("explanation", current_result.summary),
            insights=current_result.insights + llm_response.get("changes_applied", []),
            conflicts_resolved=current_result.conflicts_resolved,
            evaluation_metadata={
                **current_result.evaluation_metadata,
                "refinement_applied": refinement.action,
            },
        )

    def _create_basic_result(
        self,
        strategy: EvaluationStrategy,
        candidate_scores: Dict[str, Dict[str, Any]],
        tokens_used: int,
    ) -> AgentResponse:
        """Create a basic result without LLM insights (fallback)."""

        evaluations = []
        sorted_candidates = sorted(
            candidate_scores.values(), key=lambda x: x.get("final_score", 0), reverse=True
        )

        for c in sorted_candidates:
            evaluation = CandidateEvaluation(
                candidate_id=c["candidate_id"],
                candidate_name=c["candidate_name"],
                candidate_info=c.get("candidate_info", {}),
                dimension_scores=c.get("dimension_scores", []),
                final_score=c.get("final_score", 0),
                rank=c.get("rank", 0),
            )
            evaluations.append(evaluation)

        result = EvaluationResult(
            strategy=strategy,
            evaluations=evaluations,
            total_evaluated=len(evaluations),
            top_candidates=evaluations[: strategy.top_k],
            summary="Evaluation completed with basic aggregation",
        )

        return AgentResponse(
            success=True,
            data={"result": result.to_dict()},
            message="Evaluation completed (basic mode)",
            tokens_used=tokens_used,
        )
