"""
Cost tracking utilities for PartnerScope.

Provides classes and functions for tracking OpenAI API costs
across different operations (chat, search, refinement).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


# OpenAI Pricing (per 1M tokens) - Standard tier as of Jan 2025
OPENAI_PRICING = {
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-4.1': {'input': 2.00, 'output': 8.00},
    'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
    'gpt-4': {'input': 30.00, 'output': 60.00},  # Legacy
}

# Web search tool cost per call
WEB_SEARCH_COST_PER_CALL = 0.01  # $0.01 per web search tool call


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = 'gpt-4o-mini',
    web_search_calls: int = 0
) -> Dict[str, float]:
    """
    Calculate the cost for an API operation.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (default: gpt-4o-mini)
        web_search_calls: Number of web search tool calls

    Returns:
        Dictionary with cost breakdown:
        {
            'input_cost': float,
            'output_cost': float,
            'web_search_cost': float,
            'total_cost': float
        }
    """
    pricing = OPENAI_PRICING.get(model, OPENAI_PRICING['gpt-4o-mini'])

    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    web_search_cost = web_search_calls * WEB_SEARCH_COST_PER_CALL
    total_cost = input_cost + output_cost + web_search_cost

    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'web_search_calls': web_search_calls,
        'web_search_cost': web_search_cost,
        'total_cost': total_cost,
        'model': model,
    }


@dataclass
class OperationCost:
    """Represents the cost of a single API operation."""

    operation: str  # "discovery_chat", "template_gen", "search", "refine"
    input_tokens: int = 0
    output_tokens: int = 0
    web_search_calls: int = 0
    model: str = 'gpt-4o-mini'
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def input_cost(self) -> float:
        """Calculate input token cost."""
        pricing = OPENAI_PRICING.get(self.model, OPENAI_PRICING['gpt-4o-mini'])
        return (self.input_tokens / 1_000_000) * pricing['input']

    @property
    def output_cost(self) -> float:
        """Calculate output token cost."""
        pricing = OPENAI_PRICING.get(self.model, OPENAI_PRICING['gpt-4o-mini'])
        return (self.output_tokens / 1_000_000) * pricing['output']

    @property
    def web_search_cost(self) -> float:
        """Calculate web search tool cost."""
        return self.web_search_calls * WEB_SEARCH_COST_PER_CALL

    @property
    def total_cost(self) -> float:
        """Calculate total cost for this operation."""
        return self.input_cost + self.output_cost + self.web_search_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'operation': self.operation,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'web_search_calls': self.web_search_calls,
            'model': self.model,
            'costs': {
                'input': self.input_cost,
                'output': self.output_cost,
                'web_search': self.web_search_cost,
                'total': self.total_cost,
            },
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
        }


@dataclass
class SessionCostTracker:
    """
    Tracks costs across multiple operations in a session.

    Usage:
        tracker = SessionCostTracker()
        tracker.add_operation(OperationCost(
            operation="discovery_chat",
            input_tokens=500,
            output_tokens=200,
        ))
        print(f"Total cost: ${tracker.total_cost:.4f}")
    """

    operations: List[OperationCost] = field(default_factory=list)
    session_id: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)

    def add_operation(self, operation: OperationCost) -> None:
        """Add an operation cost to the tracker."""
        self.operations.append(operation)

    def add_from_response(
        self,
        operation_name: str,
        response_usage,
        model: str = 'gpt-4o-mini',
        web_search_calls: int = 0,
        metadata: Dict[str, Any] = None
    ) -> OperationCost:
        """
        Add operation cost from an OpenAI response usage object.

        Args:
            operation_name: Name of the operation
            response_usage: OpenAI response.usage object
            model: Model name
            web_search_calls: Number of web search calls
            metadata: Optional metadata

        Returns:
            The created OperationCost object
        """
        op = OperationCost(
            operation=operation_name,
            input_tokens=getattr(response_usage, 'prompt_tokens', 0) or
                        getattr(response_usage, 'input_tokens', 0),
            output_tokens=getattr(response_usage, 'completion_tokens', 0) or
                         getattr(response_usage, 'output_tokens', 0),
            web_search_calls=web_search_calls,
            model=model,
            metadata=metadata or {},
        )
        self.operations.append(op)
        return op

    @property
    def total_input_tokens(self) -> int:
        """Total input tokens across all operations."""
        return sum(op.input_tokens for op in self.operations)

    @property
    def total_output_tokens(self) -> int:
        """Total output tokens across all operations."""
        return sum(op.output_tokens for op in self.operations)

    @property
    def total_tokens(self) -> int:
        """Total tokens across all operations."""
        return self.total_input_tokens + self.total_output_tokens

    @property
    def total_web_search_calls(self) -> int:
        """Total web search calls across all operations."""
        return sum(op.web_search_calls for op in self.operations)

    @property
    def total_input_cost(self) -> float:
        """Total input token cost."""
        return sum(op.input_cost for op in self.operations)

    @property
    def total_output_cost(self) -> float:
        """Total output token cost."""
        return sum(op.output_cost for op in self.operations)

    @property
    def total_web_search_cost(self) -> float:
        """Total web search cost."""
        return sum(op.web_search_cost for op in self.operations)

    @property
    def total_cost(self) -> float:
        """Total cost across all operations."""
        return sum(op.total_cost for op in self.operations)

    def get_cost_by_operation(self) -> Dict[str, float]:
        """Get cost breakdown by operation type."""
        costs = {}
        for op in self.operations:
            if op.operation not in costs:
                costs[op.operation] = 0.0
            costs[op.operation] += op.total_cost
        return costs

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat(),
            'total_operations': len(self.operations),
            'totals': {
                'input_tokens': self.total_input_tokens,
                'output_tokens': self.total_output_tokens,
                'total_tokens': self.total_tokens,
                'web_search_calls': self.total_web_search_calls,
            },
            'costs': {
                'input': self.total_input_cost,
                'output': self.total_output_cost,
                'web_search': self.total_web_search_cost,
                'total': self.total_cost,
            },
            'by_operation': self.get_cost_by_operation(),
            'operations': [op.to_dict() for op in self.operations],
        }

    def to_summary_dict(self) -> Dict[str, Any]:
        """Return a concise summary for API responses."""
        return {
            'total_cost': self.total_cost,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'web_search_calls': self.total_web_search_calls,
            'operation_count': len(self.operations),
        }

    def print_summary(self) -> None:
        """Print a formatted summary to console."""
        print("\n" + "=" * 60)
        print("SESSION COST SUMMARY")
        print("=" * 60)
        print(f"Session ID: {self.session_id or 'N/A'}")
        print(f"Started: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Operations: {len(self.operations)}")
        print("-" * 60)
        print(f"{'Category':<25} {'Count':>12} {'Cost':>12}")
        print("-" * 60)
        print(f"{'Input tokens':<25} {self.total_input_tokens:>12,} ${self.total_input_cost:>10.6f}")
        print(f"{'Output tokens':<25} {self.total_output_tokens:>12,} ${self.total_output_cost:>10.6f}")
        print(f"{'Web search calls':<25} {self.total_web_search_calls:>12} ${self.total_web_search_cost:>10.6f}")
        print("-" * 60)
        print(f"{'TOTAL':<25} {self.total_tokens:>12,} ${self.total_cost:>10.6f}")
        print("=" * 60)

        if self.operations:
            print("\nBreakdown by operation:")
            print("-" * 60)
            for op in self.operations:
                print(f"  {op.operation:<30} ${op.total_cost:.6f}")
        print("=" * 60 + "\n")
