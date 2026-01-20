# PartnerScope

**Intelligent Partner Discovery for Startups**

---

## The Problem

Finding the right business partners is one of the most time-consuming and critical challenges for startups. Traditional approaches involve:

- Hours of manual research across databases and websites
- Inconsistent evaluation criteria across team members
- No systematic way to compare candidates
- Difficulty articulating exactly what kind of partner is needed

**PartnerScope solves this** by combining conversational AI with structured search and evaluation—turning weeks of research into minutes.

---

## How It Works

PartnerScope guides startups through a complete partner discovery workflow:

```
Discovery Chat → Partner Search → Evaluation → Refinement → Comparison
```

### 1. Discovery Chat

Start with a conversation, not a form. Our AI coach helps you articulate your partnership needs through natural dialogue.

**What makes it different:**
- Acts as a strategic advisor, not a data collector
- Proactively suggests partnership types you may not have considered
- Extracts structured requirements from conversation

**Sample dialogue:**
```
You: "We're building a wellness app for students"

PartnerScope: "Tell me more about how it works—what does the
app actually do, and what makes it different from other
wellness apps?"

You: "It uses AI agents to create a personalized co-regulation
companion that responds to check-ins and nudges users
toward social contact"

PartnerScope: "That's a unique approach—AI-driven co-regulation
rather than generic wellness content. For something this
personalized, you'd likely need a Pilot Population Partner—
an organization with users who could test it over several weeks.

What scale are you thinking for a pilot? 50 users? 500?"
```

**What gets extracted:**
- Partner type (pilot, distribution, validation, etc.)
- Minimum requirements ("must have 100+ participants")
- Success criteria ("60% retention at week 8")
- Red flags to avoid ("no single owner on the org side")
- Information to collect during outreach

---

### 2. Partner Search

Multi-source search combines database lookups with real-time AI web search.

**Data Sources:**

| Source | Best For | Speed |
|--------|----------|-------|
| **Database/CSV** | Known players, established companies | Fast |
| **AI Web Search** | Emerging players, niche specialists | Thorough |

Use both together for comprehensive coverage, or individually based on your needs.

**5-Phase Search Architecture:**

| Phase | What Happens | Why It Matters |
|-------|--------------|----------------|
| **1. Discovery** | 4 search queries from different angles | Casts a wide net |
| **2. Reflection** | Analyzes gaps, searches for non-obvious partners | Finds what you didn't know to look for |
| **3. Decomposition** | Breaks need into sub-needs, targeted search for each | Ensures comprehensive coverage |
| **4. Batch Filtering** | Scores candidates in small batches | Maintains quality across large candidate sets |
| **5. Enrichment** | Fills missing data for top candidates | Clean, complete output |

**Output:** 20 ranked partners with:
- Company details (name, website, industry, location)
- Partnership fit rationale
- Needs they satisfy
- Validation score (1-10)

---

### 3. Evaluation

Multi-dimensional assessment with human-in-the-loop refinement.

**Dynamic Strategy:**
Instead of fixed criteria, you control the evaluation dimensions and weights:

```
Proposed Strategy:
1. Market Compatibility (25%)
2. Technical Synergy (25%)
3. Strategic Alignment (20%)
4. Growth Potential (15%)
5. Risk Profile (15%)

You: "Focus more on technical synergy, we need API integration"

Adjusted:
- Technical Synergy: 35% (was 25%)
- Market Compatibility: 20% (was 25%)
```

**Available Dimensions:**

| Dimension | What It Measures |
|-----------|-----------------|
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

---

### 4. Refinement

As results come in, you learn more about what fits. Refinement lets you iterate without starting over.

**What you can do:**

| Action | Example | What Happens |
|--------|---------|--------------|
| **Adjust weights** | "Prioritize geographic coverage" | Recalculates scores, re-ranks instantly |
| **Exclude candidates** | "Remove TechPartner, they're a competitor" | Filters out, remaining candidates re-rank |
| **Change criteria** | "Add regulatory experience as a dimension" | New evaluation dimension applied |
| **Re-research** | "Find more APAC partners" | Additional targeted search, results merged |
| **Dig deeper** | "Tell me about their weaknesses" | Detailed analysis of specific candidates |

