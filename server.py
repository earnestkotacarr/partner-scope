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
from src.providers import MockCrunchbaseProvider

# Initialize FastAPI app
app = FastAPI(title="Partner Scope API", version="1.0.0")

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

        # Query MockCrunchbaseProvider for CSV-based results
        # TODO: Replace with full pipeline execution once Stage 2 & 3 are implemented
        matches = await _get_csv_results(request)

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
