"""
API Router for the Evaluation Framework.

Provides REST endpoints for:
- Strategy formulation and modification
- Evaluation execution
- Result refinement

This router is designed to be mounted on the main FastAPI application.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from .orchestrator import EvaluationOrchestrator
from .models import (
    EvaluationDimension,
    RefinementRequest,
    StartupProfile,
)


# Pydantic models for API requests/responses

class StartupProfileRequest(BaseModel):
    """Request model for startup profile."""
    name: str
    industry: str
    stage: str
    tech_stack: List[str] = []
    team_size: Optional[int] = None
    location: str = ""
    description: str = ""
    partner_needs: str = ""
    preferred_geography: List[str] = []
    exclusion_criteria: List[str] = []


class CreateSessionRequest(BaseModel):
    """Request to create a new evaluation session."""
    startup_profile: StartupProfileRequest
    candidates: List[Dict[str, Any]]
    session_id: Optional[str] = None


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    success: bool
    session_id: str
    message: str
    candidates_count: int


class ProposeStrategyRequest(BaseModel):
    """Request to propose an evaluation strategy."""
    session_id: str
    partner_requirements: Optional[Dict[str, Any]] = None


class StrategyResponse(BaseModel):
    """Response containing strategy information."""
    success: bool
    strategy: Optional[Dict[str, Any]] = None
    summary: str = ""
    explanation: str = ""
    recommended_focus: List[str] = []
    message: str = ""


class ModifyStrategyRequest(BaseModel):
    """Request to modify the current strategy."""
    session_id: str
    modification: str = Field(..., description="Natural language modification request")


class ConfirmStrategyRequest(BaseModel):
    """Request to confirm the strategy."""
    session_id: str


class RunEvaluationRequest(BaseModel):
    """Request to run evaluation."""
    session_id: str
    context: Optional[Dict[str, Any]] = None


class EvaluationResponse(BaseModel):
    """Response containing evaluation results."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    insights: List[str] = []
    conflicts: List[Dict[str, Any]] = []
    token_usage: Dict[str, int] = {}
    message: str = ""


class RefineResultsRequest(BaseModel):
    """Request to refine results."""
    session_id: str
    action: str = Field(..., description="Action type: exclude, adjust_weight, focus, rerank")
    parameters: Dict[str, Any]
    reason: str = ""


class ExcludeCandidateRequest(BaseModel):
    """Request to exclude a candidate."""
    session_id: str
    candidate_id: str
    reason: str = ""


class AdjustWeightRequest(BaseModel):
    """Request to adjust dimension weight."""
    session_id: str
    dimension: str
    new_weight: float = Field(..., ge=0.0, le=1.0)
    reason: str = ""


class SessionStatusResponse(BaseModel):
    """Response with session status."""
    success: bool
    session_id: str = ""
    phase: str = ""
    has_strategy: bool = False
    strategy_confirmed: bool = False
    has_result: bool = False
    candidates_count: int = 0
    token_usage: Dict[str, int] = {}
    created_at: str = ""
    message: str = ""


# Create router
router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

# Global orchestrator instance
_orchestrator: Optional[EvaluationOrchestrator] = None


def get_orchestrator() -> EvaluationOrchestrator:
    """Get or create the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EvaluationOrchestrator()
    return _orchestrator


# API Endpoints

@router.post("/session", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new evaluation session.

    This is the first step in the evaluation process.
    """
    orchestrator = get_orchestrator()

    session_id = request.session_id or str(uuid.uuid4())

    # Convert request to StartupProfile
    startup_profile = StartupProfile(
        name=request.startup_profile.name,
        industry=request.startup_profile.industry,
        stage=request.startup_profile.stage,
        tech_stack=request.startup_profile.tech_stack,
        team_size=request.startup_profile.team_size,
        location=request.startup_profile.location,
        description=request.startup_profile.description,
        partner_needs=request.startup_profile.partner_needs,
        preferred_geography=request.startup_profile.preferred_geography,
        exclusion_criteria=request.startup_profile.exclusion_criteria,
    )

    await orchestrator.create_session(
        session_id=session_id,
        startup_profile=startup_profile,
        candidates=request.candidates,
    )

    return CreateSessionResponse(
        success=True,
        session_id=session_id,
        message="Session created successfully",
        candidates_count=len(request.candidates),
    )


