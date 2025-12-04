"""
Agent and AI types for ONEX SPI.

This module provides protocol interfaces for agent actions, AI execution metrics,
debug intelligence, and related analytics types.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolAgentAction(Protocol):
    """Protocol for agent action definitions."""

    @property
    def action_id(self) -> str:
        """Action identifier."""
        ...

    @property
    def action_type(self) -> str:
        """Type of action."""
        ...

    @property
    def parameters(self) -> dict[str, ContextValue]:
        """Action parameters."""
        ...

    @property
    def timeout_ms(self) -> int:
        """Timeout in milliseconds."""
        ...

    @property
    def retry_count(self) -> int:
        """Retry count."""
        ...

    @property
    def required_capabilities(self) -> list[str]:
        """Required capabilities."""
        ...


@runtime_checkable
class ProtocolAIExecutionMetrics(Protocol):
    """Protocol for AI execution metrics."""

    @property
    def execution_id(self) -> UUID:
        """Execution identifier."""
        ...

    @property
    def model_name(self) -> str:
        """Model used."""
        ...

    async def input_tokens(self) -> int:
        """Input token count."""
        ...

    async def output_tokens(self) -> int:
        """Output token count."""
        ...

    @property
    def execution_time_ms(self) -> int:
        """Execution time."""
        ...

    @property
    def cost_estimate_usd(self) -> float:
        """Cost estimate in USD."""
        ...

    @property
    def success(self) -> bool:
        """Execution success status."""
        ...


@runtime_checkable
class ProtocolAgentDebugIntelligence(Protocol):
    """Protocol for agent debug intelligence."""

    @property
    def session_id(self) -> UUID:
        """Session identifier."""
        ...

    @property
    def agent_name(self) -> str:
        """Agent name."""
        ...

    @property
    def debug_data(self) -> dict[str, ContextValue]:
        """Debug data."""
        ...

    @property
    def performance_metrics(self) -> "ProtocolAIExecutionMetrics":
        """Performance metrics."""
        ...

    @property
    def error_logs(self) -> list[str]:
        """Error logs if any."""
        ...

    @property
    def suggestions(self) -> list[str]:
        """Debug suggestions."""
        ...


@runtime_checkable
class ProtocolPRTicket(Protocol):
    """Protocol for PR tickets."""

    @property
    def ticket_id(self) -> str:
        """Ticket identifier."""
        ...

    @property
    def title(self) -> str:
        """Ticket title."""
        ...

    @property
    def description(self) -> str:
        """Ticket description."""
        ...

    @property
    def priority(self) -> str:
        """Priority level."""
        ...

    @property
    def status(self) -> str:
        """Current status."""
        ...

    @property
    def assignee(self) -> str:
        """Assigned person."""
        ...


@runtime_checkable
class ProtocolVelocityLog(Protocol):
    """Protocol for velocity logs."""

    @property
    def log_id(self) -> UUID:
        """Log identifier."""
        ...

    @property
    def timestamp(self) -> str:
        """Log timestamp."""
        ...

    @property
    def metric_name(self) -> str:
        """Metric name."""
        ...

    @property
    def value(self) -> float:
        """Metric value."""
        ...

    @property
    def unit(self) -> str:
        """Metric unit."""
        ...

    @property
    def tags(self) -> list[str]:
        """Metric tags."""
        ...


@runtime_checkable
class ProtocolIntelligenceResult(Protocol):
    """Protocol for intelligence analysis results."""

    @property
    def analysis_id(self) -> UUID:
        """Analysis identifier."""
        ...

    @property
    def confidence_score(self) -> float:
        """Confidence score."""
        ...

    @property
    def entities(self) -> list[dict[str, ContextValue]]:
        """Extracted entities."""
        ...

    @property
    def sentiment_score(self) -> float | None:
        """Sentiment analysis if available."""
        ...

    @property
    def language_detected(self) -> str | None:
        """Detected language."""
        ...

    @property
    def processing_metadata(self) -> dict[str, ContextValue]:
        """Processing metadata."""
        ...


# Type aliases for common literal types
LiteralActionType = str  # Would be a Literal in full implementation
