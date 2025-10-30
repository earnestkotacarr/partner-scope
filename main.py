#!/usr/bin/env python3
"""
Main entry point for Partner Scope pipeline.

Usage:
    python main.py --config config.yaml
"""
import argparse
import yaml
import sys
from pathlib import Path
from dotenv import load_dotenv

from src import PartnerPipeline, StartupProfile


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Partner Scope - Find and rank potential partners for startups'
    )

    # Configuration
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    # Startup information
    parser.add_argument(
        '--startup-name',
        type=str,
        required=True,
        help='Name of the startup'
    )
    parser.add_argument(
        '--investment-stage',
        type=str,
        required=True,
        help='Current investment stage (e.g., Seed, Series A, Series B)'
    )
    parser.add_argument(
        '--product-stage',
        type=str,
        required=True,
        help='Product development stage (e.g., MVP, Beta, Launched)'
    )
    parser.add_argument(
        '--partner-needs',
        type=str,
        required=True,
        help='Description of partner requirements'
    )
    parser.add_argument(
        '--industry',
        type=str,
        default='',
        help='Startup industry (optional)'
    )
    parser.add_argument(
        '--description',
        type=str,
        default='',
        help='Startup description (optional)'
    )

    # Pipeline options
    parser.add_argument(
        '--max-results',
        type=int,
        default=50,
        help='Maximum number of partners to return (default: 50)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Load configuration
    if not Path(args.config).exists():
        print(f"Error: Configuration file '{args.config}' not found.")
        print("Please copy config.yaml.template to config.yaml and configure it.")
        sys.exit(1)

    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Initialize pipeline
    try:
        pipeline = PartnerPipeline(config)
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        sys.exit(1)

    # Run pipeline
    try:
        results = pipeline.run(
            startup_name=args.startup_name,
            investment_stage=args.investment_stage,
            product_stage=args.product_stage,
            partner_needs=args.partner_needs,
            industry=args.industry,
            description=args.description,
            max_results=args.max_results
        )

        # Print summary
        print(f"\n{'='*80}")
        print(f"TOP {min(10, len(results))} MATCHES:")
        print(f"{'='*80}\n")

        for i, match in enumerate(results[:10], 1):
            print(f"{i}. {match.company_name} - Score: {match.match_score}/100")
            print(f"   {match.rationale[:150]}...")
            print(f"   Action: {match.recommended_action}\n")

        print(f"\nFull results saved to results directory.")
        print(f"Total partners found: {len(results)}")

    except Exception as e:
        print(f"Error running pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
