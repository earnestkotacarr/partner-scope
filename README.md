# Partner Scope

A VC partner-matching pipeline that helps find and rank potential partners for startups.

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
│   ├── providers/          # Data source integrations
│   │   ├── base.py         # Base provider interface
│   │   ├── crunchbase.py   # Crunchbase API integration
│   │   ├── cbinsights.py   # CB Insights web scraping
│   │   ├── linkedin.py     # LinkedIn integration
│   │   └── web_search.py   # Generic web search
│   ├── core/               # Core functionality
│   │   ├── aggregator.py   # Company deduplication and merging
│   │   └── ranker.py       # LLM-based partner ranking
│   └── pipeline.py         # Main pipeline orchestrator
├── work/                   # Working directory (debug files)
├── results/                # Final output reports
├── tests/                  # Test suite
├── config.yaml             # Configuration file
├── .env                    # Environment variables (API keys)
└── requirements.txt        # Python dependencies
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

This is a scaffolded project with TODO comments throughout. Key implementation tasks:

### Data Providers
- [ ] Implement Crunchbase API integration
- [ ] Implement CB Insights web scraping
- [ ] Implement LinkedIn data extraction
- [ ] Implement web search and scraping

### Core Functionality
- [ ] Implement company deduplication logic
- [ ] Implement LLM-based ranking
- [ ] Add prompt engineering for better matching

### Pipeline
- [ ] Wire up all components in pipeline.py
- [ ] Add error handling and retry logic
- [ ] Implement output generation
- [ ] Add progress tracking and logging

### Testing
- [ ] Add unit tests for core modules
- [ ] Add integration tests for providers
- [ ] Add end-to-end pipeline tests

### Enhancements
- [ ] Add CLI interface
- [ ] Add database storage option
- [ ] Add caching for API responses
- [ ] Add rate limiting and quota management
- [ ] Add support for additional data sources

## Example Scenarios

### Scenario 1: Food Safety Startup
```python
pipeline.run(
    startup_name="TempTrack",
    investment_stage="Seed",
    product_stage="MVP",
    partner_needs="Large logistics company for pilot testing temperature tracking stickers",
    industry="Food Safety / Supply Chain"
)
```

### Scenario 2: Fintech Startup
```python
pipeline.run(
    startup_name="PayFlow",
    investment_stage="Series A",
    product_stage="Beta",
    partner_needs="Regional banks for payment processing pilot program",
    industry="Fintech"
)
```

### Scenario 3: Healthcare SaaS
```python
pipeline.run(
    startup_name="HealthTrack",
    investment_stage="Series B",
    product_stage="Launched",
    partner_needs="Hospital networks for EHR integration and deployment",
    industry="Healthcare IT"
)
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
