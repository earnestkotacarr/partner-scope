"""
FastAPI web server for Partner Scope.

This server provides:
1. API endpoints for the partner search pipeline
2. Static file serving for the React frontend
3. SSE streaming for real-time cost updates
4. Export endpoints for PDF and CSV
"""
import asyncio
import json
import csv
import io
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import os
from pathlib import Path

from src.pipeline import PartnerPipeline
from src.core import StartupProfile
from src.providers import MockCrunchbaseProvider, OpenAIWebSearchProvider
from src.chat import StartupDiscoveryAssistant, RefinementAssistant
from src.chat.prompts import STARTUP_DISCOVERY_PROMPT, REFINEMENT_PROMPT

# Import evaluation framework router
from src.evaluation.api import router as evaluation_router

# Import debug mode utilities
from src.debug import DebugConfig, FakeDataGenerator

# Initialize FastAPI app
app = FastAPI(title="Partner Scope API", version="1.0.0")

# Include evaluation framework router
app.include_router(evaluation_router)

# Configuration
# TODO: Load from config file or environment variables
CONFIG = {
    'mock_crunchbase': {'enabled': True},  # Use CSV-based mock provider
    'crunchbase': {'enabled': False},
    'cbinsights': {'enabled': False},
    'linkedin': {'enabled': False},
    'web_search': {'enabled': False},
    'llm': {
        'model': 'gpt-4',
        'api_key': os.getenv('OPENAI_API_KEY'),
    },
    'work_dir': 'work',
    'results_dir': 'results',
}

# Initialize pipeline
pipeline = PartnerPipeline(CONFIG)


# Request/Response Models
class SearchRequest(BaseModel):
    """Request model for partner search."""
    startup_name: str
    investment_stage: str
    product_stage: str
    partner_needs: str
    industry: Optional[str] = ""
    description: Optional[str] = ""
    max_results: Optional[int] = 20
    use_csv: Optional[bool] = True
    use_web_search: Optional[bool] = False


class PartnerMatchResponse(BaseModel):
    """Response model for a single partner match."""
    company_name: str
    company_info: dict
    match_score: float
    rationale: str
    key_strengths: list[str]
    potential_concerns: list[str]
    recommended_action: str


class SearchResponse(BaseModel):
    """Response model for partner search."""
    startup_name: str
    matches: list[PartnerMatchResponse]
    total_matches: int
    cost: Optional[dict] = None  # Cost breakdown for the search


# Chat Request/Response Models
class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # 'user' or 'assistant'
    content: str


class DiscoveryChatRequest(BaseModel):
    """Request model for startup discovery chat."""
    messages: list[dict]
    current_message: str


class DiscoveryChatResponse(BaseModel):
    """Response model for startup discovery chat."""
    response: str
    ready_for_template: bool
    suggested_actions: list[str]
    cost: Optional[dict] = None  # Cost breakdown for this chat turn


class GenerateTemplateRequest(BaseModel):
    """Request model for generating scenario template."""
    messages: list[dict]


class GenerateTemplateResponse(BaseModel):
    """Response model for scenario template."""
    scenario_template: dict
    cost: Optional[dict] = None  # Cost breakdown for template generation


class RefinementRequest(BaseModel):
    """Request model for result refinement."""
    messages: list[dict]
    current_message: str
    current_results: list[dict]
    scenario: dict


class RefinementResponse(BaseModel):
    """Response model for result refinement."""
    response: str
    refined_results: list[dict]
    applied_filters: list[str]
    action_taken: str
    cost: Optional[dict] = None  # Cost breakdown for refinement


# Export Request/Response Models
class ExportRequest(BaseModel):
    """Request model for exporting results."""
    scenario: dict
    results: list[dict]
    chat_history: Optional[list[dict]] = []
    costs: Optional[list[dict]] = []
    format: str = "pdf"  # "pdf" or "csv"


# Evaluation Chat Request/Response Models
class EvaluationChatRequest(BaseModel):
    """Request model for evaluation chat."""
    messages: list[dict]
    current_message: str
    session_id: Optional[str] = None
    phase: str = "init"
    candidates: list[dict] = []
    startup_profile: Optional[dict] = None
    strategy: Optional[dict] = None
    evaluation_result: Optional[dict] = None
    action_hint: Optional[str] = None  # Explicit action from frontend buttons


