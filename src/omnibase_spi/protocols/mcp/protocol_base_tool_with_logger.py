"""
Protocol for base tool with logger functionality.

Defines the interface for tools that need standardized logger resolution.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolLoggerEmitLogEvent(Protocol):
    """
    Protocol for logger emit log event functionality.

    Defines the interface for standardized log event emission with correlation tracking
    and metadata support for distributed system logging.

    Example:
        class LogEmitter(ProtocolLoggerEmitLogEvent):
            async def emit_log_event(self, event_type, message, level, metadata, timestamp, correlation_id):
                # Emit structured log event with correlation tracking
                log_entry = {
                    "event_type": event_type,
                    "message": message,
                    "level": level,
                    "metadata": metadata or {},
                    "timestamp": timestamp or datetime.utcnow().isoformat(),
                    "correlation_id": correlation_id
                }
                await self.log_sink.write(log_entry)
                return True
    """

    async def emit_log_event(
        self,
        event_type: str,
        message: str,
        level: str,
        metadata: dict[str, ContextValue] | None,
        timestamp: str | None,
        correlation_id: str | None,
    ) -> bool: ...


@runtime_checkable
class ProtocolMCPNodeRegistry(Protocol):
    """
    Protocol for node registry functionality.

    Defines the interface for dynamic node registration, discovery, and management
    in distributed systems with capability tracking and metadata support.

    Example:
        class DistributedNodeRegistry(ProtocolMCPNodeRegistry):
            async def register_node(self, node_type, node_id, capabilities, metadata):
                # Register node with type, capabilities, and metadata
                node_info = {
                    "node_type": node_type,
                    "node_id": node_id,
                    "capabilities": capabilities,
                    "metadata": metadata or {},
                    "registered_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
                await self.registry_store.set(node_id, node_info)
                return node_id

            async def get_node(self, node_id):
                # Retrieve node information by ID
                return await self.registry_store.get(node_id)

            async def list_nodes(self, node_type, status):
                # List nodes filtered by type and/or status
                nodes = await self.registry_store.scan()
                return [
                    node for node in nodes
                    if (node_type is None or node["node_type"] == node_type) and
                       (status is None or node["status"] == status)
                ]
    """

    async def register_node(
        self,
        node_type: str,
        node_id: str,
        capabilities: list[str],
        metadata: dict[str, ContextValue] | None,
    ) -> str: ...

    async def get_node(self, node_id: str) -> dict[str, ContextValue] | None: ...

    async def list_nodes(
        self,
        node_type: str | None,
        status: str | None,
    ) -> list[dict[str, ContextValue]]: ...


@runtime_checkable
class ProtocolBaseToolWithLogger(Protocol):
    """
    Protocol interface for tools with logger functionality.

    Provides standardized logger resolution interface.
    """

    registry: ProtocolMCPNodeRegistry
    node_id: str
    logger_tool: ProtocolLoggerEmitLogEvent

    def _resolve_logger_tool(self) -> ProtocolLoggerEmitLogEvent: ...
