# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Domain plugin protocol for kernel-level initialization hooks.

This module defines ProtocolDomainPlugin — the core contract for domain-specific
initialization plugins in the ONEX kernel bootstrap sequence.

Moved from omnibase_infra to omnibase_spi in OMN-8550 so that multiple repos
can implement the protocol without taking a runtime dependency on omnibase_infra.
omnibase_infra re-exports all three names from its original location for
backwards compatibility.

The config and result model types live in omnibase_spi.models.domain_plugin
(not here) to satisfy SPI purity rules. They are imported under TYPE_CHECKING
only so that importing this protocol module does not transitively pull in
omnibase_spi.models (which would break the namespace-isolation CI check).

Lifecycle Hooks:
    1. should_activate() - Check if plugin should activate
    2. initialize() - Create domain-specific resources
    3. validate_handshake() - Run prerequisite checks (optional)
    4. wire_handlers() - Register handlers in the container
    5. wire_dispatchers() - Register dispatchers with MessageDispatchEngine
    6. start_consumers() - Start event consumers
    7. shutdown() - Clean up resources during kernel shutdown
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.models.domain_plugin import (
        ModelDomainPluginConfig,
        ModelDomainPluginResult,
    )


@runtime_checkable
class ProtocolDomainPlugin(Protocol):
    """Protocol for domain-specific initialization plugins.

    Domain plugins implement this protocol to hook into the kernel bootstrap
    sequence. Each plugin is responsible for initializing its domain-specific
    resources, wiring handlers, and cleaning up during shutdown.

    The protocol uses duck typing - any class that implements these methods
    can be used as a domain plugin without explicit inheritance.

    Lifecycle Order:
        1. should_activate() - Check environment/config
        2. initialize() - Create pools, connections
        3. validate_handshake() - Run prerequisite checks (optional, default pass)
        4. wire_handlers() - Register handlers in container
        5. wire_dispatchers() - Register with dispatch engine (optional)
        6. start_consumers() - Start event consumers (optional)
        7. shutdown() - Clean up during kernel shutdown

    Optional Methods:
        ``validate_handshake()`` is **not** part of this Protocol definition
        because it is optional. Plugins that implement it will be detected at
        runtime via ``hasattr()`` in the kernel.
    """

    @property
    def plugin_id(self) -> str:
        """Return unique identifier for this plugin."""
        ...

    @property
    def display_name(self) -> str:
        """Return human-readable name for this plugin."""
        ...

    def should_activate(self, config: ModelDomainPluginConfig) -> bool:
        """Check if this plugin should activate based on configuration."""
        ...

    async def initialize(
        self,
        config: ModelDomainPluginConfig,
    ) -> ModelDomainPluginResult:
        """Initialize domain-specific resources."""
        ...

    async def wire_handlers(
        self,
        config: ModelDomainPluginConfig,
    ) -> ModelDomainPluginResult:
        """Register handlers with the container."""
        ...

    async def wire_dispatchers(
        self,
        config: ModelDomainPluginConfig,
    ) -> ModelDomainPluginResult:
        """Register dispatchers with MessageDispatchEngine (optional)."""
        ...

    async def start_consumers(
        self,
        config: ModelDomainPluginConfig,
    ) -> ModelDomainPluginResult:
        """Start event consumers (optional)."""
        ...

    async def shutdown(
        self,
        config: ModelDomainPluginConfig,
    ) -> ModelDomainPluginResult:
        """Clean up domain resources during kernel shutdown.

        Shutdown Order (LIFO):
            Plugins are shut down in **reverse activation order** (Last In, First Out).

        Self-Contained Constraint:
            **CRITICAL**: Plugins MUST NOT depend on resources from other plugins
            during shutdown. Each plugin should only clean up its own resources.
        """
        ...


__all__: list[str] = [
    "ProtocolDomainPlugin",
]
