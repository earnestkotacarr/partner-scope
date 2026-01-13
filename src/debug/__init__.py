"""
Debug Mode Module for Partner Scope.

This module provides debug mode functionality to run each stage
of the pipeline with fake/mock data, without requiring API calls.

Usage:
    from src.debug import DebugConfig, FakeDataGenerator

    # Enable debug mode
    DebugConfig.enable()

    # Generate fake data for testing
    fake_data = FakeDataGenerator()
    candidates = fake_data.generate_candidates(count=10)
    strategy = fake_data.generate_strategy()
    evaluation_result = fake_data.generate_evaluation_result(candidates)
"""

from .config import DebugConfig
from .fake_data import FakeDataGenerator

__all__ = ["DebugConfig", "FakeDataGenerator"]
