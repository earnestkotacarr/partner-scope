"""
Debug Configuration Module.

Provides global debug settings and configuration for running
the pipeline with fake data.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("debug.config")


@dataclass
class DebugSettings:
    """Settings for debug mode."""

    # Master debug switch
    enabled: bool = False

    # Stage-specific debug flags
    skip_planner_llm: bool = True  # Use fake strategy instead of LLM
    skip_specialized_llm: bool = True  # Use fake dimension scores instead of LLM
    skip_supervisor_llm: bool = True  # Use fake aggregation instead of LLM
    skip_web_search: bool = True  # Skip web search API calls
    skip_ranking_llm: bool = True  # Skip LLM ranking in pipeline

    # Timing simulation (milliseconds)
    simulate_delay: bool = False
    planner_delay_ms: int = 500
    specialized_delay_ms: int = 300
    supervisor_delay_ms: int = 400

    # Fake data configuration
    fake_candidates_count: int = 10
    fake_score_range: tuple = (60, 95)
    fake_confidence_range: tuple = (0.7, 0.95)

    # Verbose output
    verbose: bool = True


class DebugConfig:
    """
    Global debug configuration manager.

    Usage:
        # Enable debug mode
        DebugConfig.enable()

        # Check if debug mode is enabled
        if DebugConfig.is_enabled():
            ...

        # Get specific settings
        settings = DebugConfig.get_settings()

        # Customize settings
        DebugConfig.configure(skip_planner_llm=True, verbose=True)
    """

    _settings: DebugSettings = DebugSettings()
    _initialized: bool = False

    @classmethod
    def _init_from_env(cls) -> None:
        """Initialize settings from environment variables."""
        if cls._initialized:
            return

        # Check for DEBUG_MODE environment variable
        debug_env = os.getenv("DEBUG_MODE", "").lower()
        if debug_env in ("1", "true", "yes", "on"):
            cls._settings.enabled = True
            logger.info("Debug mode enabled via DEBUG_MODE environment variable")

        # Check for individual stage overrides
        if os.getenv("DEBUG_SKIP_PLANNER", "").lower() in ("1", "true"):
            cls._settings.skip_planner_llm = True

        if os.getenv("DEBUG_SKIP_SPECIALIZED", "").lower() in ("1", "true"):
            cls._settings.skip_specialized_llm = True

        if os.getenv("DEBUG_SKIP_SUPERVISOR", "").lower() in ("1", "true"):
            cls._settings.skip_supervisor_llm = True

        if os.getenv("DEBUG_SKIP_WEB_SEARCH", "").lower() in ("1", "true"):
            cls._settings.skip_web_search = True

        if os.getenv("DEBUG_VERBOSE", "").lower() in ("1", "true"):
            cls._settings.verbose = True

        cls._initialized = True

    @classmethod
    def enable(cls, **kwargs) -> None:
        """
        Enable debug mode with optional configuration.

        Args:
            **kwargs: Optional settings overrides
        """
        cls._init_from_env()
        cls._settings.enabled = True

        # Apply any custom settings
        for key, value in kwargs.items():
            if hasattr(cls._settings, key):
                setattr(cls._settings, key, value)

        if cls._settings.verbose:
            logger.info("Debug mode ENABLED")
            logger.info(f"Settings: {cls._settings}")

    @classmethod
    def disable(cls) -> None:
        """Disable debug mode."""
        cls._settings.enabled = False
        if cls._settings.verbose:
            logger.info("Debug mode DISABLED")

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if debug mode is enabled."""
        cls._init_from_env()
        return cls._settings.enabled

    @classmethod
    def get_settings(cls) -> DebugSettings:
        """Get the current debug settings."""
        cls._init_from_env()
        return cls._settings

    @classmethod
    def configure(cls, **kwargs) -> None:
        """
        Configure debug settings without enabling/disabling.

        Args:
            **kwargs: Settings to update
        """
        cls._init_from_env()
        for key, value in kwargs.items():
            if hasattr(cls._settings, key):
                setattr(cls._settings, key, value)
            else:
                logger.warning(f"Unknown debug setting: {key}")

    @classmethod
    def reset(cls) -> None:
        """Reset all settings to defaults."""
        cls._settings = DebugSettings()
        cls._initialized = False
        logger.info("Debug settings reset to defaults")

    @classmethod
    def should_skip_llm(cls, stage: str) -> bool:
        """
        Check if LLM calls should be skipped for a given stage.

        Args:
            stage: One of 'planner', 'specialized', 'supervisor', 'ranking'

        Returns:
            True if LLM calls should be skipped
        """
        if not cls.is_enabled():
            return False

        stage_map = {
            "planner": cls._settings.skip_planner_llm,
            "specialized": cls._settings.skip_specialized_llm,
            "supervisor": cls._settings.skip_supervisor_llm,
            "ranking": cls._settings.skip_ranking_llm,
        }

        return stage_map.get(stage, False)

    @classmethod
    def should_skip_web_search(cls) -> bool:
        """Check if web search should be skipped."""
        return cls.is_enabled() and cls._settings.skip_web_search

    @classmethod
    def get_delay_ms(cls, stage: str) -> int:
        """
        Get the simulated delay for a stage.

        Args:
            stage: One of 'planner', 'specialized', 'supervisor'

        Returns:
            Delay in milliseconds (0 if simulation disabled)
        """
        if not cls.is_enabled() or not cls._settings.simulate_delay:
            return 0

        delay_map = {
            "planner": cls._settings.planner_delay_ms,
            "specialized": cls._settings.specialized_delay_ms,
            "supervisor": cls._settings.supervisor_delay_ms,
        }

        return delay_map.get(stage, 0)

    @classmethod
    def log(cls, message: str, level: str = "info") -> None:
        """
        Log a debug message if verbose mode is enabled.

        Args:
            message: Message to log
            level: Log level ('debug', 'info', 'warning', 'error')
        """
        if not cls._settings.verbose:
            return

        log_func = getattr(logger, level, logger.info)
        log_func(f"[DEBUG] {message}")
