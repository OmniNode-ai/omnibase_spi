# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Protocol for answering "is this node owned by THIS runtime host?".

Implementations compare a node name against the runtime's local ownership
set so the resolver can emit ``SKIPPED_NOT_OWNED`` for handlers that belong
to a different process.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolHandlerOwnershipQuery(Protocol):
    """Answers: does THIS runtime host the node owning this handler?"""

    def is_owned_here(self, node_name: str) -> bool: ...
