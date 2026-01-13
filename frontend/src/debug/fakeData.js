/**
 * Frontend Fake Data Generator
 *
 * Generates realistic fake data for testing UI without API calls.
 * Mirrors the backend FakeDataGenerator structure.
 */

// Seeded random number generator for reproducibility
class SeededRandom {
  constructor(seed = 42) {
    this.seed = seed;
  }

  // Simple LCG random number generator
  random() {
    this.seed = (this.seed * 1664525 + 1013904223) % 4294967296;
    return this.seed / 4294967296;
  }

  randInt(min, max) {
    return Math.floor(this.random() * (max - min + 1)) + min;
  }

  choice(array) {
    return array[Math.floor(this.random() * array.length)];
  }

  sample(array, k) {
    const shuffled = [...array].sort(() => this.random() - 0.5);
    return shuffled.slice(0, k);
  }
}

// Sample data constants
const COMPANY_PREFIXES = [
  'Tech', 'Global', 'Smart', 'Next', 'Future', 'Data', 'Cloud', 'Cyber',
  'Digital', 'AI', 'Quantum', 'Bio', 'Green', 'Eco', 'Solar', 'Nano',
];

const COMPANY_SUFFIXES = [
  'Corp', 'Labs', 'Systems', 'Solutions', 'Technologies', 'Dynamics',
  'Innovations', 'Ventures', 'Partners', 'Group', 'Industries', 'Networks',
];

const INDUSTRIES = [
  'Software & Technology',
  'Healthcare & Biotech',
  'Financial Services',
  'E-commerce & Retail',
  'Manufacturing',
  'Energy & Utilities',
  'Transportation & Logistics',
  'Education & EdTech',
  'Media & Entertainment',
  'Agriculture & FoodTech',
];

const LOCATIONS = [
  'San Francisco, CA',
  'New York, NY',
  'Boston, MA',
  'Austin, TX',
  'Seattle, WA',
  'Los Angeles, CA',
  'Chicago, IL',
  'Denver, CO',
  'Tokyo, Japan',
  'London, UK',
  'Berlin, Germany',
  'Singapore',
];

const COMPANY_SIZES = [
  '1-10 employees',
  '11-50 employees',
  '51-200 employees',
  '201-500 employees',
  '501-1000 employees',
  '1000+ employees',
];

const STRENGTH_TEMPLATES = [
  'Strong market presence in {industry}',
  'Proven track record with similar partnerships',
  'Well-funded with {funding} in recent rounds',
  'Experienced leadership team',
  'Complementary technology stack',
  'Strong geographic coverage in target markets',
  'Excellent customer retention rate',
  'Innovative product portfolio',
];

const WEAKNESS_TEMPLATES = [
  'Limited experience with startups',
  'Potential cultural alignment challenges',
  'Long decision-making cycles',
  'Geographic limitations in some regions',
];

const DIMENSIONS = [
  { id: 'MARKET_COMPATIBILITY', label: 'Market Compatibility', weight: 0.20 },
  { id: 'FINANCIAL_HEALTH', label: 'Financial Health', weight: 0.15 },
  { id: 'TECHNICAL_SYNERGY', label: 'Technical Synergy', weight: 0.20 },
  { id: 'OPERATIONAL_CAPACITY', label: 'Operational Capacity', weight: 0.15 },
  { id: 'STRATEGIC_ALIGNMENT', label: 'Strategic Alignment', weight: 0.15 },
  { id: 'CULTURAL_FIT', label: 'Cultural Fit', weight: 0.15 },
];

/**
 * Generate fake data for testing
 */
export class FakeDataGenerator {
  constructor(seed = 42) {
    this.rng = new SeededRandom(seed);
    this.usedNames = new Set();
  }

  generateCompanyName() {
    let name;
    do {
      name = this.rng.choice(COMPANY_PREFIXES) + this.rng.choice(COMPANY_SUFFIXES);
    } while (this.usedNames.has(name));
    this.usedNames.add(name);
    return name;
  }

  /**
   * Generate fake scenario (from discovery chat)
   */
  generateScenario() {
    return {
      startup_name: 'InnovateTech AI',
      description: 'We are developing an AI-powered healthcare platform that uses machine learning to improve patient diagnosis and treatment recommendations.',
      industry: 'Healthcare & Biotech',
      investment_stage: 'Series A',
      product_stage: 'Beta',
      partner_needs: 'Looking for strategic partners with healthcare expertise, established distribution networks, and complementary technology platforms to accelerate market entry.',
      keywords: ['AI', 'healthcare', 'machine learning', 'diagnostics', 'enterprise'],
      use_csv: true,
      use_web_search: true,
    };
  }

