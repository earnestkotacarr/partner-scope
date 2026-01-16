"""
Evaluation Orchestrator

Coordinates the multi-agent evaluation process:
1. Invokes Planner Agent for strategy formulation
2. Spawns Specialized Agents for each dimension
3. Uses Supervisor Agent for aggregation and refinement

This is the main entry point for the evaluation framework.

Debug Mode:
    Set DEBUG_MODE=1 environment variable or use DebugConfig.enable()
    to run with fake data without API calls.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .models import (
    EvaluationDimension,
    EvaluationStrategy,
    EvaluationResult,
    RefinementRequest,
    StartupProfile,
)
from .agents.planner import PlannerAgent
from .agents.specialized import create_specialized_agent
from .agents.supervisor import SupervisorAgent
from ..debug import DebugConfig, FakeDataGenerator


@dataclass
class EvaluationSession:
    """Tracks the state of an evaluation session."""

    session_id: str
    startup_profile: StartupProfile
    candidates: List[Dict[str, Any]]
    strategy: Optional[EvaluationStrategy] = None
    result: Optional[EvaluationResult] = None
    phase: str = "init"  # init, planning, evaluating, complete
    created_at: datetime = field(default_factory=datetime.now)
    token_usage: Dict[str, int] = field(default_factory=dict)


class EvaluationOrchestrator:
    """
    Main orchestrator for the partner evaluation framework.

    Manages the evaluation lifecycle:
    1. Strategy formulation with user alignment
    2. Multi-dimensional evaluation
    3. Aggregation and iterative refinement

    Debug Mode:
        When debug mode is enabled, the orchestrator will use fake data
        instead of making actual API calls. This is useful for testing
        the UI and workflow without incurring API costs.

        Enable debug mode:
            - Set DEBUG_MODE=1 environment variable
            - Or call DebugConfig.enable() before creating the orchestrator
    """

    def __init__(self, model: str = "gpt-4.1", debug_mode: Optional[bool] = None):
        """
        Initialize the evaluation orchestrator.

        Args:
            model: LLM model to use for agents
            debug_mode: Override debug mode setting (None = use global DebugConfig)
        """
        self.model = model
        self.logger = logging.getLogger("evaluation.orchestrator")

        # Debug mode configuration
        if debug_mode is not None:
            if debug_mode:
                DebugConfig.enable()
            else:
                DebugConfig.disable()

        self._debug_mode = DebugConfig.is_enabled()
        self._fake_data_generator = FakeDataGenerator() if self._debug_mode else None

        if self._debug_mode:
            self.logger.info("EvaluationOrchestrator initialized in DEBUG MODE")

        # Initialize agents
        self.planner = PlannerAgent(model=model)
        self.supervisor = SupervisorAgent(model=model)

        # Active sessions
        self.sessions: Dict[str, EvaluationSession] = {}

    async def create_session(
        self,
        session_id: str,
        startup_profile: StartupProfile,
        candidates: List[Dict[str, Any]],
    ) -> EvaluationSession:
        """
        Create a new evaluation session.

        Args:
            session_id: Unique identifier for the session
            startup_profile: Startup profile for context
            candidates: List of candidates to evaluate

        Returns:
            New EvaluationSession
        """
        session = EvaluationSession(
            session_id=session_id,
            startup_profile=startup_profile,
            candidates=candidates,
        )
        self.sessions[session_id] = session
        self.logger.info(f"Created evaluation session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[EvaluationSession]:
        """Get an existing session by ID."""
        return self.sessions.get(session_id)

    # Phase 1: Strategy Formulation

    async def propose_strategy(
        self,
        session_id: str,
        partner_requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an evaluation strategy proposal.

        Args:
            session_id: Session identifier
            partner_requirements: Additional partner requirements

        Returns:
            Strategy proposal with explanation
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.phase = "planning"

        response = self.planner.propose_strategy(
            startup_profile=session.startup_profile,
            partner_requirements=partner_requirements or {},
            num_candidates=len(session.candidates),
        )

        if response.success:
            # Store the proposed strategy
            strategy_data = response.data.get("strategy", {})
            session.strategy = EvaluationStrategy.from_dict(strategy_data)

            # Update token usage
            session.token_usage["planner"] = session.token_usage.get("planner", 0) + response.tokens_used

            return {
                "success": True,
                "strategy": strategy_data,
                "explanation": response.data.get("explanation", ""),
                "summary": self.planner.generate_strategy_summary(session.strategy),
                "recommended_focus": response.data.get("recommended_focus", []),
            }
        else:
            return {
                "success": False,
                "message": response.message,
            }

    async def modify_strategy(
        self,
        session_id: str,
        modification: str,
    ) -> Dict[str, Any]:
        """
        Modify the current strategy based on user feedback.

        Args:
            session_id: Session identifier
            modification: User's modification request in natural language

        Returns:
            Modified strategy
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if not session.strategy:
            raise ValueError("No strategy to modify. Call propose_strategy first.")

        response = self.planner.modify_strategy(
            current_strategy=session.strategy,
            user_modification=modification,
            startup_profile=session.startup_profile,
        )

        if response.success:
            strategy_data = response.data.get("strategy", {})
            session.strategy = EvaluationStrategy.from_dict(strategy_data)

            session.token_usage["planner"] = session.token_usage.get("planner", 0) + response.tokens_used

            return {
                "success": True,
                "strategy": strategy_data,
                "changes_made": response.data.get("changes_made", []),
                "warnings": response.data.get("warnings", []),
                "summary": self.planner.generate_strategy_summary(session.strategy),
            }
        else:
            return {
                "success": False,
                "message": response.message,
            }

    async def confirm_strategy(self, session_id: str) -> Dict[str, Any]:
        """
        Confirm the current strategy and prepare for evaluation.

        Args:
            session_id: Session identifier

        Returns:
            Confirmation result
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if not session.strategy:
            raise ValueError("No strategy to confirm. Call propose_strategy first.")

        session.strategy.confirmed_by_user = True
        session.phase = "evaluating"

        return {
            "success": True,
            "message": "Strategy confirmed. Ready to begin evaluation.",
            "strategy": session.strategy.to_dict(),
            "dimensions": [dw.dimension.value for dw in session.strategy.dimensions],
        }

    # Phase 2: Multi-Dimensional Evaluation

    async def run_evaluation(
        self,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the full multi-dimensional evaluation.

        Args:
            session_id: Session identifier
            context: Additional context for evaluation

        Returns:
            Evaluation result
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if not session.strategy or not session.strategy.confirmed_by_user:
            raise ValueError("Strategy must be confirmed before evaluation. Call confirm_strategy first.")

        # Create specialized agents for each dimension
        dimension_agents = {}
        for dw in session.strategy.dimensions:
            dimension_agents[dw.dimension] = create_specialized_agent(
                dimension=dw.dimension,
                model=self.model,
            )

        # Run specialized evaluations in parallel
        dimension_results = {}
        evaluation_tasks = []

        for dimension, agent in dimension_agents.items():
            task = agent.evaluate_candidates(
                startup_profile=session.startup_profile,
                candidates=session.candidates,
                context=context,
            )
            evaluation_tasks.append((dimension, task))

        # Execute all evaluations
        for dimension, task in evaluation_tasks:
            response = task  # Already executed synchronously in current implementation
            if response.success:
                dimension_results[dimension] = response.data.get("scores", [])
                session.token_usage[f"specialized_{dimension.value}"] = response.tokens_used
            else:
                self.logger.warning(f"Evaluation failed for {dimension.value}: {response.message}")
                dimension_results[dimension] = []

        # Phase 3: Aggregation
        supervisor_response = self.supervisor.aggregate_and_rank(
            strategy=session.strategy,
            dimension_results=dimension_results,
            candidates=session.candidates,
            startup_profile=session.startup_profile,
        )

        if supervisor_response.success:
            result_data = supervisor_response.data.get("result", {})
            session.result = EvaluationResult(
                strategy=session.strategy,
                evaluations=[],  # Will be populated from result_data
                total_evaluated=result_data.get("total_evaluated", 0),
                top_candidates=[],
                summary=result_data.get("summary", ""),
                insights=result_data.get("insights", []),
                conflicts_resolved=result_data.get("conflicts_resolved", []),
            )
            session.phase = "complete"
            session.token_usage["supervisor"] = supervisor_response.tokens_used

            return {
                "success": True,
                "result": result_data,
                "insights": supervisor_response.data.get("insights", []),
                "conflicts": supervisor_response.data.get("conflicts", []),
                "token_usage": session.token_usage,
            }
        else:
            return {
                "success": False,
                "message": supervisor_response.message,
            }

    # Phase 3b: Iterative Refinement

    async def refine_results(
        self,
        session_id: str,
        refinement: RefinementRequest,
    ) -> Dict[str, Any]:
        """
        Refine evaluation results based on user feedback.

        Args:
            session_id: Session identifier
            refinement: User's refinement request

        Returns:
            Refined results
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if not session.result:
            raise ValueError("No results to refine. Run evaluation first.")

        response = self.supervisor.refine_results(
            current_result=session.result,
            refinement=refinement,
            startup_profile=session.startup_profile,
        )

        if response.success:
            result_data = response.data.get("result", {})
            session.token_usage["refinement"] = session.token_usage.get("refinement", 0) + response.tokens_used

            return {
                "success": True,
                "result": result_data,
                "changes_applied": response.data.get("changes_applied", []),
                "new_rankings": response.data.get("new_rankings", []),
            }
        else:
            return {
                "success": False,
                "message": response.message,
            }

    async def exclude_candidate(
        self,
        session_id: str,
        candidate_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Exclude a specific candidate from results.

        Args:
            session_id: Session identifier
            candidate_id: ID of candidate to exclude
            reason: Reason for exclusion

        Returns:
            Updated results
        """
        refinement = RefinementRequest.exclude_candidate(candidate_id, reason)
        return await self.refine_results(session_id, refinement)

    async def adjust_dimension_weight(
        self,
        session_id: str,
        dimension: EvaluationDimension,
        new_weight: float,
        reason: str = "",
    ) -> Dict[str, Any]:
        """
        Adjust the weight of a dimension and re-rank.

        Args:
            session_id: Session identifier
            dimension: Dimension to adjust
            new_weight: New weight value (0.0 to 1.0)
            reason: Reason for adjustment

        Returns:
            Updated results
        """
        refinement = RefinementRequest.adjust_dimension_weight(dimension, new_weight, reason)
        return await self.refine_results(session_id, refinement)

    # Utility methods

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get the current status of a session."""
        session = self.sessions.get(session_id)
        if not session:
            return {"success": False, "message": f"Session not found: {session_id}"}

        return {
            "success": True,
            "session_id": session_id,
            "phase": session.phase,
            "has_strategy": session.strategy is not None,
            "strategy_confirmed": session.strategy.confirmed_by_user if session.strategy else False,
            "has_result": session.result is not None,
            "candidates_count": len(session.candidates),
            "token_usage": session.token_usage,
            "created_at": session.created_at.isoformat(),
        }

    def get_total_token_usage(self, session_id: str) -> Dict[str, int]:
        """Get total token usage for a session."""
        session = self.sessions.get(session_id)
        if not session:
            return {}

        total_tokens = sum(session.token_usage.values())
        return {
            **session.token_usage,
            "total": total_tokens,
        }

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def is_debug_mode(self) -> bool:
        """Check if orchestrator is running in debug mode."""
        return self._debug_mode

    # Debug mode methods

    async def run_debug_evaluation(
        self,
        session_id: Optional[str] = None,
        num_candidates: int = 10,
        startup_profile: Optional[StartupProfile] = None,
    ) -> Dict[str, Any]:
        """
        Run a complete evaluation cycle with fake data (debug mode).

        This method bypasses all API calls and returns realistic fake data
        for testing the UI and workflow.

        Args:
            session_id: Optional session ID (auto-generated if not provided)
            num_candidates: Number of fake candidates to generate
            startup_profile: Optional startup profile (auto-generated if not provided)

        Returns:
            Complete evaluation result with fake data
        """
        import uuid

        if not self._debug_mode:
            DebugConfig.enable()
            self._debug_mode = True
            self._fake_data_generator = FakeDataGenerator()
            self.logger.info("Debug mode enabled for run_debug_evaluation")

        session_id = session_id or str(uuid.uuid4())
        generator = self._fake_data_generator or FakeDataGenerator()

        # Generate fake startup profile if not provided
        if startup_profile is None:
            startup_profile = generator.generate_startup_profile()

        # Generate fake candidates
        candidates = generator.generate_candidates(count=num_candidates)

        # Create session
        await self.create_session(session_id, startup_profile, candidates)

        # Generate fake strategy
        strategy = generator.generate_strategy(num_candidates=num_candidates)
        session = self.sessions[session_id]
        session.strategy = strategy
        session.phase = "planning"

        # Auto-confirm strategy
        session.strategy.confirmed_by_user = True
        session.phase = "evaluating"

        # Generate fake evaluation result
        result = generator.generate_evaluation_result(candidates, strategy)
        session.result = result
        session.phase = "complete"

        # Simulate token usage
        session.token_usage = {
            "planner": 500,
            "specialized_total": 1500,
            "supervisor": 800,
        }

        self.logger.info(f"Debug evaluation completed for session {session_id}")

        return {
            "success": True,
            "debug_mode": True,
            "session_id": session_id,
            "phase": "complete",
            "startup_profile": startup_profile.to_dict(),
            "candidates_count": len(candidates),
            "strategy": strategy.to_dict(),
            "result": result.to_dict(),
            "token_usage": session.token_usage,
        }

    def generate_debug_candidates(self, count: int = 10, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate fake candidate data for debug/testing purposes.

        Args:
            count: Number of candidates to generate
            industry: Optional industry filter

        Returns:
            List of fake candidate dictionaries
        """
        generator = self._fake_data_generator or FakeDataGenerator()
        return generator.generate_candidates(count=count, industry=industry)

    def generate_debug_strategy(self, num_candidates: int = 10) -> Dict[str, Any]:
        """
        Generate a fake evaluation strategy for debug/testing purposes.

        Args:
            num_candidates: Number of candidates the strategy is for

        Returns:
            Strategy dictionary
        """
        generator = self._fake_data_generator or FakeDataGenerator()
        strategy = generator.generate_strategy(num_candidates=num_candidates)
        return strategy.to_dict()

    def generate_debug_result(
        self,
        candidates: Optional[List[Dict[str, Any]]] = None,
        num_candidates: int = 10,
    ) -> Dict[str, Any]:
        """
        Generate a fake evaluation result for debug/testing purposes.

        Args:
            candidates: Optional list of candidates (auto-generated if not provided)
            num_candidates: Number of candidates if auto-generating

        Returns:
            Evaluation result dictionary
        """
        generator = self._fake_data_generator or FakeDataGenerator()

        if candidates is None:
            candidates = generator.generate_candidates(count=num_candidates)

        strategy = generator.generate_strategy(num_candidates=len(candidates))
        result = generator.generate_evaluation_result(candidates, strategy)
        return result.to_dict()


# Convenience function for simple evaluations
async def evaluate_partners(
    startup_profile: StartupProfile,
    candidates: List[Dict[str, Any]],
    partner_requirements: Optional[Dict[str, Any]] = None,
    auto_confirm: bool = False,
    model: str = "gpt-4.1",
) -> Dict[str, Any]:
    """
    Convenience function for running a complete evaluation.

    Args:
        startup_profile: Startup profile
        candidates: Candidates to evaluate
        partner_requirements: Additional requirements
        auto_confirm: If True, automatically confirm strategy
        model: LLM model to use

    Returns:
        Evaluation result
    """
    import uuid

    orchestrator = EvaluationOrchestrator(model=model)
    session_id = str(uuid.uuid4())

    # Create session
    await orchestrator.create_session(session_id, startup_profile, candidates)

    # Propose strategy
    strategy_result = await orchestrator.propose_strategy(session_id, partner_requirements)
    if not strategy_result["success"]:
        return strategy_result

    # Confirm strategy if auto_confirm
    if auto_confirm:
        await orchestrator.confirm_strategy(session_id)

        # Run evaluation
        return await orchestrator.run_evaluation(session_id)
    else:
        return {
            "success": True,
            "phase": "strategy_proposed",
            "session_id": session_id,
            "strategy": strategy_result["strategy"],
            "summary": strategy_result["summary"],
            "message": "Strategy proposed. Please confirm or modify before evaluation.",
        }
