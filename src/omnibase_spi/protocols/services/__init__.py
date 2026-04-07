# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Service lifecycle protocols for external service integrations.

Defines protocol contracts for ticket tracking, secret management,
and code hosting services used across the ONEX platform.
"""

from omnibase_spi.protocols.services.protocol_code_host import ProtocolCodeHost
from omnibase_spi.protocols.services.protocol_external_service import (
    ProtocolExternalService,
)
from omnibase_spi.protocols.services.protocol_secret_store import ProtocolSecretStore
from omnibase_spi.protocols.services.protocol_ticket_service import (
    ProtocolTicketService,
)

__all__ = [
    "ProtocolCodeHost",
    "ProtocolExternalService",
    "ProtocolSecretStore",
    "ProtocolTicketService",
]