  /**
   * Generate fake chat history
   */
  generateChatHistory() {
    return [
      {
        role: 'assistant',
        content: "Hello! I'm here to help you find the perfect partner for your startup. Tell me about your company and what kind of partnerships you're looking for.",
      },
      {
        role: 'user',
        content: "We're building an AI healthcare platform and looking for partners with healthcare distribution networks.",
      },
      {
        role: 'assistant',
        content: "That's exciting! An AI healthcare platform with distribution partner needs. Can you tell me more about your current stage and specific partnership goals?",
      },
      {
        role: 'user',
        content: "We're Series A funded, have a working beta product. We need partners who can help us reach hospitals and clinics.",
      },
      {
        role: 'assistant',
        content: "Got it! I'll help you find healthcare distribution partners. Let me generate a profile based on what you've shared.",
      },
    ];
  }

  /**
   * Generate a single fake candidate
   */
  generateCandidate(index) {
    const name = this.generateCompanyName();
    const industry = this.rng.choice(INDUSTRIES);
    const location = this.rng.choice(LOCATIONS);
    const size = this.rng.choice(COMPANY_SIZES);
    const fundingAmount = this.rng.randInt(1, 500);
    const matchScore = this.rng.randInt(70, 98);

    return {
      id: `candidate_${index + 1}`,
      company_name: name,
      name: name,
      website: `https://www.${name.toLowerCase().replace(/\s/g, '')}.com`,
      industry: industry,
      location: location,
      size: size,
      description: `${name} is a leading provider of innovative solutions in ${industry}.`,
      funding_total: `$${fundingAmount}M`,
      founded_year: this.rng.randInt(2000, 2023),
      employees: this.rng.randInt(10, 5000),
      source: this.rng.choice(['CrunchBase CSV', 'AI Web Search', 'LinkedIn']),
      match_score: matchScore,
      rationale: `Strong alignment with your healthcare AI needs. ${name} has extensive experience in ${industry} and complementary technology platforms.`,
      key_strengths: this.rng.sample(STRENGTH_TEMPLATES, 3).map(s =>
        s.replace('{industry}', industry).replace('{funding}', `$${fundingAmount}M`)
      ),
      potential_concerns: this.rng.sample(WEAKNESS_TEMPLATES, 2),
      recommended_action: 'Schedule introductory call to discuss partnership structure',
      company_info: {
        website: `https://www.${name.toLowerCase().replace(/\s/g, '')}.com`,
        industry: industry,
        location: location,
        size: size,
        funding_total: `$${fundingAmount}M`,
        founded_year: this.rng.randInt(2000, 2023),
      },
    };
  }

  /**
   * Generate fake search results
   */
  generateResults(count = 10) {
    const matches = Array.from({ length: count }, (_, i) => this.generateCandidate(i));

    // Sort by match score descending
    matches.sort((a, b) => b.match_score - a.match_score);

    return {
      matches: matches,
      total_matches: count,
      search_metadata: {
        sources_searched: ['CrunchBase CSV', 'AI Web Search'],
        total_considered: count * 5,
        search_time_ms: this.rng.randInt(2000, 5000),
      },
      cost: {
        total_cost: 0.05,
        input_tokens: 1500,
        output_tokens: 2000,
        web_search_calls: 3,
      },
    };
  }

  /**
   * Generate fake evaluation strategy
   */
  generateStrategy(numCandidates = 10) {
    const selectedDimensions = this.rng.sample(DIMENSIONS, 5);

    // Normalize weights to sum to 1.0
    const totalWeight = selectedDimensions.reduce((sum, d) => sum + d.weight, 0);
    const normalizedDimensions = selectedDimensions.map((d, i) => ({
      dimension: d.id,
      dimension_label: d.label,
      weight: Math.round((d.weight / totalWeight) * 100) / 100,
      priority: i + 1,
      rationale: `Critical for evaluating ${d.label.toLowerCase()} alignment`,
      description: `Assesses the ${d.label.toLowerCase()} between your startup and potential partners`,
    }));

    return {
      dimensions: normalizedDimensions,
      total_candidates: numCandidates,
      top_k: Math.min(5, numCandidates),
      exclusion_criteria: ['Direct competitors', 'Companies with poor financial health'],
      inclusion_criteria: ['Established market presence', 'Complementary technology'],
      confirmed_by_user: true,
    };
  }

  /**
   * Generate fake dimension score for a candidate
   */
  generateDimensionScore(dimension, rankAdjustment = 0) {
    const baseScore = this.rng.randInt(60 + rankAdjustment, 95 - Math.max(0, rankAdjustment - 10));

    return {
      dimension: dimension.dimension || dimension.id,
      dimension_label: dimension.dimension_label || dimension.label,
      score: baseScore,
      confidence: Math.round(this.rng.random() * 0.25 + 0.70, 2),
      evidence: [
        `Strong indicator in ${dimension.dimension_label || dimension.label}`,
        `Positive market signals observed`,
        `Complementary capabilities identified`,
      ],
      reasoning: `Based on available data, the candidate shows ${baseScore >= 75 ? 'strong' : 'moderate'} performance in ${dimension.dimension_label || dimension.label}.`,
      data_sources: ['Company website', 'Industry reports', 'Public filings'],
    };
  }

