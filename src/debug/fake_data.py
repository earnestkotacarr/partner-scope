"""
Fake Data Generator for Debug Mode.

Generates realistic fake data for each stage of the evaluation pipeline,
allowing testing without API calls.
"""

import random
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..evaluation.models import (
    EvaluationDimension,
    DimensionWeight,
    EvaluationStrategy,
    DimensionScore,
    CandidateEvaluation,
    EvaluationResult,
    StartupProfile,
)


# Sample data for generating realistic fake companies
COMPANY_PREFIXES = [
    "Tech", "Global", "Smart", "Next", "Future", "Data", "Cloud", "Cyber",
    "Digital", "AI", "Quantum", "Bio", "Green", "Eco", "Solar", "Nano",
]

COMPANY_SUFFIXES = [
    "Corp", "Labs", "Systems", "Solutions", "Technologies", "Dynamics",
    "Innovations", "Ventures", "Partners", "Group", "Industries", "Networks",
]

INDUSTRIES = [
    "Software & Technology",
    "Healthcare & Biotech",
    "Financial Services",
    "E-commerce & Retail",
    "Manufacturing",
    "Energy & Utilities",
    "Transportation & Logistics",
    "Education & EdTech",
    "Media & Entertainment",
    "Agriculture & FoodTech",
]

LOCATIONS = [
    "San Francisco, CA",
    "New York, NY",
    "Boston, MA",
    "Austin, TX",
    "Seattle, WA",
    "Los Angeles, CA",
    "Chicago, IL",
    "Denver, CO",
    "Tokyo, Japan",
    "London, UK",
    "Berlin, Germany",
    "Singapore",
]

COMPANY_SIZES = [
    "1-10 employees",
    "11-50 employees",
    "51-200 employees",
    "201-500 employees",
    "501-1000 employees",
    "1000+ employees",
]

STRENGTH_TEMPLATES = [
    "Strong market presence in {industry}",
    "Proven track record with similar partnerships",
    "Well-funded with {funding} in recent rounds",
    "Experienced leadership team",
    "Complementary technology stack",
    "Strong geographic coverage in target markets",
    "Excellent customer retention rate",
    "Innovative product portfolio",
    "Strong R&D capabilities",
    "Established distribution network",
]

WEAKNESS_TEMPLATES = [
    "Limited experience with startups",
    "Potential cultural alignment challenges",
    "Long decision-making cycles",
    "Geographic limitations in some regions",
    "Competing priorities with other initiatives",
    "Integration complexity with legacy systems",
]

RECOMMENDATION_TEMPLATES = [
    "Schedule introductory call to discuss partnership structure",
    "Request detailed technical documentation for integration assessment",
    "Arrange site visit to understand operational capabilities",
    "Negotiate pilot program terms before full commitment",
    "Conduct due diligence on financial stability",
    "Explore joint go-to-market opportunities",
]


