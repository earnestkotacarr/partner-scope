# Partner Scope

**Team 3 - Corundum Corp** | UTokyo GMSI Innovation Workshop

A VC partner-matching pipeline that helps find and rank potential partners for startups.

## Current Status (Dec 2024)

### ✅ What's Working

**Stage 1 - Search & Identification:**

| Component | Status | Description |
|-----------|--------|-------------|
| MockCrunchbaseProvider | ✅ Working | Reads from pre-curated CrunchBase CSV exports with keyword-based query matching |
| OpenAI Web Search | ✅ Working | GPT-4o with web search for real-time partner discovery |
| React Frontend | ✅ Working | Vite + Tailwind CSS form with color-coded match scores |
| FastAPI Backend | ✅ Working | Web server with mock data endpoints |

**Configured Test Startups:**

1. **CoVital Node** - doorway co-regulation robot for loneliness
   - Pilot partners (100 companies): dorm operators, co-living, employers
   - Validation partners (150 companies): research labs, hospitals for IRB/ethics

2. **StellarCore Mining** - asteroid resource-mapping AI
   - Data-source partners (300 companies): smallsat, spacecraft, sensors
   - Validation partners (300 companies): planetary science labs

### 🚧 What Needs To Be Done

**Immediate Admin:**
- [ ] Activate Crunchbase Pro subscription
- [ ] Add $100 credits to OpenAI
- [ ] Send receipts to GMSI Office

**Stage 1 - Search & Identification:**
- [ ] Chatbot to help startups define partner requirements (Earnest & Claude)
- [ ] Generate Scenario Template from conversation (Earnest & Claude)
- [ ] Integrate real Crunchbase API when available (Shreejan)
- [ ] Look into both Companies and Investors (Shreejan)

**Stage 2 - Evaluation & Analysis:**
- [ ] Criteria Assessment (geographic match, past collaborations, needs)
- [ ] Business Viability Check
- [ ] "E" Score summarization

**Stage 3 - Recommendation & Output:**
- [ ] Generate recommendation reports (CSV/Interface)
- [ ] Include: potential targets, partner candidates, detailed info, growth potential
- [ ] Transparency: links/sources

**Backend (Wentao):**
- [ ] Web Search provider improvements
- [ ] Pipeline integration

**Scenarios for Midterm (Dec 18):**
- [ ] Space - Wentao/Natsuki
- [ ] AI/ALife - Earnest
- [ ] Health - Shreejan
- [ ] Environment - Amalie

---

## Overview

Partner Scope automates the process of finding suitable corporate partners for startups by:

1. **Data Collection**: Searches multiple sources (Crunchbase, CB Insights, web search) for potential partner companies
2. **Deduplication**: Intelligently merges and deduplicates company data from different sources
3. **AI Ranking**: Uses LLM-based analysis to rank and match partners based on startup needs
4. **Reporting**: Generates detailed reports with scores, rationales, and contact information

## Project Structure

```
partner-scope/
├── src/
│   ├── providers/              # Data source integrations
│   │   ├── base.py             # Base provider interface
│   │   ├── crunchbase.py       # Crunchbase API integration
│   │   ├── mock_crunchbase.py  # Mock provider using CSV exports
│   │   ├── openai_web_search.py# OpenAI GPT-4o web search
│   │   ├── cbinsights.py       # CB Insights web scraping
│   │   ├── linkedin.py         # LinkedIn integration
│   │   └── web_search.py       # Generic web search
│   ├── core/                   # Core functionality
│   │   ├── aggregator.py       # Company deduplication and merging
│   │   └── ranker.py           # LLM-based partner ranking
│   └── pipeline.py             # Main pipeline orchestrator
├── csv/                        # Pre-curated CrunchBase exports
│   ├── covital-pilot-partners.csv
│   ├── covital-validation-partners.csv
│   ├── partner1_space.csv
│   └── partner2_space.csv
├── frontend/                   # React + Vite frontend
├── web/                        # FastAPI backend
├── work/                       # Working directory (debug files)
├── results/                    # Final output reports
├── tests/                      # Test suite
└── requirements.txt            # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the template files and add your API keys:

```bash
cp config.yaml.template config.yaml
cp .env.template .env
```

Edit `config.yaml` and `.env` to add your API keys:
- **Crunchbase API**: https://www.crunchbase.com/
- **Google Custom Search API**: https://developers.google.com/custom-search
- **OpenAI API**: https://platform.openai.com/api-keys

### 3. Run the Pipeline

```python
from src.pipeline import PartnerPipeline

config = {...}  # Load from config.yaml
pipeline = PartnerPipeline(config)

results = pipeline.run(
    startup_name="TempTrack",
    investment_stage="Seed",
    product_stage="MVP",
    partner_needs="Large logistics company for pilot testing temperature tracking stickers",
    industry="Food Safety / Supply Chain",
    max_results=20
)
```

## Usage

### Input Parameters

- **startup_name**: Name of the startup
- **investment_stage**: Current funding stage (Seed, Series A, etc.)
- **product_stage**: Development stage (MVP, Beta, Launched, etc.)
- **partner_needs**: Description of what the startup is looking for in a partner
- **industry**: Startup's industry (optional)
- **description**: Brief description of the startup (optional)

### Output

The pipeline generates:

1. **Markdown Report** (`results/{startup_name}_{timestamp}.md`):
   - Executive summary
   - Ranked list of partners with scores
   - Detailed rationales
   - Contact information and social links
   - Recommended next steps

2. **JSON Data** (`results/{startup_name}_{timestamp}.json`):
   - Structured data for programmatic access

3. **Debug Files** (`work/` directory):
   - Raw provider results
   - Aggregated companies
   - Intermediate processing data

## Next Steps

See the **What Needs To Be Done** section at the top for current development tasks.

Key milestones:
- **Dec 18, 2024** - Midterm Presentation (4 scenarios required)

## Example Scenarios

### Scenario 1: CoVital Node (AI/Robotics)
```python
# Doorway co-regulation robot for loneliness
# Partner 1: Pilot population (housing/employers)
provider.search_companies("dorm university co-living employer student housing wellness")

# Partner 2: Validation (research institutions)
provider.search_companies("research IRB ethics clinical psych HCI hospital lab")
```

### Scenario 2: StellarCore Mining (Space)
```python
# Asteroid resource-mapping AI
# Partner 1: Data-source partners
provider.search_companies("satellite spacecraft smallsat cubesat radar sensor aerospace")

# Partner 2: Scientific validation
provider.search_companies("planetary science research lab mineralogy geology asteroid")
```

## Notes

- **API Costs**: Be mindful of API costs, especially for LLM calls. Consider batching and caching.
- **Rate Limiting**: Implement rate limiting to avoid being blocked by data sources.
- **Legal**: Respect Terms of Service for all data sources, especially when web scraping.
- **Data Privacy**: Handle contact information responsibly and comply with data protection regulations.

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
