"""
FastAPI web server for Partner Scope.

This server provides:
1. API endpoints for the partner search pipeline
2. Static file serving for the React frontend
"""
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

from src.pipeline import PartnerPipeline
from src.core import StartupProfile

# Initialize FastAPI app
app = FastAPI(title="Partner Scope API", version="1.0.0")

# Configuration
# TODO: Load from config file or environment variables
CONFIG = {
    'crunchbase': {'enabled': False},  # Disabled by default until API keys are configured
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


# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Partner Scope API is running"}


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

        # For now, we'll return mock data until the pipeline is fully implemented
        # TODO: Replace with actual pipeline execution once implemented
        matches = await _get_mock_results(request)

        return SearchResponse(
            startup_name=request.startup_name,
            matches=matches,
            total_matches=len(matches),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _get_mock_results(request: SearchRequest) -> list[PartnerMatchResponse]:
    """
    Generate mock results for testing the UI.

    TODO: Remove this once the pipeline is fully implemented.
    """
    # Simulate some processing time
    await asyncio.sleep(2)

    # Return mock data based on the request
    mock_matches = [
        {
            "company_name": "GlobalLogistics Corp",
            "company_info": {
                "website": "https://globallogistics.example.com",
                "industry": "Logistics & Supply Chain",
                "location": "Chicago, IL",
                "linkedin_url": "https://linkedin.com/company/globallogistics",
            },
            "match_score": 92,
            "rationale": f"Excellent match for {request.startup_name}. GlobalLogistics operates a large fleet and has expressed interest in food safety innovations. Their distribution network spans 40 states, making them ideal for a pilot program.",
            "key_strengths": [
                "Extensive distribution network across North America",
                "Strong focus on food safety and compliance",
                "Budget allocated for innovation pilots",
                "Existing temperature monitoring infrastructure",
            ],
            "potential_concerns": [
                "May require lengthy procurement process",
                "Corporate decision-making can be slow",
            ],
            "recommended_action": "High priority - reach out to VP of Operations",
        },
        {
            "company_name": "FreshChain Solutions",
            "company_info": {
                "website": "https://freshchain.example.com",
                "industry": "Cold Chain Logistics",
                "location": "Dallas, TX",
                "linkedin_url": "https://linkedin.com/company/freshchain",
                "twitter_url": "https://twitter.com/freshchain",
            },
            "match_score": 85,
            "rationale": "Strong alignment with partner needs. FreshChain specializes in temperature-sensitive logistics and has been actively seeking innovation partners.",
            "key_strengths": [
                "Specialized in perishable goods transport",
                "Recent funding round for innovation",
                "Expressed pain points align with solution",
            ],
            "potential_concerns": [
                "Smaller scale than GlobalLogistics",
                "May have budget constraints",
            ],
            "recommended_action": "Reach out to innovation team",
        },
        {
            "company_name": "RegionalFreight Inc",
            "company_info": {
                "website": "https://regionalfreight.example.com",
                "industry": "Transportation",
                "location": "Atlanta, GA",
            },
            "match_score": 72,
            "rationale": "Moderate fit. RegionalFreight handles some food logistics but it's not their core focus. Could be a good secondary partner.",
            "key_strengths": [
                "Regional presence in Southeast",
                "Flexible partnership approach",
            ],
            "potential_concerns": [
                "Food logistics is only 20% of their business",
                "Limited resources for pilots",
                "May not have right expertise",
            ],
            "recommended_action": "Research more before reaching out",
        },
    ]

    return [PartnerMatchResponse(**match) for match in mock_matches]


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

    if not FRONTEND_DIST.exists():
        print("\n⚠️  Frontend not built. Run the following to build it:")
        print("   cd frontend && npm run build\n")

    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
