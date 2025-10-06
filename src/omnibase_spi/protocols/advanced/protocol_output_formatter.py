# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.255525'
# description: Stamped by ToolPython
# entrypoint: python://protocol_output_formatter
# hash: 3384b026a07dbf9a2d626c9dcc4b36e767f29891a9c3db380b2d32db58f475fc
# last_modified_at: '2025-05-29T14:14:00.310790+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_output_formatter.py
# namespace: python://omnibase.protocol.protocol_output_formatter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 78bc5693-1149-46fe-a1f3-0cd7c48dcb65
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import (
        ProtocolOutputData,
        ProtocolOutputFormat,
    )


@runtime_checkable
class ProtocolOutputFormatter(Protocol):
    """
    Protocol for ONEX output formatting components.

    Example:
        class MyFormatter:
            def format(self, data: ProtocolOutputData, style: ProtocolOutputFormat) -> str:
                ...
    """

    def format(
        self,
        data: "ProtocolOutputData",
        style: "ProtocolOutputFormat",
    ) -> str: ...