class EvaluationChatResponse(BaseModel):
    """Response model for evaluation chat."""
    response: str
    session_id: Optional[str] = None
    phase: str = "init"
    strategy: Optional[dict] = None
    evaluation_result: Optional[dict] = None
    cost: Optional[dict] = None


# Initialize chat assistants
discovery_assistant = StartupDiscoveryAssistant()
refinement_assistant = RefinementAssistant()


# ============================================================================
# Debug Mode API Routes
# ============================================================================

class DebugModeRequest(BaseModel):
    """Request model for enabling/disabling debug mode."""
    enabled: bool
    skip_planner_llm: Optional[bool] = True
    skip_specialized_llm: Optional[bool] = True
    skip_supervisor_llm: Optional[bool] = True
    skip_web_search: Optional[bool] = True
    simulate_delay: Optional[bool] = False
    verbose: Optional[bool] = True


class DebugEvaluationRequest(BaseModel):
    """Request model for debug evaluation."""
    num_candidates: Optional[int] = 10
    startup_name: Optional[str] = None
    industry: Optional[str] = None


@app.get("/api/debug/status")
async def get_debug_status():
    """
    Get the current debug mode status.

    Returns the debug configuration settings.
    """
    settings = DebugConfig.get_settings()
    return {
        "debug_mode": DebugConfig.is_enabled(),
        "settings": {
            "skip_planner_llm": settings.skip_planner_llm,
            "skip_specialized_llm": settings.skip_specialized_llm,
            "skip_supervisor_llm": settings.skip_supervisor_llm,
            "skip_web_search": settings.skip_web_search,
            "skip_ranking_llm": settings.skip_ranking_llm,
            "simulate_delay": settings.simulate_delay,
            "verbose": settings.verbose,
            "fake_candidates_count": settings.fake_candidates_count,
        }
    }


@app.post("/api/debug/enable")
async def enable_debug_mode(request: DebugModeRequest):
    """
    Enable or disable debug mode.

    When debug mode is enabled, the system will use fake data
    instead of making actual API calls.
    """
    if request.enabled:
        DebugConfig.enable(
            skip_planner_llm=request.skip_planner_llm,
            skip_specialized_llm=request.skip_specialized_llm,
            skip_supervisor_llm=request.skip_supervisor_llm,
            skip_web_search=request.skip_web_search,
            simulate_delay=request.simulate_delay,
            verbose=request.verbose,
        )
        return {
            "success": True,
            "message": "Debug mode enabled",
            "debug_mode": True,
        }
    else:
        DebugConfig.disable()
        return {
            "success": True,
            "message": "Debug mode disabled",
            "debug_mode": False,
        }


@app.post("/api/debug/evaluation")
async def run_debug_evaluation(request: DebugEvaluationRequest):
    """
    Run a complete evaluation cycle with fake data.

    This endpoint bypasses all API calls and returns realistic fake data
    for testing the UI and workflow.
    """
    from src.evaluation.orchestrator import EvaluationOrchestrator
    from src.evaluation.models import StartupProfile as EvalStartupProfile

    # Enable debug mode if not already enabled
    if not DebugConfig.is_enabled():
        DebugConfig.enable()

    generator = FakeDataGenerator()

    # Generate startup profile
    startup_profile = generator.generate_startup_profile(
        name=request.startup_name,
        industry=request.industry,
    )

    # Run debug evaluation
    orchestrator = EvaluationOrchestrator(debug_mode=True)
    result = await orchestrator.run_debug_evaluation(
        num_candidates=request.num_candidates,
        startup_profile=startup_profile,
    )

    return result


@app.get("/api/debug/candidates")
async def get_debug_candidates(count: int = 10, industry: Optional[str] = None):
    """
    Generate fake candidate data for testing.

    Args:
        count: Number of candidates to generate
        industry: Optional industry filter
    """
    generator = FakeDataGenerator()
    candidates = generator.generate_candidates(count=count, industry=industry)
    return {
        "success": True,
        "debug_mode": True,
        "count": len(candidates),
        "candidates": candidates,
    }


@app.get("/api/debug/strategy")
async def get_debug_strategy(num_candidates: int = 10):
    """
    Generate a fake evaluation strategy for testing.

    Args:
        num_candidates: Number of candidates the strategy is for
    """
    generator = FakeDataGenerator()
    strategy = generator.generate_strategy(num_candidates=num_candidates)
    return {
        "success": True,
        "debug_mode": True,
        "strategy": strategy.to_dict(),
    }


