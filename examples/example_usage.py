"""
Example usage of the Partner Scope pipeline.

This script demonstrates how to use the pipeline with different startup scenarios.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import PartnerPipeline


def example_food_safety_startup():
    """Example: Food safety temperature tracking startup."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Food Safety Startup")
    print("="*80 + "\n")

    config = {
        'crunchbase': {'enabled': True, 'api_key': 'YOUR_API_KEY'},
        'cbinsights': {'enabled': True},
        'linkedin': {'enabled': False},
        'web_search': {'enabled': True},
        'llm': {'model': 'gpt-4', 'api_key': 'YOUR_API_KEY'},
        'work_dir': 'work',
        'results_dir': 'results',
    }

    pipeline = PartnerPipeline(config)

    results = pipeline.run(
        startup_name="TempTrack",
        investment_stage="Seed",
        product_stage="MVP",
        partner_needs="Large logistics company for pilot testing temperature tracking stickers for food safety",
        industry="Food Safety / Supply Chain",
        description="Temperature tracking stickers for food safety in logistics",
        max_results=20
    )

    print(f"\nFound {len(results)} potential partners")
    return results


def example_fintech_startup():
    """Example: Fintech payment processing startup."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Fintech Startup")
    print("="*80 + "\n")

    config = {
        'crunchbase': {'enabled': True, 'api_key': 'YOUR_API_KEY'},
        'cbinsights': {'enabled': True},
        'linkedin': {'enabled': False},
        'web_search': {'enabled': True},
        'llm': {'model': 'gpt-4', 'api_key': 'YOUR_API_KEY'},
        'work_dir': 'work',
        'results_dir': 'results',
    }

    pipeline = PartnerPipeline(config)

    results = pipeline.run(
        startup_name="PayFlow",
        investment_stage="Series A",
        product_stage="Beta",
        partner_needs="Regional banks interested in modern payment processing solutions for SMB customers",
        industry="Fintech / Payments",
        description="Modern payment processing platform for small businesses",
        max_results=20
    )

    print(f"\nFound {len(results)} potential partners")
    return results


def example_healthcare_startup():
    """Example: Healthcare IT startup."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Healthcare IT Startup")
    print("="*80 + "\n")

    config = {
        'crunchbase': {'enabled': True, 'api_key': 'YOUR_API_KEY'},
        'cbinsights': {'enabled': True},
        'linkedin': {'enabled': False},
        'web_search': {'enabled': True},
        'llm': {'model': 'gpt-4', 'api_key': 'YOUR_API_KEY'},
        'work_dir': 'work',
        'results_dir': 'results',
    }

    pipeline = PartnerPipeline(config)

    results = pipeline.run(
        startup_name="HealthTrack",
        investment_stage="Series B",
        product_stage="Launched",
        partner_needs="Hospital networks and health systems for EHR integration and deployment",
        industry="Healthcare IT",
        description="Patient engagement and EHR integration platform",
        max_results=20
    )

    print(f"\nFound {len(results)} potential partners")
    return results


if __name__ == '__main__':
    print("Partner Scope - Example Usage")
    print("="*80)
    print("\nNOTE: These examples require proper API keys in the config.")
    print("Please update the config dictionaries with your actual API keys.\n")

    # Uncomment to run examples:
    # example_food_safety_startup()
    # example_fintech_startup()
    # example_healthcare_startup()

    print("\nTo run these examples:")
    print("1. Update the config dictionaries with your API keys")
    print("2. Uncomment the example function calls at the bottom of this file")
    print("3. Run: python examples/example_usage.py")