Traditional research is linear: search once, deliver, start over if priorities change. PartnerScope is iterative—refine specifications, re-search specific areas, and build on what you've learned.

---

### 5. Comparison with External Research

Validate results against other AI research tools—Gemini Deep Research, OpenAI Deep Research, or Claude.

**How it works:**
1. Run your preferred external research tool with the same query
2. Paste the results into PartnerScope
3. PartnerScope evaluates them using the same criteria
4. Side-by-side comparison shows which found better partners

**Metrics compared:**
- Top-8 average score
- Overall average score
- Score distribution
- Specific candidate rankings

This provides objective validation that your partner search is producing high-quality results.

---

## Quality vs. Speed vs. Cost

Choose the right balance for your situation:

| Mode | Quality | Speed | Cost | Best For |
|------|---------|-------|------|----------|
| **Quality** | Highest | ~20-30 min | ~$0.32/search | Final selection, high-stakes decisions |
| **Balanced** | Good | ~20 sec | ~$0.18/search | Day-to-day use (recommended) |
| **Fast** | Basic | ~5 sec | ~$0.05/search | Quick exploration, brainstorming |

Select your mode before running a search. All modes use the same methodology—the difference is in the AI model powering each stage.

---

## Cost Transparency

Every operation shows real-time cost tracking:

- Discovery chat: ~$0.02/message
- Search (50 candidates): ~$0.80-1.50
- Evaluation: ~$0.15-0.30
- Typical full session: **$1-2 total**

No hidden fees. No subscriptions. Pay only for what you use.

---

## Architecture

| Layer | Component | Technology |
|-------|-----------|------------|
| **Frontend** | Web Interface | React, Tailwind, Real-time Updates |
| **Backend** | API Server | FastAPI, Streaming SSE |
| **Services** | Discovery Chat | Conversational partner needs extraction |
| | Search Provider | Multi-source candidate discovery |
| | Evaluation Assistant | Multi-dimensional scoring & refinement |
| **AI** | Language Model | OpenAI GPT-4.1 + Web Search Tool |

**Key Design Decisions:**
- Single LLM with specialized prompts (not multi-agent)
- Batch processing to avoid quality degradation at scale
- External state management for consistent scoring
- Human-in-the-loop at every stage

---

## What Makes PartnerScope Different

| Traditional Approach | PartnerScope |
|---------------------|--------------|
| Manual database searches | AI-powered multi-source discovery |
| Spreadsheet tracking | Structured evaluation with rankings |
| Gut-feel decisions | Multi-dimensional scoring with confidence |
| One-time analysis | Dynamic refinement without re-running |
| No validation | Comparison against external research tools |

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

## Getting Started

1. **Start a conversation** — Tell us about your startup
2. **Review your profile** — Edit the extracted requirements
3. **Run search** — Select data sources and quality level
4. **Evaluate results** — Customize dimensions and weights
5. **Compare & refine** — Validate against external tools, adjust as needed

The entire process takes 5-15 minutes for a comprehensive partner search that would traditionally require days of manual research.

---

## Technical Specifications

- **Backend:** Python, FastAPI
- **Frontend:** React, Tailwind CSS
- **AI Models:** OpenAI GPT-4.1 series (configurable)
- **Data Sources:** CSV/Database import, Real-time web search
- **Output Formats:** JSON, exportable rankings

---

## Research Foundation

PartnerScope draws inspiration from academic research in partner selection:

- **PartnerMAS** (arXiv:2509.24046): Multi-agent framework for partner evaluation
- **Batch Processing**: Inspired by insights from Recursive Language Models (arXiv:2512.24601)

We've adapted these approaches for practical startup use—prioritizing interactivity and human control over full automation.

---

*PartnerScope — From months of research to minutes of conversation.*

*UTokyo Research, 2026*
