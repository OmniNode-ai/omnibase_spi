"""Base node protocol for all ONEX nodes."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolNode(Protocol):
    """
    Base protocol for all nodes.

    Provides identity and type metadata; execution behavior is
    defined in specialized sub-interfaces (compute, effect, etc.).

    Stability:
        Stable - No breaking changes expected within minor versions.

    .. versionadded:: 0.3.0
    """

    @property
    def node_id(self) -> str:
        """Globally unique node identifier (e.g., 'vectorization.v1')."""
        ...

    @property
    def node_type(self) -> str:
        """
        Node type classification.

        Recommended values: 'compute', 'effect', 'reducer', 'orchestrator'.
        """
        ...

    @property
    def version(self) -> str:
        """Semantic version of this node implementation."""
        ...
