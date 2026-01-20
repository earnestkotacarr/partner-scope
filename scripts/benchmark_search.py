#!/usr/bin/env python3
"""
Benchmark Script for Search Optimization

============================================================================
USAGE
============================================================================

    # Run on training scenarios (for optimization)
    python scripts/benchmark_search.py

    # Run on holdout scenarios (for final validation)
    python scripts/benchmark_search.py --holdout

    # Run a single scenario
    python scripts/benchmark_search.py --scenario healthcare

    # Use different model
    python scripts/benchmark_search.py --model gpt-4o-mini

============================================================================
WORKFLOW
============================================================================

1. Run this script to get baseline scores
2. Modify src/providers/openai_web_search.py
3. Run this script again to measure improvement
4. Repeat until scores are consistently high

============================================================================
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.providers import OpenAIWebSearchProvider
from src.chat.evaluation_assistant import EvaluationChatAssistant


# ============================================================================
# TEST SCENARIOS - Diverse startup profiles
# ============================================================================

TRAINING_SCENARIOS = [
    {
        'id': 'healthcare',
        'startup_name': 'HealthAI Solutions',
        'industry': 'Healthcare & Biotech',
        'investment_stage': 'Series A',
        'product_stage': 'Beta',
        'description': 'AI-powered diagnostic platform for early disease detection using medical imaging.',
        'partner_needs': 'Looking for healthcare distribution partners, hospital networks, and EHR integration partners to accelerate market entry.',
    },
    {
        'id': 'fintech',
        'startup_name': 'FinFlow',
        'industry': 'Fintech',
        'investment_stage': 'Seed',
        'product_stage': 'MVP',
        'description': 'Modern payment infrastructure for B2B cross-border transactions.',
        'partner_needs': 'Seeking banking partners for API integration, compliance partners, and enterprise clients in APAC region.',
    },
    {
        'id': 'saas_enterprise',
        'startup_name': 'CloudScale Analytics',
        'industry': 'Enterprise SaaS',
        'investment_stage': 'Series B',
        'product_stage': 'Growth',
        'description': 'Real-time business intelligence platform for enterprise data analytics.',
        'partner_needs': 'Looking for enterprise resellers, system integrators, and data warehouse partners.',
    },
    {
        'id': 'edtech',
        'startup_name': 'LearnSmart',
        'industry': 'EdTech',
        'investment_stage': 'Series A',
        'product_stage': 'Growth',
        'description': 'Adaptive learning platform using AI to personalize education for K-12 students.',
        'partner_needs': 'Seeking school district partnerships, content providers, and LMS integration partners.',
    },
    {
        'id': 'cleantech',
        'startup_name': 'GreenEnergy Tech',
        'industry': 'CleanTech',
        'investment_stage': 'Seed',
        'product_stage': 'Prototype',
        'description': 'Next-generation solar panel technology with 40% higher efficiency.',
        'partner_needs': 'Looking for manufacturing partners, solar installers, and utility company partnerships.',
    },
    {
        'id': 'logistics',
        'startup_name': 'FleetOptimize',
        'industry': 'Logistics & Transportation',
        'investment_stage': 'Series A',
        'product_stage': 'Beta',
        'description': 'AI-powered fleet management and route optimization for delivery companies.',
        'partner_needs': 'Seeking logistics companies, fleet operators, and telematics providers as partners.',
    },
]

# Holdout scenarios - NEVER optimize on these
HOLDOUT_SCENARIOS = [
    {
        'id': 'hardware_iot',
        'startup_name': 'SmartSense IoT',
        'industry': 'Hardware & IoT',
        'investment_stage': 'Pre-seed',
        'product_stage': 'Prototype',
        'description': 'Industrial IoT sensors for predictive maintenance in manufacturing.',
        'partner_needs': 'Looking for manufacturing partners, sensor component suppliers, and industrial customers.',
    },
    {
        'id': 'consumer_app',
        'startup_name': 'FitLife',
        'industry': 'Consumer Health',
        'investment_stage': 'Seed',
        'product_stage': 'MVP',
        'description': 'Mobile app for personalized fitness and nutrition coaching.',
        'partner_needs': 'Seeking gym partnerships, nutrition brands, and wearable device integrations.',
    },
    {
        'id': 'cybersecurity',
        'startup_name': 'SecureShield',
        'industry': 'Cybersecurity',
        'investment_stage': 'Series A',
        'product_stage': 'Beta',
        'description': 'Zero-trust security platform for enterprise cloud infrastructure.',
        'partner_needs': 'Looking for MSSP partners, cloud platform integrations, and enterprise resellers.',
    },
]


# ============================================================================
# EVALUATION HELPERS
# ============================================================================

def run_search(scenario: Dict, model: str = 'gpt-4.1') -> tuple[List[Dict], Dict]:
    """
    Run search on a scenario.

    Returns:
        (candidates, usage_info)
    """
    provider = OpenAIWebSearchProvider({'model': model})

    startup_context = {
        'startup_name': scenario['startup_name'],
        'industry': scenario['industry'],
        'description': scenario['description'],
        'investment_stage': scenario['investment_stage'],
        'product_stage': scenario['product_stage'],
        'keywords': [],
    }

    candidates = provider.search_companies(
        query=scenario['partner_needs'],
        filters={
            'max_results': 15,
            'startup_context': startup_context,
        }
    )

    usage = provider.get_last_usage()
    usage_info = usage.to_dict() if usage else {}

    return candidates, usage_info


def evaluate_candidates(candidates: List[Dict], scenario: Dict) -> List[Dict]:
    """
    Run evaluation on candidates.

    Note: EvaluationChatAssistant uses hardcoded model (gpt-4.1) to ensure
    consistent evaluation regardless of search model used.

    Returns:
        List of evaluation results with scores
    """
    if not candidates:
        return []

    # Build startup profile for evaluation
    startup_profile = {
        'name': scenario['startup_name'],
        'industry': scenario['industry'],
        'investment_stage': scenario['investment_stage'],
        'product_stage': scenario['product_stage'],
        'partner_needs': scenario['partner_needs'],
        'description': scenario['description'],
    }

    # Format candidates for evaluation
    formatted_candidates = []
    for i, c in enumerate(candidates):
        formatted_candidates.append({
            'id': str(i),
            'company_name': c.get('name', 'Unknown'),
            'company_info': {
                'name': c.get('name', ''),
                'industry': c.get('industry', ''),
                'location': c.get('location', ''),
                'description': c.get('description', ''),
                'size': c.get('size', ''),
                'website': c.get('website', ''),
            },
            'match_score': 50,  # Placeholder
            'info_score': 50,
            'rationale': c.get('how_it_helps', ''),
            'key_strengths': c.get('needs_satisfied', []),
        })

    # Initialize evaluator (uses hardcoded model for consistency)
    evaluator = EvaluationChatAssistant()

    # Run evaluation (simplified - just get scores)
    try:
        # First, get evaluation strategy
        result = evaluator.chat(
            messages=[],
            current_message='start',
            candidates=formatted_candidates,
            startup_profile=startup_profile,
        )

        if result.get('phase') == 'planning':
            # Confirm and run evaluation
            result = evaluator.chat(
                messages=result.get('messages', []),
                current_message='confirm',
                candidates=formatted_candidates,
                startup_profile=startup_profile,
                strategy=result.get('strategy'),
                action_hint='confirm',
            )

        # Extract scores from results (key is 'top_candidates' not 'candidates')
        if result.get('evaluation_result') and result['evaluation_result'].get('top_candidates'):
            return result['evaluation_result']['top_candidates']

    except Exception as e:
        print(f"    Evaluation error: {str(e)[:50]}")

    return []


def calculate_metrics(scores: List[float]) -> Dict:
    """Calculate aggregate metrics from scores."""
    if not scores:
        return {'avg': 0, 'top8_avg': 0, 'min': 0, 'max': 0, 'std': 0}

    sorted_scores = sorted(scores, reverse=True)
    top_8 = sorted_scores[:8]

    return {
        'avg': mean(scores) if scores else 0,
        'top8_avg': mean(top_8) if top_8 else 0,
        'min': min(scores) if scores else 0,
        'max': max(scores) if scores else 0,
        'std': stdev(scores) if len(scores) > 1 else 0,
    }


# ============================================================================
# MAIN BENCHMARK FUNCTION
# ============================================================================

def run_benchmark(
    scenarios: List[Dict],
    model: str = 'gpt-4.1',
    verbose: bool = True
) -> Dict:
    """
    Run benchmark on a set of scenarios.

    Returns:
        Aggregate benchmark results
    """
    all_results = []
    total_cost = 0

    print("\n" + "=" * 70)
    print("PARTNERSCOPE SEARCH BENCHMARK")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Scenarios: {len(scenarios)}")
    print("=" * 70)

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] {scenario['id']}: {scenario['startup_name']}")
        print(f"    Industry: {scenario['industry']}")
        print(f"    Need: {scenario['partner_needs'][:60]}...")

        # Run search
        print(f"    Running search...", end=" ", flush=True)
        try:
            candidates, usage = run_search(scenario, model)
            search_cost = usage.get('costs', {}).get('total', 0)
            total_cost += search_cost
            print(f"Found {len(candidates)} candidates (${search_cost:.2f})")
        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            continue

        # Run evaluation
        print(f"    Running evaluation...", end=" ", flush=True)
        try:
            eval_results = evaluate_candidates(candidates, scenario)
            scores = [r.get('final_score', 0) for r in eval_results if r.get('final_score')]
            print(f"Scored {len(scores)} candidates")
        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            scores = []

        # Calculate metrics
        metrics = calculate_metrics(scores)

        result = {
            'scenario_id': scenario['id'],
            'startup_name': scenario['startup_name'],
            'industry': scenario['industry'],
            'candidates_found': len(candidates),
            'candidates_scored': len(scores),
            'avg_score': metrics['avg'],
            'top8_avg': metrics['top8_avg'],
            'min_score': metrics['min'],
            'max_score': metrics['max'],
            'search_cost': search_cost,
        }
        all_results.append(result)

        if verbose:
            print(f"    Results: Avg={metrics['avg']:.1f}, Top-8={metrics['top8_avg']:.1f}, "
                  f"Range=[{metrics['min']:.0f}-{metrics['max']:.0f}]")

    # Aggregate results
    all_top8 = [r['top8_avg'] for r in all_results if r['top8_avg'] > 0]
    all_avg = [r['avg_score'] for r in all_results if r['avg_score'] > 0]

    aggregate = {
        'scenarios_run': len(all_results),
        'mean_top8_score': mean(all_top8) if all_top8 else 0,
        'mean_avg_score': mean(all_avg) if all_avg else 0,
        'consistency_std': stdev(all_top8) if len(all_top8) > 1 else 0,
        'total_cost': total_cost,
        'results': all_results,
    }

    # Print summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Scenarios run: {aggregate['scenarios_run']}")
    print(f"Mean Top-8 Score: {aggregate['mean_top8_score']:.1f}/100")
    print(f"Mean Avg Score: {aggregate['mean_avg_score']:.1f}/100")
    print(f"Consistency (StdDev): {aggregate['consistency_std']:.1f}")
    print(f"Total Cost: ${aggregate['total_cost']:.2f}")
    print("=" * 70)

    # Per-scenario breakdown
    print("\nPer-Scenario Results:")
    print("-" * 70)
    for r in all_results:
        print(f"  {r['scenario_id']:<15} Top-8: {r['top8_avg']:>5.1f}  "
              f"Avg: {r['avg_score']:>5.1f}  Cost: ${r['search_cost']:.2f}")
    print("-" * 70)

    return aggregate


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Benchmark PartnerScope search against evaluation criteria',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--holdout',
        action='store_true',
        help='Run on holdout scenarios (for final validation only)'
    )

    parser.add_argument(
        '--scenario',
        type=str,
        help='Run a single scenario by ID (e.g., "healthcare", "fintech")'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4.1',
        help='Model to use for search and evaluation (default: gpt-4.1)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    # Select scenarios
    if args.holdout:
        print("\n*** RUNNING HOLDOUT SCENARIOS (for validation only) ***")
        scenarios = HOLDOUT_SCENARIOS
    elif args.scenario:
        all_scenarios = TRAINING_SCENARIOS + HOLDOUT_SCENARIOS
        scenarios = [s for s in all_scenarios if s['id'] == args.scenario]
        if not scenarios:
            print(f"ERROR: Scenario '{args.scenario}' not found")
            print(f"Available: {[s['id'] for s in all_scenarios]}")
            sys.exit(1)
    else:
        scenarios = TRAINING_SCENARIOS

    # Run benchmark
    results = run_benchmark(scenarios, model=args.model)

    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        results['timestamp'] = datetime.now().isoformat()
        results['model'] = args.model
        results['is_holdout'] = args.holdout

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")

    # Exit with appropriate code
    if results['mean_top8_score'] >= 80:
        print("\n✓ SUCCESS: Top-8 score >= 80")
        sys.exit(0)
    else:
        print(f"\n⚠ NEEDS IMPROVEMENT: Top-8 score {results['mean_top8_score']:.1f} < 80")
        sys.exit(1)


if __name__ == '__main__':
    main()