@app.get("/api/debug/result")
async def get_debug_result(num_candidates: int = 10):
    """
    Generate a complete fake evaluation result for testing.

    Args:
        num_candidates: Number of candidates to evaluate
    """
    generator = FakeDataGenerator()
    candidates = generator.generate_candidates(count=num_candidates)
    strategy = generator.generate_strategy(num_candidates=num_candidates)
    result = generator.generate_evaluation_result(candidates, strategy)

    return {
        "success": True,
        "debug_mode": True,
        "candidates_count": len(candidates),
        "result": result.to_dict(),
    }


# ============================================================================
# Standard API Routes
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Partner Scope API is running",
        "debug_mode": DebugConfig.is_enabled(),
    }


@app.post("/api/search", response_model=SearchResponse)
async def search_partners(request: SearchRequest):
    """
    Search for potential partners for a startup.

    This endpoint triggers the partner matching pipeline and returns
    ranked results based on the startup's needs.
    """
    try:
        # Run pipeline in background thread to avoid blocking
        # TODO: Consider using Celery or similar for long-running tasks
        loop = asyncio.get_event_loop()

        def run_pipeline():
            return pipeline.run(
                startup_name=request.startup_name,
                investment_stage=request.investment_stage,
                product_stage=request.product_stage,
                partner_needs=request.partner_needs,
                industry=request.industry,
                description=request.description,
                max_results=request.max_results,
            )

        # Aggregate results from selected data sources
        all_matches = []

        if request.use_csv:
            csv_matches = await _get_csv_results(request)
            # Tag source for display
            for m in csv_matches:
                m.company_info["source"] = "CrunchBase CSV"
            all_matches.extend(csv_matches)

        if request.use_web_search:
            web_matches = await _get_web_search_results(request)
            # Tag source for display
            for m in web_matches:
                m.company_info["source"] = "AI Web Search"
            all_matches.extend(web_matches)

        # Sort by score descending and limit results
        all_matches.sort(key=lambda x: x.match_score, reverse=True)
        matches = all_matches[:request.max_results or 20]

        return SearchResponse(
            startup_name=request.startup_name,
            matches=matches,
            total_matches=len(matches),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _get_csv_results(request: SearchRequest) -> list[PartnerMatchResponse]:
    """
    Query the MockCrunchbaseProvider CSV data and return results.

    Uses keyword matching to find relevant companies from pre-curated CSV files.
    """
    # Initialize the mock provider
    provider = MockCrunchbaseProvider({})

    # Search using the partner_needs as the query
    companies = provider.search_companies(
        query=request.partner_needs,
        filters={'max_results': request.max_results or 20}
    )

    # Transform company dictionaries to PartnerMatchResponse format
    matches = []
    for i, company in enumerate(companies):
        # Calculate a simple relevance score based on position (will be replaced by LLM ranking later)
        base_score = 95 - (i * 2)  # Decreasing score by position
        score = max(50, min(99, base_score))  # Clamp between 50-99

        description = company.get('description', '') or ''
        industry = company.get('industry', '') or ''
        location = company.get('location', '') or ''
        raw_data = company.get('raw_data', {}) or {}

        match = PartnerMatchResponse(
            company_name=company.get('name', 'Unknown'),
            company_info={
                "website": company.get('website', ''),
                "industry": industry,
                "location": location,
                "description": description,
                "crunchbase_url": raw_data.get('crunchbase_url', ''),
            },
            match_score=score,
            rationale=f"Found via CrunchBase search. {description[:200] + '...' if len(description) > 200 else description or 'No description available.'}",
            key_strengths=[
                f"Industry: {industry}" if industry else "Industry data available",
                f"Location: {location}" if location else "Location data available",
            ],
            potential_concerns=[
                "Requires further evaluation (Stage 2 not yet implemented)",
            ],
            recommended_action="Review company details and assess fit manually",
        )
        matches.append(match)

    return matches


async def _get_web_search_results(request: SearchRequest) -> list[PartnerMatchResponse]:
    """
    Query OpenAI Web Search for real-time partner discovery.

    Uses GPT-4o with web search to find companies matching the partner needs.
    """
    import asyncio

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
        )

    # Initialize the web search provider
    provider = OpenAIWebSearchProvider({})

    # Run the synchronous search in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    companies = await loop.run_in_executor(
        None,
        lambda: provider.search_companies(
            query=request.partner_needs,
            filters={'max_results': request.max_results or 10}
        )
    )

    # Transform company dictionaries to PartnerMatchResponse format
    matches = []
    for i, company in enumerate(companies):
        # Calculate a simple relevance score based on position
        base_score = 95 - (i * 3)
        score = max(50, min(99, base_score))

        description = company.get('description', '') or ''
        industry = company.get('industry', '') or ''
        location = company.get('location', '') or ''
        size = company.get('size', '') or ''

        match = PartnerMatchResponse(
            company_name=company.get('name', 'Unknown'),
            company_info={
                "website": company.get('website', ''),
                "industry": industry,
                "location": location,
                "description": description,
                "size": size,
            },
            match_score=score,
            rationale=f"Found via AI web search. {description[:200] + '...' if len(description) > 200 else description or 'No description available.'}",
            key_strengths=[
                f"Industry: {industry}" if industry and industry != 'Not available' else "Industry match pending",
                f"Location: {location}" if location and location != 'Not available' else "Location data pending",
                f"Size: {size}" if size and size != 'Not available' else "Size data pending",
            ],
            potential_concerns=[
                "Web search results - verify company details independently",
            ],
            recommended_action="Review company website and validate fit",
        )
        matches.append(match)

    return matches


