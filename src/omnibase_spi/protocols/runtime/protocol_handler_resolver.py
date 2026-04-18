# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Protocol for resolving handler classes to constructed instances.

The ``context`` parameter is typed ``object`` at the spi layer; concrete
implementations in omnibase_core narrow it to
``ModelHandlerResolverContext`` in their own signatures. This keeps the spi
layer free of a hard dependency on core resolver models.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolHandlerResolver(Protocol):
    """Resolves a handler class to a constructed instance or a documented skip.

    Implementations MUST use a deterministic precedence chain so identical
    inputs produce identical outputs across processes.
    """

    def resolve(self, context: object) -> object:
        """Resolve a handler from resolver context.

        Args:
            context: Opaque SPI-level resolver input context. Concrete
                implementations in omnibase_core narrow this to
                ``ModelHandlerResolverContext``.

        Returns:
            A resolved handler instance or a documented skip/result object
            (e.g. ``SKIPPED_NOT_OWNED``).

        Raises:
            Exception: Implementations may raise resolution failures
                (unresolvable class, precedence conflict, missing
                dependency, etc.).
        """
        ...
