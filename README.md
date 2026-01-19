# PartnerScope

**Intelligent Partner Discovery for Startups**

Turn weeks of manual partner research into minutes of conversation. PartnerScope combines conversational AI with structured search and multi-dimensional evaluation to help startups find and rank potential business partners.

> *From months of research to minutes of conversation.*

---

## The Problem

Finding the right business partners is one of the most time-consuming challenges for startups:

- Hours of manual research across databases and websites
- Inconsistent evaluation criteria across team members
- No systematic way to compare candidates
- Difficulty articulating exactly what kind of partner is needed

**PartnerScope solves this** by guiding you through a complete partner discovery workflow—from needs articulation to ranked recommendations.

---

## How It Works

```
Discovery Chat → Partner Search → Evaluation → Comparison
```

### 1. Discovery Chat

Start with a conversation, not a form. Our AI coach helps you articulate your partnership needs through natural dialogue.

**What makes it different:**
- Acts as a strategic advisor, not just a data collector
- Proactively suggests partnership types you may not have considered
- Extracts structured requirements from conversation

**What gets extracted:**
- Partner type (pilot, distribution, validation, etc.)
- Minimum requirements ("must have 100+ participants")
- Success criteria ("60% retention at week 8")
- Red flags to avoid
- Information to collect during outreach

### 2. Partner Search

Multi-source search combines database lookups with real-time AI web search.

| Source | Best For | Speed |
|--------|----------|-------|
| Database/CSV | Known players, established companies | Fast |
| AI Web Search | Emerging players, niche specialists | Thorough |

**5-Phase Search Architecture:**

| Phase | What Happens | Why It Matters |
|-------|--------------|----------------|
| 1. Discovery | 4 search queries from different angles | Casts a wide net |
| 2. Reflection | Analyzes gaps, searches for non-obvious partners | Finds what you didn't know to look for |
| 3. Decomposition | Breaks need into sub-needs, targeted search for each | Ensures comprehensive coverage |
| 4. Batch Filtering | Scores candidates in small batches | Maintains quality across large candidate sets |
| 5. Enrichment | Fills missing data for top candidates | Clean, complete output |

**Output:** 20 ranked partners with company details, partnership fit rationale, needs satisfied, and validation scores (1-10).

### 3. Evaluation

Multi-dimensional assessment with human-in-the-loop refinement.

**Available Dimensions:**

| Dimension | What It Measures |
|-----------|------------------|
| Market Compatibility | Target market alignment |
| Technical Synergy | Technology compatibility |
| Financial Health | Stability, funding status |
| Operational Capacity | Logistics, scale capability |
| Geographic Coverage | Regional presence |
| Strategic Alignment | Business goal fit |
| Cultural Fit | Organizational compatibility |
| Resource Complementarity | Complementary assets |
| Growth Potential | Scalability opportunity |
| Risk Profile | Potential challenges |

**Post-Evaluation Refinement:** Adjust results without re-running the entire evaluation:

| Action | Example | What Happens |
|--------|---------|--------------|
| Exclude | "Remove TechPartner, they're a competitor" | Filters out, re-ranks remaining |
| Reweight | "Prioritize geographic coverage" | Adjusts weights, recalculates scores |
| Filter | "Show only top 3" | Returns focused subset |
| Focus | "Tell me more about their weaknesses" | Deeper analysis |

### 4. Comparison with External Research

Validate results against other AI research tools (Gemini Deep Research, OpenAI Deep Research, Claude).

1. Run your preferred external research tool with the same query
2. Paste the results into PartnerScope
3. PartnerScope evaluates them using the same criteria
4. Side-by-side comparison shows which found better partners

---

## Quality vs. Speed vs. Cost

| Mode | Quality | Speed | Cost | Best For |
|------|---------|-------|------|----------|
| Quality | Highest | ~20-30 min | ~$0.32/search | Final selection, high-stakes decisions |
| Balanced | Good | ~20 sec | ~$0.18/search | Day-to-day use (recommended) |
| Fast | Basic | ~5 sec | ~$0.05/search | Quick exploration, brainstorming |

**Cost Transparency:**
- Discovery chat: ~$0.02/message
- Search (50 candidates): ~$0.80-1.50
- Evaluation: ~$0.15-0.30
- Typical full session: **$1-2 total**

No hidden fees. No subscriptions. Pay only for what you use.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/partner-scope.git
   cd partner-scope
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure API keys**
   ```bash
   cp config.yaml.template config.yaml
   cp .env.template .env
   ```

   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=sk-...
   ```

### Running the Application

**Development Mode** (with hot reload):

```bash
# Terminal 1: Frontend
cd frontend
npm run dev
# → http://localhost:3000

