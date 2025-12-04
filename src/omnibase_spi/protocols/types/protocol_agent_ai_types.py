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
    """
    Protocol for agent action definitions specifying executable agent operations.

    Defines an action that an AI agent can perform, including identification,
    parameters, execution constraints, and required capabilities. Used for
    agent orchestration and action dispatch.

    Attributes:
        action_id: Unique identifier for the action.
        action_type: Category or type of action (e.g., "query", "transform").
        parameters: Key-value parameters for action execution.
        timeout_ms: Maximum execution time in milliseconds.
        retry_count: Number of retry attempts on failure.
        required_capabilities: List of capabilities the agent must have.

    Example:
        ```python
        class QueryAction:
            '''Database query action for agent.'''
            @property
            def action_id(self) -> str:
                return "query-users-001"

            @property
            def action_type(self) -> str:
                return "database_query"

            @property
            def parameters(self) -> dict[str, ContextValue]:
                return {"table": "users", "limit": 100}

            @property
            def timeout_ms(self) -> int:
                return 30000

            @property
            def retry_count(self) -> int:
                return 3

            @property
            def required_capabilities(self) -> list[str]:
                return ["database_read"]

        obj = QueryAction()
        assert isinstance(obj, ProtocolAgentAction)
        ```
    """

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
    """
    Protocol for AI execution metrics tracking model invocation performance.

    Captures detailed metrics about AI model execution including token usage,
    timing, cost estimation, and success status. Essential for cost tracking,
    performance monitoring, and usage analytics.

    Attributes:
        execution_id: Unique identifier for this execution.
        model_name: Name of the AI model used.
        input_tokens: Number of input tokens processed.
        output_tokens: Number of output tokens generated.
        execution_time_ms: Total execution time in milliseconds.
        cost_estimate_usd: Estimated cost in US dollars.
        success: Whether execution completed successfully.

    Example:
        ```python
        class AIMetrics:
            '''Metrics for GPT-4 execution.'''
            @property
            def execution_id(self) -> UUID:
                return uuid4()

            @property
            def model_name(self) -> str:
                return "gpt-4-turbo"

            async def input_tokens(self) -> int:
                return 1500

            async def output_tokens(self) -> int:
                return 500

            @property
            def execution_time_ms(self) -> int:
                return 2500

            @property
            def cost_estimate_usd(self) -> float:
                return 0.045

            @property
            def success(self) -> bool:
                return True

        obj = AIMetrics()
        assert isinstance(obj, ProtocolAIExecutionMetrics)
        ```
    """

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
    """
    Protocol for agent debug intelligence providing diagnostic and debugging data.

    Aggregates debug information for an agent session including performance
    metrics, error logs, and actionable suggestions. Used for troubleshooting
    agent behavior and optimizing performance.

    Attributes:
        session_id: Unique identifier for the agent session.
        agent_name: Name of the agent being debugged.
        debug_data: Detailed debug information as key-value pairs.
        performance_metrics: Execution metrics for the session.
        error_logs: List of error messages encountered.
        suggestions: AI-generated suggestions for improvement.

    Example:
        ```python
        class DebugIntel:
            '''Debug intelligence for coding agent.'''
            @property
            def session_id(self) -> UUID:
                return uuid4()

            @property
            def agent_name(self) -> str:
                return "coding-assistant"

            @property
            def debug_data(self) -> dict[str, ContextValue]:
                return {"last_action": "code_review", "files_analyzed": 5}

            @property
            def performance_metrics(self) -> ProtocolAIExecutionMetrics:
                return metrics

            @property
            def error_logs(self) -> list[str]:
                return ["Rate limit hit at 14:32:00"]

            @property
            def suggestions(self) -> list[str]:
                return ["Consider batching requests to avoid rate limits"]

        obj = DebugIntel()
        assert isinstance(obj, ProtocolAgentDebugIntelligence)
        ```
    """

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
    """
    Protocol for PR (Pull Request) tickets tracking code review items.

    Represents a ticket or issue associated with a pull request including
    identification, description, priority, status, and assignment. Used for
    tracking PR feedback and code review items.

    Attributes:
        ticket_id: Unique identifier for the ticket.
        title: Brief title summarizing the issue.
        description: Detailed description of the issue or task.
        priority: Priority level (e.g., "critical", "high", "medium", "low").
        status: Current status (e.g., "open", "in_progress", "resolved").
        assignee: Person responsible for addressing the ticket.

    Example:
        ```python
        class PRTicketImpl:
            '''PR review ticket for security issue.'''
            @property
            def ticket_id(self) -> str:
                return "PR-123-SEC-001"

            @property
            def title(self) -> str:
                return "SQL injection vulnerability in user query"

            @property
            def description(self) -> str:
                return "The user query endpoint uses string concatenation..."

            @property
            def priority(self) -> str:
                return "critical"

            @property
            def status(self) -> str:
                return "open"

            @property
            def assignee(self) -> str:
                return "security-team"

        obj = PRTicketImpl()
        assert isinstance(obj, ProtocolPRTicket)
        ```
    """

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
    """
    Protocol for velocity logs tracking team or system performance metrics over time.

    Records individual velocity measurements including metric name, value,
    unit, timestamp, and categorization tags. Used for tracking productivity,
    throughput, and performance trends.

    Attributes:
        log_id: Unique identifier for this log entry.
        timestamp: When the measurement was recorded.
        metric_name: Name of the velocity metric.
        value: Numeric value of the measurement.
        unit: Unit of measurement (e.g., "points", "tasks", "commits").
        tags: Categorization tags for filtering and grouping.

    Example:
        ```python
        class VelocityLogImpl:
            '''Velocity log for sprint throughput.'''
            @property
            def log_id(self) -> UUID:
                return uuid4()

            @property
            def timestamp(self) -> str:
                return "2024-01-15T10:30:00Z"

            @property
            def metric_name(self) -> str:
                return "sprint_velocity"

            @property
            def value(self) -> float:
                return 42.5

            @property
            def unit(self) -> str:
                return "story_points"

            @property
            def tags(self) -> list[str]:
                return ["team-alpha", "sprint-23", "backend"]

        obj = VelocityLogImpl()
        assert isinstance(obj, ProtocolVelocityLog)
        ```
    """

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
    """
    Protocol for intelligence analysis results from AI processing pipelines.

    Captures the output of AI-powered intelligence analysis including
    entity extraction, sentiment analysis, language detection, and
    confidence scoring. Used for natural language processing, content
    analysis, and automated intelligence gathering in ONEX workflows.

    Attributes:
        analysis_id: Unique identifier for this analysis run.
        confidence_score: Overall confidence in the analysis (0.0-1.0).
        entities: List of extracted entities with their attributes.
        sentiment_score: Sentiment score (-1.0 to 1.0); None if not analyzed.
        language_detected: ISO language code of detected language; None if unknown.
        processing_metadata: Additional processing details and metrics.

    Example:
        ```python
        from uuid import uuid4

        class ContentAnalysisResult:
            @property
            def analysis_id(self) -> UUID:
                return uuid4()

            @property
            def confidence_score(self) -> float:
                return 0.92

            @property
            def entities(self) -> list[dict[str, ContextValue]]:
                return [
                    {"type": "PERSON", "text": "Alice Smith", "confidence": 0.95},
                    {"type": "ORGANIZATION", "text": "ONEX Corp", "confidence": 0.88}
                ]

            @property
            def sentiment_score(self) -> float | None:
                return 0.65  # Positive sentiment

            @property
            def language_detected(self) -> str | None:
                return "en"

            @property
            def processing_metadata(self) -> dict[str, ContextValue]:
                return {
                    "model_version": "v2.1",
                    "processing_time_ms": 245,
                    "token_count": 150
                }

        result = ContentAnalysisResult()
        assert isinstance(result, ProtocolIntelligenceResult)
        assert result.confidence_score >= 0.9
        ```
    """

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