@router.post("/strategy/propose", response_model=StrategyResponse)
async def propose_strategy(request: ProposeStrategyRequest):
    """
    Generate an evaluation strategy proposal.

    Phase 1 of the evaluation framework.
    Returns a strategy with recommended dimensions and weights.
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.propose_strategy(
            session_id=request.session_id,
            partner_requirements=request.partner_requirements,
        )

        return StrategyResponse(
            success=result.get("success", False),
            strategy=result.get("strategy"),
            summary=result.get("summary", ""),
            explanation=result.get("explanation", ""),
            recommended_focus=result.get("recommended_focus", []),
            message=result.get("message", ""),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/strategy/modify", response_model=StrategyResponse)
async def modify_strategy(request: ModifyStrategyRequest):
    """
    Modify the current strategy based on user feedback.

    Example modifications:
    - "Lower the weight of Geographic Coverage to 10%"
    - "Focus more on technical synergy"
    - "Remove cultural fit from the evaluation"
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.modify_strategy(
            session_id=request.session_id,
            modification=request.modification,
        )

        return StrategyResponse(
            success=result.get("success", False),
            strategy=result.get("strategy"),
            summary=result.get("summary", ""),
            message=result.get("message", ""),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/strategy/confirm")
async def confirm_strategy(request: ConfirmStrategyRequest):
    """
    Confirm the current strategy and prepare for evaluation.

    Must be called before running the evaluation.
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.confirm_strategy(request.session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/run", response_model=EvaluationResponse)
async def run_evaluation(request: RunEvaluationRequest):
    """
    Run the full multi-dimensional evaluation.

    Phases 2 and 3 of the evaluation framework.
    Requires the strategy to be confirmed first.
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.run_evaluation(
            session_id=request.session_id,
            context=request.context,
        )

        return EvaluationResponse(
            success=result.get("success", False),
            result=result.get("result"),
            insights=result.get("insights", []),
            conflicts=result.get("conflicts", []),
            token_usage=result.get("token_usage", {}),
            message=result.get("message", ""),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refine")
async def refine_results(request: RefineResultsRequest):
    """
    Refine evaluation results based on user feedback.

    Supports actions:
    - exclude: Remove a candidate
    - adjust_weight: Change dimension weight
    - focus: Focus more on a specific dimension
    - rerank: Request re-ranking with new criteria
    """
    orchestrator = get_orchestrator()

    try:
        refinement = RefinementRequest(
            action=request.action,
            parameters=request.parameters,
            reason=request.reason,
        )

        result = await orchestrator.refine_results(
            session_id=request.session_id,
            refinement=refinement,
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/exclude")
async def exclude_candidate(request: ExcludeCandidateRequest):
    """
    Exclude a specific candidate from results.

    Shortcut for refine with action="exclude".
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.exclude_candidate(
            session_id=request.session_id,
            candidate_id=request.candidate_id,
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/adjust-weight")
async def adjust_weight(request: AdjustWeightRequest):
    """
    Adjust the weight of a dimension and re-rank results.
    """
    orchestrator = get_orchestrator()

    try:
        dimension = EvaluationDimension(request.dimension)
        result = await orchestrator.adjust_dimension_weight(
            session_id=request.session_id,
            dimension=dimension,
            new_weight=request.new_weight,
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Get the current status of an evaluation session.
    """
    orchestrator = get_orchestrator()
    result = orchestrator.get_session_status(session_id)

    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Session not found"))

    return SessionStatusResponse(**result)


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete an evaluation session.
    """
    orchestrator = get_orchestrator()

    if orchestrator.delete_session(session_id):
        return {"success": True, "message": "Session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/dimensions")
async def get_available_dimensions():
    """
    Get list of all available evaluation dimensions.
    """
    return {
        "dimensions": [
            {
                "id": dim.value,
                "name": dim.value.replace("_", " ").title(),
                "description": EvaluationDimension.get_description(dim),
            }
            for dim in EvaluationDimension
        ]
    }
