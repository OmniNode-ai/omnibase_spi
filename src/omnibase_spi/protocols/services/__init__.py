# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
Service lifecycle protocols for external service integrations.

Defines protocol contracts for source control, project tracking, database,
ticket tracking, Done-write receipt gating, secret management, and code hosting
services used across the ONEX platform.
"""

from omnibase_spi.protocols.services.protocol_code_host import ProtocolCodeHost
from omnibase_spi.protocols.services.protocol_database_service import (
    ProtocolDatabaseService,
)
from omnibase_spi.protocols.services.protocol_done_write_receipt_gate import (
    ProtocolDoneWriteReceiptGate,
)
from omnibase_spi.protocols.services.protocol_done_write_receipt_queries import (
    ProtocolDoneWriteReceiptQueries,
)
from omnibase_spi.protocols.services.protocol_external_service import (
    ProtocolExternalService,
)
from omnibase_spi.protocols.services.protocol_project_tracker import (
    ProtocolProjectTracker,
)
from omnibase_spi.protocols.services.protocol_secret_store import ProtocolSecretStore
from omnibase_spi.protocols.services.protocol_source_control import (
    ProtocolSourceControl,
)
from omnibase_spi.protocols.services.protocol_ticket_service import (
    ProtocolTicketService,
)

__all__ = [
    "ProtocolCodeHost",
    "ProtocolDatabaseService",
    "ProtocolDoneWriteReceiptGate",
    "ProtocolDoneWriteReceiptQueries",
    "ProtocolExternalService",
    "ProtocolProjectTracker",
    "ProtocolSecretStore",
    "ProtocolSourceControl",
    "ProtocolTicketService",
]