class FakeDataGenerator:
    """
    Generates fake data for testing the evaluation pipeline.

    Usage:
        generator = FakeDataGenerator(seed=42)  # Optional seed for reproducibility

        # Generate fake candidates
        candidates = generator.generate_candidates(count=10)

        # Generate fake startup profile
        startup = generator.generate_startup_profile()

        # Generate fake strategy
        strategy = generator.generate_strategy(num_candidates=10)

        # Generate fake evaluation result
        result = generator.generate_evaluation_result(candidates, strategy)
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the fake data generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        self.seed = seed

    def generate_company_name(self) -> str:
        """Generate a random company name."""
        prefix = random.choice(COMPANY_PREFIXES)
        suffix = random.choice(COMPANY_SUFFIXES)
        return f"{prefix}{suffix}"

    def generate_candidates(
        self,
        count: int = 10,
        industry: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a list of fake candidate companies.

        Args:
            count: Number of candidates to generate
            industry: Optional specific industry for all candidates

        Returns:
            List of candidate dictionaries
        """
        candidates = []
        used_names = set()

        for i in range(count):
            # Generate unique name
            name = self.generate_company_name()
            while name in used_names:
                name = self.generate_company_name()
            used_names.add(name)

            candidate_industry = industry or random.choice(INDUSTRIES)
            location = random.choice(LOCATIONS)
            size = random.choice(COMPANY_SIZES)

            candidate = {
                "id": f"candidate_{i + 1}",
                "name": name,
                "company_name": name,
                "website": f"https://www.{name.lower().replace(' ', '')}.com",
                "industry": candidate_industry,
                "location": location,
                "size": size,
                "description": self._generate_description(name, candidate_industry),
                "funding_total": f"${random.randint(1, 500)}M",
                "founded_year": random.randint(2000, 2023),
                "employees": self._parse_employee_count(size),
                "source": random.choice(["CrunchBase CSV", "AI Web Search", "LinkedIn"]),
                "raw_data": {
                    "crunchbase_url": f"https://crunchbase.com/organization/{name.lower().replace(' ', '-')}",
                    "linkedin_url": f"https://linkedin.com/company/{name.lower().replace(' ', '')}",
                },
            }
            candidates.append(candidate)

        return candidates

    def _generate_description(self, name: str, industry: str) -> str:
        """Generate a company description."""
        templates = [
            f"{name} is a leading provider of innovative solutions in {industry}.",
            f"Founded to revolutionize {industry}, {name} delivers cutting-edge technology.",
            f"{name} specializes in {industry} solutions for enterprise customers.",
            f"As a pioneer in {industry}, {name} serves customers worldwide.",
            f"{name} combines expertise in {industry} with advanced technology platforms.",
        ]
        return random.choice(templates)

    def _parse_employee_count(self, size: str) -> int:
        """Parse employee count from size string."""
        size_map = {
            "1-10 employees": random.randint(1, 10),
            "11-50 employees": random.randint(11, 50),
            "51-200 employees": random.randint(51, 200),
            "201-500 employees": random.randint(201, 500),
            "501-1000 employees": random.randint(501, 1000),
            "1000+ employees": random.randint(1000, 5000),
        }
        return size_map.get(size, 50)

    def generate_startup_profile(
        self,
        name: Optional[str] = None,
        industry: Optional[str] = None,
        stage: Optional[str] = None,
    ) -> StartupProfile:
        """
        Generate a fake startup profile.

        Args:
            name: Optional startup name
            industry: Optional industry
            stage: Optional investment stage

        Returns:
            StartupProfile instance
        """
        name = name or f"{random.choice(['Nova', 'Spark', 'Pulse', 'Wave', 'Flux'])} {random.choice(['AI', 'Tech', 'Labs', 'IO'])}"
        industry = industry or random.choice(INDUSTRIES)
        stage = stage or random.choice(["Seed", "Series A", "Series B"])

        return StartupProfile(
            name=name,
            industry=industry,
            stage=stage,
            tech_stack=random.sample(
                ["Python", "React", "Node.js", "AWS", "Kubernetes", "TensorFlow", "PostgreSQL"],
                k=random.randint(2, 4),
            ),
            team_size=random.randint(5, 50),
            location=random.choice(LOCATIONS),
            description=f"{name} is building next-generation solutions for {industry}.",
            partner_needs=f"Looking for strategic partners in {industry} to accelerate growth and market expansion.",
            preferred_geography=random.sample(["North America", "Europe", "Asia Pacific"], k=2),
            exclusion_criteria=["Direct competitors", "Companies with pending litigation"],
        )

    def generate_strategy(
        self,
        num_candidates: int = 10,
        num_dimensions: int = 5,
    ) -> EvaluationStrategy:
        """
        Generate a fake evaluation strategy.

        Args:
            num_candidates: Total number of candidates
            num_dimensions: Number of dimensions to include (4-6 recommended)

        Returns:
            EvaluationStrategy instance
        """
        # Select random dimensions
        all_dimensions = list(EvaluationDimension)
        selected_dimensions = random.sample(all_dimensions, min(num_dimensions, len(all_dimensions)))

        # Generate weights that sum to 1.0
        raw_weights = [random.random() for _ in selected_dimensions]
        total = sum(raw_weights)
        normalized_weights = [w / total for w in raw_weights]

        # Create dimension weights
        dimension_weights = []
        for i, (dim, weight) in enumerate(zip(selected_dimensions, normalized_weights)):
            dw = DimensionWeight(
                dimension=dim,
                weight=round(weight, 3),
                priority=i + 1,
                rationale=f"Critical for evaluating {dim.value.replace('_', ' ')} alignment",
            )
            dimension_weights.append(dw)

        # Adjust last weight to ensure sum is exactly 1.0
        current_sum = sum(dw.weight for dw in dimension_weights[:-1])
        dimension_weights[-1].weight = round(1.0 - current_sum, 3)

        return EvaluationStrategy(
            dimensions=dimension_weights,
            total_candidates=num_candidates,
            top_k=min(5, num_candidates),
            exclusion_criteria=["Direct competitors", "Companies with poor financial health"],
            inclusion_criteria=["Established market presence", "Complementary technology"],
            confirmed_by_user=True,
        )

    def generate_dimension_score(
        self,
        dimension: EvaluationDimension,
        score_range: tuple = (60, 95),
        confidence_range: tuple = (0.7, 0.95),
    ) -> DimensionScore:
        """
        Generate a fake dimension score.

        Args:
            dimension: The evaluation dimension
            score_range: Range for the score (min, max)
            confidence_range: Range for confidence (min, max)

        Returns:
            DimensionScore instance
        """
        score = round(random.uniform(*score_range), 1)
        confidence = round(random.uniform(*confidence_range), 2)

        return DimensionScore(
            dimension=dimension,
            score=score,
            confidence=confidence,
            evidence=[
                f"Evidence point 1 for {dimension.value}",
                f"Evidence point 2 for {dimension.value}",
                f"Positive indicator observed in {dimension.value}",
            ],
            reasoning=f"Based on available data, the candidate shows {'strong' if score >= 75 else 'moderate'} performance in {dimension.value.replace('_', ' ')}.",
            data_sources=["Company website", "Industry reports", "Public filings"],
        )

    def generate_candidate_evaluation(
        self,
        candidate: Dict[str, Any],
        strategy: EvaluationStrategy,
        rank: int,
        score_range: tuple = (60, 95),
    ) -> CandidateEvaluation:
        """
        Generate a fake evaluation for a candidate.

        Args:
            candidate: Candidate data dictionary
            strategy: Evaluation strategy with dimensions
            rank: Candidate rank
            score_range: Range for generating scores

        Returns:
            CandidateEvaluation instance
        """
        # Generate dimension scores
        dimension_scores = []
        weighted_sum = 0.0
        total_weight = 0.0

        for dw in strategy.dimensions:
            # Adjust score range based on rank (higher ranks get higher scores)
            rank_adjusted_range = (
                score_range[0] + (10 - rank) * 2,
                score_range[1] - (rank - 1) * 1.5,
            )
            rank_adjusted_range = (
                max(50, rank_adjusted_range[0]),
                min(98, rank_adjusted_range[1]),
            )

            dim_score = self.generate_dimension_score(
                dimension=dw.dimension,
                score_range=rank_adjusted_range,
            )
            dimension_scores.append(dim_score)
            weighted_sum += dim_score.score * dw.weight * dim_score.confidence
            total_weight += dw.weight * dim_score.confidence

        # Calculate final score
        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Generate strengths and weaknesses
        num_strengths = random.randint(2, 4)
        num_weaknesses = random.randint(1, 2)

        strengths = random.sample(STRENGTH_TEMPLATES, num_strengths)
        strengths = [s.format(
            industry=candidate.get("industry", "technology"),
            funding=candidate.get("funding_total", "$50M"),
        ) for s in strengths]

        weaknesses = random.sample(WEAKNESS_TEMPLATES, num_weaknesses)
        recommendations = random.sample(RECOMMENDATION_TEMPLATES, min(3, len(RECOMMENDATION_TEMPLATES)))

        return CandidateEvaluation(
            candidate_id=candidate.get("id", f"candidate_{rank}"),
            candidate_name=candidate.get("name", candidate.get("company_name", f"Company {rank}")),
            candidate_info=candidate,
            dimension_scores=dimension_scores,
            final_score=round(final_score, 1),
            rank=rank,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            flags=[] if rank <= 3 else ["Requires further due diligence"],
        )

    def generate_evaluation_result(
        self,
        candidates: List[Dict[str, Any]],
        strategy: Optional[EvaluationStrategy] = None,
    ) -> EvaluationResult:
        """
        Generate a complete fake evaluation result.

        Args:
            candidates: List of candidate dictionaries
            strategy: Optional evaluation strategy (generated if not provided)

        Returns:
            EvaluationResult instance
        """
        if strategy is None:
            strategy = self.generate_strategy(num_candidates=len(candidates))

        # Generate evaluations for all candidates
        evaluations = []
        for rank, candidate in enumerate(candidates, 1):
            evaluation = self.generate_candidate_evaluation(
                candidate=candidate,
                strategy=strategy,
                rank=rank,
            )
            evaluations.append(evaluation)

        # Sort by final score
        evaluations.sort(key=lambda e: e.final_score, reverse=True)

        # Reassign ranks
        for i, evaluation in enumerate(evaluations, 1):
            evaluation.rank = i

        # Get top candidates
        top_candidates = evaluations[: strategy.top_k]

        return EvaluationResult(
            strategy=strategy,
            evaluations=evaluations,
            total_evaluated=len(evaluations),
            top_candidates=top_candidates,
            summary=self._generate_summary(top_candidates),
            insights=self._generate_insights(evaluations),
            conflicts_resolved=self._generate_conflicts(evaluations[:3]),
            evaluation_metadata={
                "generated_at": datetime.now().isoformat(),
                "debug_mode": True,
                "generator_seed": self.seed,
            },
        )

    def _generate_summary(self, top_candidates: List[CandidateEvaluation]) -> str:
        """Generate an evaluation summary."""
        if not top_candidates:
            return "No candidates evaluated."

        top_names = [c.candidate_name for c in top_candidates[:3]]
        return (
            f"Evaluation complete. Top candidates are {', '.join(top_names)}. "
            f"All candidates show strong potential for partnership with varying strengths "
            f"across different evaluation dimensions."
        )

    def _generate_insights(self, evaluations: List[CandidateEvaluation]) -> List[str]:
        """Generate evaluation insights."""
        if not evaluations:
            return []

        avg_score = sum(e.final_score for e in evaluations) / len(evaluations)

        insights = [
            f"Average candidate score: {avg_score:.1f}/100",
            f"Top performer scores {evaluations[0].final_score:.1f} with particular strength in key dimensions",
            "Market compatibility and strategic alignment emerged as differentiating factors",
            f"{len([e for e in evaluations if e.final_score >= 75])} candidates show strong partnership potential (score >= 75)",
        ]

        return insights

    def _generate_conflicts(self, top_candidates: List[CandidateEvaluation]) -> List[Dict[str, Any]]:
        """Generate resolved conflict examples."""
        if len(top_candidates) < 2:
            return []

        conflicts = []
        for candidate in top_candidates[:2]:
            if len(candidate.dimension_scores) >= 2:
                scores = candidate.dimension_scores
                high_dim = max(scores, key=lambda s: s.score)
                low_dim = min(scores, key=lambda s: s.score)

                if high_dim.score - low_dim.score > 15:
                    conflicts.append({
                        "candidate": candidate.candidate_name,
                        "conflict": f"High {high_dim.dimension.value.replace('_', ' ')} ({high_dim.score}) vs lower {low_dim.dimension.value.replace('_', ' ')} ({low_dim.score})",
                        "resolution": "Weighted average applied based on strategy priorities; overall score reflects balanced assessment",
                    })

        return conflicts

    def generate_agent_response(
        self,
        agent_type: str,
        success: bool = True,
        tokens_used: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate a fake agent response.

        Args:
            agent_type: Type of agent ('planner', 'specialized', 'supervisor')
            success: Whether the operation succeeded
            tokens_used: Simulated token usage

        Returns:
            Response dictionary
        """
        return {
            "success": success,
            "message": f"{agent_type.title()} completed successfully" if success else f"{agent_type.title()} failed",
            "tokens_used": tokens_used,
            "debug_mode": True,
        }


# Convenience function for quick fake data generation
def generate_fake_evaluation_data(
    num_candidates: int = 10,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a complete set of fake evaluation data.

    Args:
        num_candidates: Number of candidates to generate
        seed: Random seed for reproducibility

    Returns:
        Dictionary containing all generated data
    """
    generator = FakeDataGenerator(seed=seed)

    startup = generator.generate_startup_profile()
    candidates = generator.generate_candidates(count=num_candidates)
    strategy = generator.generate_strategy(num_candidates=num_candidates)
    result = generator.generate_evaluation_result(candidates, strategy)

    return {
        "startup_profile": startup.to_dict(),
        "candidates": candidates,
        "strategy": strategy.to_dict(),
        "evaluation_result": result.to_dict(),
    }