# Chat API Routes
@app.post("/api/chat/startup", response_model=DiscoveryChatResponse)
async def startup_chat(request: DiscoveryChatRequest):
    """
    Process a message in the startup discovery chat.

    This endpoint helps startups discover their partnership needs through conversation.
    """
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )

        # Run chat in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: discovery_assistant.chat(request.messages, request.current_message)
        )

        return DiscoveryChatResponse(
            response=result["response"],
            ready_for_template=result["ready_for_template"],
            suggested_actions=result["suggested_actions"],
            cost=result.get("cost")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/startup/generate-template", response_model=GenerateTemplateResponse)
async def generate_template(request: GenerateTemplateRequest):
    """
    Generate a scenario template from the conversation history.

    Extracts structured data from the discovery conversation.
    """
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )

        # Run extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        template = await loop.run_in_executor(
            None,
            lambda: discovery_assistant.generate_template(request.messages)
        )

        # Extract cost from template (if present)
        template_cost = template.pop('_cost', None)

        return GenerateTemplateResponse(
            scenario_template=template,
            cost=template_cost
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/refine", response_model=RefinementResponse)
async def refine_results(request: RefinementRequest):
    """
    Refine search results through natural language instructions.

    Allows users to filter, reorder, expand, or narrow results.
    Also supports triggering new searches for expansion.
    """
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )

        print(f"\n[Refinement] Request: '{request.current_message}'")
        print(f"[Refinement] Input results count: {len(request.current_results)}")

        # Run refinement in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: refinement_assistant.refine_results(
                request.messages,
                request.current_message,
                request.current_results,
                request.scenario
            )
        )

        print(f"[Refinement] Action taken: {result['action_taken']}")

        # Handle NEW SEARCH action
        if result.get('action_taken') == 'search':
            search_query = result.get('search_query', '')
            search_focus = result.get('search_focus', '')
            merge_mode = result.get('merge_mode', 'add')

            print(f"[Refinement] Triggering NEW SEARCH: '{search_query}'")
            print(f"[Refinement] Search focus: '{search_focus}'")
            print(f"[Refinement] Merge mode: {merge_mode}")

            # Create search provider for web search
            web_provider = OpenAIWebSearchProvider()

            # Build search profile from scenario + refinement focus
            search_profile = StartupProfile(
                name=request.scenario.get('startup_name', 'startup'),
                investment_stage=request.scenario.get('investment_stage', 'Seed'),
                product_stage=request.scenario.get('product_stage', 'MVP'),
                partner_needs=search_query,  # Use the refined search query
                industry=request.scenario.get('industry', ''),
                description=request.scenario.get('description', '')
            )

            # Run web search
            def run_search():
                return web_provider.get_potential_partners(search_profile, max_results=10)

            new_companies = await loop.run_in_executor(None, run_search)

            print(f"[Refinement] New search found {len(new_companies)} companies")

            # Rank new results
            def run_ranking():
                return pipeline.ranker.rank_partners(new_companies, search_profile)

            new_matches = await loop.run_in_executor(None, run_ranking)

            # Get search cost
            search_usage = web_provider.get_last_usage()
            search_cost = None
            if search_usage:
                search_cost = {
                    "input_tokens": search_usage.total_input_tokens,
                    "output_tokens": search_usage.total_output_tokens,
                    "web_search_calls": search_usage.api_calls,
                    "total_cost": search_usage.total_cost
                }

            # Merge results based on mode
            if merge_mode == 'replace':
                final_results = new_matches
                response_text = f"Searched for new partners and found {len(new_matches)} results."
            else:  # 'add' mode - merge and deduplicate
                existing_names = {r.get('company_name', '').lower() for r in request.current_results}
                unique_new = [m for m in new_matches if m.get('company_name', '').lower() not in existing_names]

                final_results = request.current_results + unique_new
                # Sort by match score
                final_results.sort(key=lambda x: x.get('match_score', 0), reverse=True)

                response_text = f"Found {len(unique_new)} new partners and added them to your results. Total: {len(final_results)}"

            print(f"[Refinement] Final results count: {len(final_results)}")

            # Combine costs
            total_cost = result.get('cost', {})
            if search_cost:
                total_cost = {
                    "input_tokens": (total_cost.get('input_tokens', 0) or 0) + search_cost.get('input_tokens', 0),
                    "output_tokens": (total_cost.get('output_tokens', 0) or 0) + search_cost.get('output_tokens', 0),
                    "web_search_calls": search_cost.get('web_search_calls', 0),
                    "total_cost": (total_cost.get('total_cost', 0) or 0) + search_cost.get('total_cost', 0)
                }

            return RefinementResponse(
                response=response_text,
                refined_results=final_results,
                applied_filters=[],
                action_taken="expanded",
                cost=total_cost
            )

        # Standard filter/reorder action
        print(f"[Refinement] Output results count: {len(result['refined_results'])}")
        print(f"[Refinement] Response: {result['response'][:100]}...")

        return RefinementResponse(
            response=result["response"],
            refined_results=result["refined_results"],
            applied_filters=result["applied_filters"],
            action_taken=result["action_taken"],
            cost=result.get("cost")
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Evaluation Chat Endpoint
@app.post("/api/evaluation/chat", response_model=EvaluationChatResponse)
async def evaluation_chat(request: EvaluationChatRequest):
    """
    Process a message in the evaluation chat.

    This endpoint handles the conversational evaluation workflow:
    - Phase 1 (planning): Strategy proposal and modification
    - Phase 2 (evaluating): Running multi-dimensional evaluation
    - Phase 3 (complete): Presenting results and handling refinements
    """
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
            )

        print(f"\n[EvaluationChat] Message: '{request.current_message}'")
        print(f"[EvaluationChat] Phase: {request.phase}, Session: {request.session_id}")
        print(f"[EvaluationChat] Candidates: {len(request.candidates)}")

        # Import here to avoid circular imports
        from src.chat.evaluation_assistant import EvaluationChatAssistant

        # Run evaluation chat in thread pool
        loop = asyncio.get_event_loop()
        assistant = EvaluationChatAssistant()

        result = await loop.run_in_executor(
            None,
            lambda: assistant.chat(
                messages=request.messages,
                current_message=request.current_message,
                session_id=request.session_id,
                phase=request.phase,
                candidates=request.candidates,
                startup_profile=request.startup_profile,
                strategy=request.strategy,
                evaluation_result=request.evaluation_result,
                action_hint=request.action_hint,
            )
        )

        print(f"[EvaluationChat] Response phase: {result.get('phase')}")

        return EvaluationChatResponse(
            response=result["response"],
            session_id=result.get("session_id"),
            phase=result.get("phase", request.phase),
            strategy=result.get("strategy"),
            evaluation_result=result.get("evaluation_result"),
            cost=result.get("cost"),
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# SSE Streaming Search Endpoint
@app.get("/api/search/stream")
async def stream_search(
    startup_name: str,
    investment_stage: str,
    product_stage: str,
    partner_needs: str,
    industry: str = "",
    description: str = "",
    max_results: int = 20,
    use_csv: bool = True,
    use_web_search: bool = False
):
    """
    Stream search progress and results using Server-Sent Events.

    Yields events as the search progresses:
    - progress: Updates on search progress with running cost
    - result: Individual match results
    - complete: Final summary with total cost
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        total_cost = {
            'input_tokens': 0,
            'output_tokens': 0,
            'web_search_calls': 0,
            'input_cost': 0.0,
            'output_cost': 0.0,
            'web_search_cost': 0.0,
            'total_cost': 0.0,
        }
        all_matches = []

        try:
            # Send start event
            yield f"event: progress\ndata: {json.dumps({'phase': 'starting', 'message': 'Initializing search...', 'cost': total_cost})}\n\n"

            # CSV Search
            if use_csv:
                yield f"event: progress\ndata: {json.dumps({'phase': 'csv_search', 'message': 'Searching CSV database...', 'cost': total_cost})}\n\n"

                provider = MockCrunchbaseProvider({})
                companies = provider.search_companies(
                    query=partner_needs,
                    filters={'max_results': max_results}
                )

                for i, company in enumerate(companies):
                    base_score = 95 - (i * 2)
                    score = max(50, min(99, base_score))
                    description_text = company.get('description', '') or ''

                    match = {
                        'company_name': company.get('name', 'Unknown'),
                        'company_info': {
                            "website": company.get('website', ''),
                            "industry": company.get('industry', '') or '',
                            "location": company.get('location', '') or '',
                            "description": description_text,
                            "source": "CrunchBase CSV",
                        },
                        'match_score': score,
                        'rationale': f"Found via CrunchBase search. {description_text[:200]}..." if len(description_text) > 200 else description_text or 'No description available.',
                        'key_strengths': [f"Industry: {company.get('industry', 'N/A')}"],
                        'potential_concerns': ["Requires further evaluation"],
                        'recommended_action': "Review company details",
                    }
                    all_matches.append(match)

                yield f"event: progress\ndata: {json.dumps({'phase': 'csv_complete', 'message': f'Found {len(companies)} companies from CSV', 'count': len(companies), 'cost': total_cost})}\n\n"

            # Web Search
            if use_web_search:
                yield f"event: progress\ndata: {json.dumps({'phase': 'web_search_start', 'message': 'Starting AI web search...', 'cost': total_cost})}\n\n"

                if not os.getenv('OPENAI_API_KEY'):
                    yield f"event: error\ndata: {json.dumps({'error': 'OpenAI API key not configured'})}\n\n"
                else:
                    provider = OpenAIWebSearchProvider({})

                    # Run synchronous search in thread pool
                    loop = asyncio.get_event_loop()

                    # Search for company list
                    yield f"event: progress\ndata: {json.dumps({'phase': 'web_search_list', 'message': 'Searching for companies...', 'cost': total_cost})}\n\n"

                    companies = await loop.run_in_executor(
                        None,
                        lambda: provider.search_companies(
                            query=partner_needs,
                            filters={'max_results': max_results or 10}
                        )
                    )

                    # Get usage from provider
                    usage = provider.get_last_usage()
                    if usage:
                        total_cost['input_tokens'] += usage.total_input_tokens
                        total_cost['output_tokens'] += usage.total_output_tokens
                        total_cost['web_search_calls'] += usage.total_web_search_calls
                        total_cost['input_cost'] += usage.total_input_cost
                        total_cost['output_cost'] += usage.total_output_cost
                        total_cost['web_search_cost'] += usage.total_web_search_cost
                        total_cost['total_cost'] += usage.total_cost

                    # Process each company
                    for i, company in enumerate(companies):
                        base_score = 95 - (i * 3)
                        score = max(50, min(99, base_score))
                        description_text = company.get('description', '') or ''

                        match = {
                            'company_name': company.get('name', 'Unknown'),
                            'company_info': {
                                "website": company.get('website', ''),
                                "industry": company.get('industry', '') or '',
                                "location": company.get('location', '') or '',
                                "description": description_text,
                                "source": "AI Web Search",
                            },
                            'match_score': score,
                            'rationale': f"Found via AI web search. {description_text[:200]}..." if len(description_text) > 200 else description_text or 'No description available.',
                            'key_strengths': [f"Industry: {company.get('industry', 'N/A')}"],
                            'potential_concerns': ["Web search results - verify independently"],
                            'recommended_action': "Review company website",
                        }
                        all_matches.append(match)

                        # Send progress update for each company
                        yield f"event: progress\ndata: {json.dumps({'phase': 'company_details', 'company': company.get('name', 'Unknown'), 'index': i + 1, 'total': len(companies), 'cost': total_cost})}\n\n"

            # Sort and limit results
            all_matches.sort(key=lambda x: x['match_score'], reverse=True)
            final_matches = all_matches[:max_results]

            # Send complete event
            yield f"event: complete\ndata: {json.dumps({'startup_name': startup_name, 'matches': final_matches, 'total_matches': len(final_matches), 'cost': total_cost})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# Export Endpoints
@app.post("/api/export/csv")
async def export_csv(request: ExportRequest):
    """
    Export search results as a CSV file.
    """
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            'Company Name', 'Website', 'Industry', 'Location',
            'Match Score', 'Rationale', 'Key Strengths',
            'Potential Concerns', 'Recommended Action', 'Source'
        ])

        # Data rows
        for result in request.results:
            company_info = result.get('company_info', {})
            writer.writerow([
                result.get('company_name', ''),
                company_info.get('website', ''),
                company_info.get('industry', ''),
                company_info.get('location', ''),
                result.get('match_score', ''),
                result.get('rationale', ''),
                '; '.join(result.get('key_strengths', [])),
                '; '.join(result.get('potential_concerns', [])),
                result.get('recommended_action', ''),
                company_info.get('source', ''),
            ])

        output.seek(0)
        filename = f"partner_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/pdf")
async def export_pdf(request: ExportRequest):
    """
    Export full session report as a PDF file.

    Includes: chat history, system prompts used, search results, and cost breakdown.
    """
    try:
        # Generate PDF using reportlab
        pdf_bytes = _generate_pdf_reportlab(request)

        filename = f"partner_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_pdf_reportlab(request: ExportRequest) -> bytes:
    """Generate PDF content using reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    scenario = request.scenario
    results = request.results
    chat_history = request.chat_history or []
    costs = request.costs or []

    # Calculate total cost
    total_cost = sum(c.get('total_cost', 0) for c in costs) if costs else 0

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, spaceAfter=6, textColor=colors.HexColor('#0f172a'))
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor('#1e40af'))
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#3730a3'))
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'))
    centered_style = ParagraphStyle('Centered', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
    chat_user_style = ParagraphStyle('ChatUser', parent=styles['Normal'], fontSize=9, backColor=colors.HexColor('#eff6ff'), spaceBefore=4, spaceAfter=4, leftIndent=10, rightIndent=10)
    chat_assistant_style = ParagraphStyle('ChatAssistant', parent=styles['Normal'], fontSize=9, backColor=colors.HexColor('#f8fafc'), spaceBefore=4, spaceAfter=4, leftIndent=10, rightIndent=10)

    # Build story (content)
    story = []

    # Header
    story.append(Paragraph("Partner Search Report", title_style))
    story.append(Paragraph(f"<b>{scenario.get('startup_name', 'Unknown Startup')}</b>", centered_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", small_style))
    story.append(Spacer(1, 20))

    # Search Profile Section
    story.append(Paragraph("Search Profile", heading_style))
    story.append(Paragraph(f"<b>Industry:</b> {scenario.get('industry', 'Not specified')}", normal_style))
    story.append(Paragraph(f"<b>Investment Stage:</b> {scenario.get('investment_stage', 'Not specified')}", normal_style))
    story.append(Paragraph(f"<b>Product Stage:</b> {scenario.get('product_stage', 'Not specified')}", normal_style))
    story.append(Paragraph(f"<b>Partner Needs:</b>", normal_style))
    story.append(Paragraph(scenario.get('partner_needs', 'Not specified'), normal_style))
    story.append(Spacer(1, 10))

    # Chat History Section
    if chat_history:
        story.append(Paragraph("Discovery Conversation", heading_style))
        for msg in chat_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            style = chat_user_style if role == 'user' else chat_assistant_style
            story.append(Paragraph(f"<b>{role.upper()}:</b> {content[:500]}{'...' if len(content) > 500 else ''}", style))
        story.append(Spacer(1, 10))

    # System Prompts Section (abbreviated)
    story.append(Paragraph("System Prompts Used", heading_style))
    story.append(Paragraph("Discovery Assistant Prompt", subheading_style))
    prompt_preview = STARTUP_DISCOVERY_PROMPT[:300].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    story.append(Paragraph(f"<font size=8>{prompt_preview}...</font>", small_style))
    story.append(Paragraph("Refinement Assistant Prompt", subheading_style))
    prompt_preview2 = REFINEMENT_PROMPT[:300].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    story.append(Paragraph(f"<font size=8>{prompt_preview2}...</font>", small_style))
    story.append(Spacer(1, 10))

    # Results Section
    story.append(Paragraph(f"Search Results ({len(results)} matches)", heading_style))

    for i, result in enumerate(results[:20], 1):  # Limit to 20 for PDF
        company_info = result.get('company_info', {})
        score = result.get('match_score', 0)
        name = result.get('company_name', 'Unknown')
        industry = company_info.get('industry', 'N/A')
        location = company_info.get('location', 'N/A')
        rationale = result.get('rationale', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        website = company_info.get('website', 'N/A')

        # Score color
        if score >= 80:
            score_color = '#22c55e'
        elif score >= 60:
            score_color = '#eab308'
        else:
            score_color = '#ef4444'

        story.append(Paragraph(f"<b>{i}. {name}</b> <font color='{score_color}'>[Score: {score}]</font>", subheading_style))
        story.append(Paragraph(f"<i>{industry} | {location}</i>", small_style))
        story.append(Paragraph(rationale[:300] + ('...' if len(rationale) > 300 else ''), normal_style))
        story.append(Paragraph(f"<b>Website:</b> {website}", small_style))

        strengths = result.get('key_strengths', [])
        if strengths:
            story.append(Paragraph("<b>Key Strengths:</b> " + ", ".join(strengths[:3]), small_style))

        concerns = result.get('potential_concerns', [])
        if concerns:
            story.append(Paragraph("<b>Concerns:</b> " + ", ".join(concerns[:2]), small_style))

        story.append(Paragraph(f"<b>Recommended Action:</b> {result.get('recommended_action', 'N/A')}", small_style))
        story.append(Spacer(1, 8))

    # Cost Summary Section
    story.append(Paragraph("Cost Summary", heading_style))

    cost_data = [['Operation', 'Tokens', 'Cost']]
    for cost in costs:
        cost_data.append([
            cost.get('operation', 'Unknown'),
            f"{cost.get('input_tokens', 0):,} in / {cost.get('output_tokens', 0):,} out",
            f"${cost.get('total_cost', 0):.6f}"
        ])
    cost_data.append(['Total Session Cost', '', f"${total_cost:.6f}"])

    cost_table = Table(cost_data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(cost_table)

    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by PartnerScope", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#64748b'))))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


@app.get("/api/prompts")
async def get_prompts():
    """
    Get the system prompts used by the assistants.

    Useful for including in exports and debugging.
    """
    return {
        "discovery_prompt": STARTUP_DISCOVERY_PROMPT,
        "refinement_prompt": REFINEMENT_PROMPT,
    }


# Serve static files from the React build
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    # Serve index.html for all other routes (SPA support)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA."""
        # If file exists, serve it
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise, serve index.html (SPA fallback)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    print("Warning: Frontend dist directory not found. Run 'npm run build' in the frontend directory.")

    @app.get("/")
    async def root():
        """Root endpoint when frontend is not built."""
        return {
            "message": "Partner Scope API is running",
            "note": "Frontend not built. Run 'cd frontend && npm run build' to build the frontend."
        }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("Partner Scope Server")
    print("="*80)
    print("\nStarting server at http://localhost:8000")
    print("\nAPI Documentation available at http://localhost:8000/docs")

    # Check for debug mode
    if DebugConfig.is_enabled():
        print("\n🔧 DEBUG MODE ENABLED")
        print("   - Using fake data instead of API calls")
        print("   - Set DEBUG_MODE=0 to disable")
    else:
        print("\n💡 Tip: Set DEBUG_MODE=1 to enable debug mode with fake data")

    if not FRONTEND_DIST.exists():
        print("\n⚠️  Frontend not built. Run the following to build it:")
        print("   cd frontend && npm run build\n")

    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