  /**
   * Generate fake candidate evaluation
   */
  generateCandidateEvaluation(candidate, strategy, rank) {
    const rankAdjustment = Math.max(0, (10 - rank) * 3);
    const dimensionScores = strategy.dimensions.map(dim =>
      this.generateDimensionScore(dim, rankAdjustment)
    );

    // Calculate weighted final score
    let weightedSum = 0;
    let totalWeight = 0;
    dimensionScores.forEach((score, i) => {
      const weight = strategy.dimensions[i].weight;
      weightedSum += score.score * weight * score.confidence;
      totalWeight += weight * score.confidence;
    });
    const finalScore = Math.round(weightedSum / totalWeight * 10) / 10;

    return {
      candidate_id: candidate.id,
      candidate_name: candidate.company_name || candidate.name,
      candidate_info: candidate,
      dimension_scores: dimensionScores,
      final_score: finalScore,
      rank: rank,
      strengths: this.rng.sample(STRENGTH_TEMPLATES, 3).map(s =>
        s.replace('{industry}', candidate.industry).replace('{funding}', candidate.funding_total)
      ),
      weaknesses: this.rng.sample(WEAKNESS_TEMPLATES, 2),
      recommendations: [
        'Schedule introductory call to discuss partnership structure',
        'Request detailed technical documentation for integration assessment',
        'Explore joint go-to-market opportunities',
      ],
      flags: rank > 3 ? ['Requires further due diligence'] : [],
    };
  }

  /**
   * Generate complete fake evaluation result
   */
  generateEvaluationResult(candidates, strategy = null) {
    if (!strategy) {
      strategy = this.generateStrategy(candidates.length);
    }

    // Generate evaluations and sort by score
    const evaluations = candidates.map((candidate, i) =>
      this.generateCandidateEvaluation(candidate, strategy, i + 1)
    );

    evaluations.sort((a, b) => b.final_score - a.final_score);

    // Reassign ranks after sorting
    evaluations.forEach((e, i) => {
      e.rank = i + 1;
    });

    const topCandidates = evaluations.slice(0, strategy.top_k);
    const avgScore = Math.round(evaluations.reduce((sum, e) => sum + e.final_score, 0) / evaluations.length * 10) / 10;

    return {
      strategy: strategy,
      evaluations: evaluations,
      total_evaluated: evaluations.length,
      top_candidates: topCandidates,
      summary: `Evaluation complete. Top candidates are ${topCandidates.slice(0, 3).map(c => c.candidate_name).join(', ')}. All candidates show strong potential for partnership with varying strengths across different evaluation dimensions.`,
      insights: [
        `Average candidate score: ${avgScore}/100`,
        `Top performer scores ${topCandidates[0]?.final_score || 0} with particular strength in key dimensions`,
        'Market compatibility and strategic alignment emerged as differentiating factors',
        `${evaluations.filter(e => e.final_score >= 75).length} candidates show strong partnership potential (score >= 75)`,
      ],
      conflicts_resolved: [],
      evaluation_metadata: {
        generated_at: new Date().toISOString(),
        debug_mode: true,
      },
    };
  }

  /**
   * Generate all fake data needed for any page
   */
  generateAllData(candidatesCount = 10) {
    const scenario = this.generateScenario();
    const chatHistory = this.generateChatHistory();
    const results = this.generateResults(candidatesCount);
    const strategy = this.generateStrategy(candidatesCount);
    const evaluationResult = this.generateEvaluationResult(results.matches, strategy);

    return {
      scenario,
      chatHistory,
      results,
      strategy,
      evaluationResult,
      startupProfile: {
        name: scenario.startup_name,
        industry: scenario.industry,
        stage: scenario.investment_stage,
        partner_needs: scenario.partner_needs,
        description: scenario.description,
      },
      candidates: results.matches,
    };
  }
}

// Default generator instance
let defaultGenerator = null;

/**
 * Get or create default generator
 */
export const getGenerator = (seed = 42) => {
  if (!defaultGenerator || defaultGenerator.rng.seed !== seed) {
    defaultGenerator = new FakeDataGenerator(seed);
  }
  return defaultGenerator;
};

/**
 * Generate all fake data with default settings
 */
export const generateFakeData = (candidatesCount = 10, seed = 42) => {
  const generator = new FakeDataGenerator(seed);
  return generator.generateAllData(candidatesCount);
};
