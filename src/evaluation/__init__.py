"""
Partner Evaluation Framework

A multi-agent evaluation system based on PartnerMAS (Li et al., 2025).

This framework provides:
- Phase 1: Strategy Formulation (Planner Agent)
- Phase 2: Multi-Dimensional Evaluation (Specialized Agents)
- Phase 3: Aggregation & Iterative Refinement (Supervisor Agent)

Usage:
    from src.evaluation import EvaluationOrchestrator

    orchestrator = EvaluationOrchestrator()
    result = await orchestrator.evaluate(startup_profile, partner_requirements, candidates)
"""

from .models import (
    EvaluationDimension,
    DimensionWeight,
    EvaluationStrategy,
    DimensionScore,
    CandidateEvaluation,
    EvaluationResult,
    RefinementRequest,
)
from .orchestrator import EvaluationOrchestrator

__all__ = [
    "EvaluationDimension",
    "DimensionWeight",
    "EvaluationStrategy",
    "DimensionScore",
    "CandidateEvaluation",
    "EvaluationResult",
    "RefinementRequest",
    "EvaluationOrchestrator",
]
