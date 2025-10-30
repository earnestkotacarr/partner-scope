# Partner Scope - Project Overview

## Project Status
✅ **Scaffolded and ready for implementation**

This project has been scaffolded with a complete architecture, clear module boundaries, and comprehensive TODO comments throughout. All core modules are in place and ready for implementation.

## Architecture

### High-Level Flow
```
1. INPUT: Startup Profile
   ├─ Name, stage, product phase
   └─ Partner requirements

2. DATA COLLECTION: Query Multiple Providers
   ├─ Crunchbase (API)
   ├─ CB Insights (Web Scraping)
   ├─ LinkedIn (API/Scraping)
   └─ Web Search (Generic)

3. AGGREGATION: Deduplicate & Merge
   ├─ Domain matching
   ├─ Name similarity
   └─ Confidence scoring

4. RANKING: LLM-Based Analysis
   ├─ Match scoring (0-100)
   ├─ Rationale generation
   └─ Action recommendations

5. OUTPUT: Reports & Data
   ├─ Markdown report
   ├─ JSON data file
   └─ Debug files
```

## Project Structure

```
partner-scope/
│
├── src/                          # Source code
│   ├── providers/                # Data source integrations
│   │   ├── base.py              # Abstract base provider class
│   │   ├── crunchbase.py        # Crunchbase API (TODO)
│   │   ├── cbinsights.py        # CB Insights scraping (TODO)
│   │   ├── linkedin.py          # LinkedIn integration (TODO)
│   │   └── web_search.py        # Generic web search (TODO)
│   │
│   ├── core/                     # Core functionality
│   │   ├── aggregator.py        # Deduplication logic (TODO)
│   │   └── ranker.py            # LLM-based ranking (TODO)
│   │
│   ├── pipeline.py              # Main orchestrator (TODO)
│   └── utils.py                 # Utility functions
│
├── examples/                     # Example usage scripts
│   └── example_usage.py         # Three example scenarios
│
├── tests/                        # Test suite
│   └── test_aggregator.py       # Unit tests (TODO)
│
├── work/                         # Debug/intermediate files
├── results/                      # Final output reports
├── logs/                         # Application logs
│
├── main.py                       # CLI entry point
├── config.yaml.template          # Configuration template
├── .env.template                 # Environment variables template
├── requirements.txt              # Python dependencies
├── README.md                     # User documentation
└── .gitignore                    # Git ignore rules
```

## Module Details

### 1. Data Providers (`src/providers/`)

**Base Provider (`base.py`)**
- Abstract interface for all data sources
- Defines standardized company schema
- Methods: `search_companies()`, `get_company_details()`, `normalize_company_data()`

**Crunchbase Provider (`crunchbase.py`)**
- ✅ Structure in place
- ⏳ TODO: Implement API calls
- ⏳ TODO: Add authentication
- ⏳ TODO: Implement pagination
- ⏳ TODO: Add data normalization

**CB Insights Provider (`cbinsights.py`)**
- ✅ Structure in place
- ⏳ TODO: Implement web scraping
- ⏳ TODO: Add rate limiting
- ⏳ TODO: Parse search results
- ⏳ TODO: Extract company profiles

**LinkedIn Provider (`linkedin.py`)**
- ✅ Structure in place
- ⏳ TODO: Implement search
- ⏳ TODO: Extract contact information
- ⏳ TODO: Handle authentication
- ⚠️  Note: LinkedIn restricts scraping heavily

**Web Search Provider (`web_search.py`)**
- ✅ Structure in place
- ⏳ TODO: Integrate Google Custom Search API
- ⏳ TODO: Implement website scraping
- ⏳ TODO: Extract social media links
- ⏳ TODO: Parse structured data

### 2. Core Modules (`src/core/`)

**Aggregator (`aggregator.py`)**
- ✅ `CompanyRecord` dataclass defined
- ✅ `normalize_domain()` implemented
- ⏳ TODO: Implement `are_duplicates()`
- ⏳ TODO: Implement `merge_companies()`
- ⏳ TODO: Implement `calculate_name_similarity()`
- ⏳ TODO: Implement `save_to_markdown()`

**Ranker (`ranker.py`)**
- ✅ `StartupProfile` and `PartnerMatch` dataclasses defined
- ✅ Prompt template structure in place
- ⏳ TODO: Initialize LLM client
- ⏳ TODO: Implement `rank_partners()`
- ⏳ TODO: Implement `evaluate_batch()`
- ⏳ TODO: Parse LLM responses
- ⏳ TODO: Implement `save_rankings_to_markdown()`

### 3. Pipeline (`src/pipeline.py`)

**PartnerPipeline**
- ✅ Initialization structure complete
- ✅ Provider management set up
- ✅ High-level flow defined
- ⏳ TODO: Implement `_query_providers()`
- ⏳ TODO: Wire up aggregation
- ⏳ TODO: Wire up ranking
- ⏳ TODO: Implement `_generate_output()`
- ⏳ TODO: Add error handling
- ⏳ TODO: Add progress logging