# Terminal 2: Backend
python server.py
# → http://localhost:8000
```

**Production Mode:**

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start server (serves built frontend)
python server.py
# → http://localhost:8000
```

### CLI Usage

```bash
python main.py \
  --startup-name "CoVital Node" \
  --investment-stage "Seed" \
  --product-stage "MVP" \
  --partner-needs "Housing partners for pilot testing" \
  --industry "Healthcare/Robotics" \
  --max-results 50
```

### Debug Mode

Test the application without API calls using fake data:

```bash
# Backend
DEBUG_MODE=1 python server.py

# Frontend (browser console)
window.debug.enable()
```

---

## Project Structure

```
partner-scope/
├── frontend/                 # React application
│   ├── src/
│   │   ├── pages/           # LandingPage, EvaluationPage, ResultsPage
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # React context providers
│   │   └── hooks/           # Custom React hooks
│   └── dist/                # Production build
│
├── src/                     # Python backend
│   ├── providers/           # Data source integrations
│   │   ├── base.py         # BaseProvider interface
│   │   ├── mock_crunchbase.py
│   │   ├── openai_web_search.py
│   │   └── ...
│   ├── core/               # Business logic
│   │   ├── aggregator.py   # Company deduplication
│   │   └── ranker.py       # LLM-based ranking
│   ├── chat/               # Conversational AI
│   │   ├── startup_discovery.py
│   │   └── evaluation_assistant.py
│   ├── evaluation/         # Evaluation framework
│   │   ├── models.py
│   │   ├── orchestrator.py
│   │   └── agents/
│   └── pipeline.py         # Main orchestrator
│
├── server.py               # FastAPI entry point
├── main.py                 # CLI entry point
├── config.yaml             # Configuration
├── results/                # Generated reports
└── work/                   # Debug/intermediate files
```

---

## Architecture

| Layer | Component | Technology |
|-------|-----------|------------|
| Frontend | Web Interface | React 19, Tailwind CSS, Real-time Updates |
| Backend | API Server | FastAPI, Streaming SSE |
| Services | Discovery Chat | Conversational partner needs extraction |
| | Search Provider | Multi-source candidate discovery |
| | Evaluation Assistant | Multi-dimensional scoring & refinement |
| AI | Language Model | OpenAI GPT-4.1 + Web Search |

**Key Design Decisions:**
- Single LLM with specialized prompts (not multi-agent)
- Batch processing to avoid quality degradation at scale
- External state management for consistent scoring
- Human-in-the-loop at every stage

---

## Use Cases

**Pilot Partners**
> "We need universities or employers who can provide 100-300 users for an 8-12 week pilot"

**Distribution Partners**
> "Looking for healthcare distributors with hospital network relationships"

**Technology Partners**
> "Need API integration partners in the fintech space"

**Validation Partners**
> "Seeking research institutions for clinical validation studies"

---

## Configuration

### config.yaml

```yaml
providers:
  crunchbase:
    enabled: false
  openai_web_search:
    enabled: true

llm:
  provider: openai  # or anthropic
  model: gpt-4.1

pipeline:
  similarity_threshold: 0.85
  max_results: 50
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (required) |
| `CRUNCHBASE_API_KEY` | Crunchbase API key (optional) |
| `DEBUG_MODE` | Enable debug mode with fake data |

---

## Output Formats

**Markdown Report** (`results/{startup}_{timestamp}.md`)
- Executive summary
- Ranked partners with scores
- Detailed rationales
- Contact information

**JSON Data** (`results/{startup}_{timestamp}.json`)
- Structured data for programmatic access
- Full evaluation details

**CSV Export**
- Exportable from the web UI
- Sortable by any evaluation dimension

---

## Make Commands

```bash
make install     # Install all dependencies
make setup       # Create config files from templates
make test        # Run test suite
make clean       # Clean generated files
make run         # Show example CLI command
```

---

## Research Foundation

PartnerScope draws inspiration from academic research in partner selection:

- **PartnerMAS** (arXiv:2509.24046): Multi-agent framework for partner evaluation
- **Batch Processing**: Inspired by insights from Recursive Language Models (arXiv:2512.24601)

We've adapted these approaches for practical startup use—prioritizing interactivity and human control over full automation.

---

## Technical Specifications

- **Backend:** Python 3.12+, FastAPI
- **Frontend:** React 19, Tailwind CSS
- **AI Models:** OpenAI GPT-4.1 series (configurable)
- **Data Sources:** CSV/Database import, Real-time web search
- **Output Formats:** JSON, Markdown, CSV

---

## Team

**Team 3 - Corundum Corp** | UTokyo GMSI Innovation Workshop

 