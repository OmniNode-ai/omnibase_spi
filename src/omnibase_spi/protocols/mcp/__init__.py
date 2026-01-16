"""
MCP (Model Context Protocol) protocols for ONEX SPI.

This module provides protocol definitions for Model Context Protocol tool registration,
coordination, and execution within the ONEX distributed system architecture.

Key Protocols:
    - ProtocolMCPRegistry: Core registry for subsystem and tool management
    - ProtocolMCPSubsystemClient: Client interface for subsystem integration
    - ProtocolMCPToolProxy: Tool execution proxy and routing
    - ProtocolMCPDiscovery: Service discovery for MCP coordination
    - ProtocolMCPValidator: Validation framework for MCP operations
    - ProtocolMCPMonitor: Health monitoring and metrics collection

Usage:
    These protocols define the contracts for implementing distributed MCP coordination
    where multiple subsystems can register their tools with a central registry and
    enable cross-subsystem tool execution and coordination.

Example Integration Pattern:
    ```python
    # Subsystem registration
    registry: "ProtocolMCPRegistry"
    client: "ProtocolMCPSubsystemClient"

    # Register subsystem and tools
    registration_id = await client.register_subsystem(
        subsystem_config, tool_definitions
)

    # Start health monitoring
    await client.start_heartbeat(interval=30)

    # Tool execution through registry
    result = await registry.execute_tool(
        tool_name="process_data",
        parameters={"input": "data"},
        correlation_id=uuid4()
)
    ```

Architecture:
    The MCP protocols support a hub-and-spoke architecture where:
    - Central MCP registry coordinates all subsystems
    - Subsystems register their tools and capabilities
    - Tool execution is proxied through the central registry
    - Health monitoring ensures system reliability
    - Service discovery enables dynamic coordination
"""

from omnibase_spi.protocols.mcp.protocol_mcp_discovery import (
    ProtocolMCPDiscovery,
    ProtocolMCPServiceDiscovery,
)
from omnibase_spi.protocols.mcp.protocol_mcp_handler import (
    ProtocolMCPHandler,
)
from omnibase_spi.protocols.mcp.protocol_mcp_monitor import (
    ProtocolMCPHealthMonitor,
    ProtocolMCPMonitor,
)
from omnibase_spi.protocols.mcp.protocol_mcp_node_adapter import (
    ProtocolMCPNodeAdapter,
)
from omnibase_spi.protocols.mcp.protocol_mcp_registry import (
    ProtocolMCPRegistry,
    ProtocolMCPRegistryAdmin,
    ProtocolMCPRegistryMetricsOperations,
)
from omnibase_spi.protocols.mcp.protocol_mcp_schema_generator import (
    ProtocolMCPSchemaGenerator,
)
from omnibase_spi.protocols.mcp.protocol_mcp_subsystem_client import (
    ProtocolMCPSubsystemClient,
    ProtocolMCPSubsystemConfig,
)
from omnibase_spi.protocols.mcp.protocol_mcp_tool_proxy import (
    ProtocolMCPToolExecutor,
    ProtocolMCPToolProxy,
    ProtocolMCPToolRouter,
)
from omnibase_spi.protocols.mcp.protocol_mcp_validator import (
    ProtocolMCPToolValidator,
    ProtocolMCPValidator,
)
from omnibase_spi.protocols.mcp.protocol_tool_discovery_service import (
    ProtocolToolDiscoveryService,
)

__all__ = [
    "ProtocolMCPDiscovery",
    "ProtocolMCPHandler",
    "ProtocolMCPHealthMonitor",
    "ProtocolMCPMonitor",
    "ProtocolMCPNodeAdapter",
    "ProtocolMCPRegistry",
    "ProtocolMCPRegistryAdmin",
    "ProtocolMCPRegistryMetricsOperations",
    "ProtocolMCPSchemaGenerator",
    "ProtocolMCPServiceDiscovery",
    "ProtocolMCPSubsystemClient",
    "ProtocolMCPSubsystemConfig",
    "ProtocolMCPToolExecutor",
    "ProtocolMCPToolProxy",
    "ProtocolMCPToolRouter",
    "ProtocolMCPToolValidator",
    "ProtocolMCPValidator",
    "ProtocolToolDiscoveryService",
]