## Next Steps - Implementation Priority

### Phase 1: Core Infrastructure (Week 1-2)
1. **Set up development environment**
   - Install dependencies: `pip install -r requirements.txt`
   - Create `config.yaml` from template
   - Set up API keys in `.env`

2. **Implement Aggregator**
   - Start with `are_duplicates()` using simple domain matching
   - Implement `merge_companies()`
   - Add fuzzy name matching using `fuzzywuzzy`
   - Test with mock data

3. **Implement basic LLM Ranker**
   - Set up OpenAI client
   - Implement single company evaluation
   - Test with manual company data
   - Iterate on prompt engineering

### Phase 2: Data Providers (Week 3-4)
4. **Crunchbase Integration**
   - Set up API authentication
   - Implement company search
   - Implement data normalization
   - Test with real queries

5. **Web Search Integration**
   - Set up Google Custom Search API
   - Implement basic search
   - Add website scraping for company details
   - Extract social media links

6. **CB Insights Scraping**
   - Set up BeautifulSoup/Selenium
   - Implement search page scraping
   - Extract company profiles
   - Add rate limiting

### Phase 3: Integration & Output (Week 5)
7. **Wire Up Pipeline**
   - Connect all providers
   - Implement query logic
   - Add error handling
   - Test end-to-end flow

8. **Output Generation**
   - Implement markdown report generation
   - Add JSON export
   - Create debug file saving
   - Format contact information nicely

### Phase 4: Polish & Testing (Week 6)
9. **Testing**
   - Write unit tests for aggregator
   - Write unit tests for ranker
   - Add integration tests
   - Test with real startup scenarios

10. **Documentation & Examples**
    - Document API configuration
    - Add more example scenarios
    - Create troubleshooting guide
    - Document rate limits and costs

## Configuration

### Required API Keys
- **Crunchbase**: Get from https://www.crunchbase.com/
- **Google Custom Search**: Get from https://developers.google.com/custom-search
- **OpenAI**: Get from https://platform.openai.com/api-keys

### Optional API Keys
- **Anthropic Claude**: Alternative to OpenAI
- **LinkedIn**: For authenticated access (difficult to obtain)

## Example Scenarios Included

1. **Food Safety Startup (TempTrack)**
   - MVP stage
   - Looking for logistics partners
   - Temperature tracking stickers

2. **Fintech Startup (PayFlow)**
   - Series A stage
   - Looking for regional banks
   - Payment processing platform

3. **Healthcare IT Startup (HealthTrack)**
   - Series B stage
   - Looking for hospital networks
   - EHR integration platform

## Development Tips

1. **Start Small**: Implement one provider at a time, test thoroughly
2. **Use Mock Data**: Create sample company data for testing before API integration
3. **Prompt Engineering**: The LLM prompts in `ranker.py` will need iteration
4. **Rate Limiting**: Be careful with API costs and rate limits
5. **Logging**: Add comprehensive logging for debugging
6. **Caching**: Consider caching API responses to save costs during development

## Cost Considerations

- **Crunchbase API**: Paid tier required for production use
- **OpenAI GPT-4**: ~$0.03-0.06 per company evaluation (can be expensive at scale)
- **Google Custom Search**: 100 free queries/day, then $5/1000 queries
- **Web Scraping**: Free but requires maintenance (websites change)

### Cost Optimization Ideas
- Batch LLM evaluations (10-20 companies per call)
- Cache API responses
- Use GPT-3.5-turbo for initial filtering, GPT-4 for final ranking
- Implement result limits per provider

## Key Design Decisions

1. **Provider Abstraction**: All providers implement `BaseProvider` for consistency
2. **Standardized Schema**: All company data normalized to common format
3. **LLM-Based Ranking**: Flexible, no hard-coded rules (can evolve)
4. **Markdown Output**: Human-readable reports for VC workflow
5. **Work Directory**: Debug files help troubleshoot and iterate
6. **Configuration Driven**: Easy to enable/disable providers and adjust settings

## Known Limitations & Risks

1. **LinkedIn Restrictions**: LinkedIn heavily restricts scraping; may not be viable
2. **API Rate Limits**: Must implement careful rate limiting
3. **Web Scraping Fragility**: Websites change; scrapers break
4. **LLM Costs**: Can be expensive at scale
5. **Data Quality**: Provider data may be incomplete or outdated
6. **Deduplication Accuracy**: Complex problem; may have false positives/negatives

## Future Enhancements

- Database storage instead of markdown files
- Web UI for easier interaction
- Automated email outreach
- CRM integration (Salesforce, HubSpot)
- More data sources (AngelList, PitchBook, etc.)
- Advanced filtering and search
- Partnership recommendation learning (ML model)
- Track outreach status and responses

---

**Status**: Ready for implementation
**Estimated Effort**: 6-8 weeks for MVP
**Primary Language**: Python 3.8+
**Key Dependencies**: requests, beautifulsoup4, openai, fuzzywuzzy
