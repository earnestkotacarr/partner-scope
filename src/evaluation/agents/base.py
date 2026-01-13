"""
Base Agent class for the evaluation framework.

All agents inherit from this base class which provides common functionality
for LLM interaction, logging, and cost tracking.
"""

import os
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI

from ...debug import DebugConfig


@dataclass
class AgentResponse:
    """Standard response structure from an agent."""

    success: bool
    data: Dict[str, Any]
    message: str = ""
    reasoning: str = ""
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all evaluation agents.

    Provides common functionality for:
    - LLM API interaction
    - Response parsing
    - Logging
    - Cost tracking
    """

    def __init__(
        self,
        name: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = logging.getLogger(f"evaluation.agents.{name}")

        # Initialize OpenAI client (only if not in debug mode)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        elif not DebugConfig.is_enabled():
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        else:
            self.client = None
            self.logger.info(f"Agent {name} initialized in debug mode (no OpenAI client)")

        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Debug mode flag
        self._debug_mode = DebugConfig.is_enabled()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    async def execute(self, *args, **kwargs) -> AgentResponse:
        """Execute the agent's main task."""
        pass

    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, str]] = None,
    ) -> tuple[str, int, int]:
        """
        Make a call to the LLM and return the response.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            response_format: Optional response format specification

        Returns:
            Tuple of (response_content, input_tokens, output_tokens)
        """
        # Check if we should use debug mode
        if self._debug_mode and DebugConfig.should_skip_llm(self._get_agent_type()):
            return self._call_llm_debug(messages)

        if self.client is None:
            raise ValueError("OpenAI client not initialized. Set OPENAI_API_KEY or enable debug mode.")

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

            self.logger.debug(
                f"LLM call completed: {input_tokens} input, {output_tokens} output tokens"
            )

            return content, input_tokens, output_tokens

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    def _get_agent_type(self) -> str:
        """Get the agent type for debug mode checking."""
        if "planner" in self.name:
            return "planner"
        elif "specialized" in self.name:
            return "specialized"
        elif "supervisor" in self.name:
            return "supervisor"
        return "unknown"

    def _call_llm_debug(
        self,
        messages: List[Dict[str, str]],
    ) -> tuple[str, int, int]:
        """
        Simulate an LLM call in debug mode.

        Returns fake but realistic response data.
        """
        agent_type = self._get_agent_type()
        DebugConfig.log(f"Debug mode: Simulating LLM call for {agent_type} agent")

        # Simulate delay if configured
        delay_ms = DebugConfig.get_delay_ms(agent_type)
        if delay_ms > 0:
            time.sleep(delay_ms / 1000)

        # Generate fake response based on agent type
        fake_response = self._generate_debug_response(messages)

        # Simulate token usage
        fake_input_tokens = sum(len(m.get("content", "")) for m in messages) // 4
        fake_output_tokens = len(fake_response) // 4

        self.total_input_tokens += fake_input_tokens
        self.total_output_tokens += fake_output_tokens

        self.logger.debug(
            f"Debug LLM call: {fake_input_tokens} input, {fake_output_tokens} output tokens (simulated)"
        )

        return fake_response, fake_input_tokens, fake_output_tokens

    def _generate_debug_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a debug response based on agent type.

        Subclasses should override this for more specific fake responses.
        """
        from ...debug import FakeDataGenerator

        agent_type = self._get_agent_type()
        generator = FakeDataGenerator()

        if agent_type == "planner":
            # Generate fake strategy
            strategy = generator.generate_strategy(num_candidates=10)
            return json.dumps({
                "dimensions": [
                    {
                        "dimension": dw.dimension.value,
                        "weight": dw.weight,
                        "priority": dw.priority,
                        "rationale": dw.rationale,
                    }
                    for dw in strategy.dimensions
                ],
                "reasoning": "Debug mode: Auto-generated strategy based on startup profile",
                "summary": "Strategy generated in debug mode",
                "recommended_focus": ["market_compatibility", "strategic_alignment"],
                "exclusion_criteria": strategy.exclusion_criteria,
                "explanation": "This strategy was automatically generated in debug mode for testing purposes.",
            })

        elif agent_type == "specialized":
            # Generate fake evaluation scores
            candidates = generator.generate_candidates(count=5)
            evaluations = []
            for i, candidate in enumerate(candidates):
                score = generator.generate_dimension_score(
                    dimension=self._get_dimension() if hasattr(self, '_get_dimension') else None,
                    score_range=(60, 95),
                )
                evaluations.append({
                    "candidate_id": candidate.get("id"),
                    "candidate_name": candidate.get("name"),
                    "score": score.score,
                    "confidence": score.confidence,
                    "evidence": score.evidence,
                    "reasoning": score.reasoning,
                    "data_sources": score.data_sources,
                })
            return json.dumps({
                "evaluations": evaluations,
                "summary": "Debug mode: Evaluation completed with simulated scores",
                "top_performers": [e["candidate_name"] for e in evaluations[:3]],
                "overall_reasoning": "Scores generated in debug mode for testing",
            })

        elif agent_type == "supervisor":
            # Generate fake aggregation result
            return json.dumps({
                "summary": "Debug mode: Aggregation completed with simulated results",
                "top_candidates_analysis": [
                    {
                        "candidate_id": f"candidate_{i}",
                        "candidate_name": f"Company {i}",
                        "strengths": ["Strong market presence", "Proven track record"],
                        "weaknesses": ["Limited geographic coverage"],
                        "recommendations": ["Schedule introductory call"],
                        "flags": [],
                    }
                    for i in range(1, 4)
                ],
                "conflicts_resolved": [
                    {
                        "candidate": "Company 1",
                        "conflict": "High financial score vs lower cultural fit",
                        "resolution": "Weighted average applied based on strategy priorities",
                    }
                ],
                "insights": [
                    "Debug mode: Insights generated for testing",
                    "Top candidates show strong partnership potential",
                ],
                "reasoning": "Results aggregated in debug mode",
            })

        # Default response
        return json.dumps({
            "success": True,
            "message": "Debug response generated",
            "debug_mode": True,
        })

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse a JSON response from the LLM.

        Handles various formats including markdown code blocks.
        """
        # Try direct JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass

        # Try extracting from generic code block
        if "```" in response:
            start = response.find("```") + 3
            # Skip language identifier if present
            newline = response.find("\n", start)
            if newline > start:
                start = newline + 1
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass

        # Try finding JSON object in response
        brace_start = response.find("{")
        brace_end = response.rfind("}") + 1
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(response[brace_start:brace_end])
            except json.JSONDecodeError:
                pass

        self.logger.warning(f"Failed to parse JSON response: {response[:200]}...")
        return {}

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as a readable string for prompts."""
        lines = []
        for key, value in context.items():
            if isinstance(value, list):
                if value:
                    lines.append(f"{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"  - {json.dumps(item)}")
                        else:
                            lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def get_token_usage(self) -> Dict[str, int]:
        """Get the total token usage for this agent."""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
        }

    def reset_token_usage(self):
        """Reset the token usage counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0