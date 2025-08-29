# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.169382'
# description: Stamped by ToolPython
# entrypoint: python://protocol_file_type_handler
# hash: f865199088b42907bcfd03147a6071a4ec1c21659e83436e8b30537c67f30d6c
# last_modified_at: '2025-05-29T14:14:00.255085+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_file_type_handler.py
# namespace: python://omnibase.protocol.protocol_file_type_handler
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4e1063a3-c759-42a8-8a3f-2d05489e0ea4
# version: 1.0.0
# === /OmniNode:Metadata ===


from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import ProtocolSemVer
from omnibase.protocols.types.file_handling_types import (
    ProtocolCanHandleResult,
    ProtocolExtractedBlock,
    ProtocolHandlerMetadata,
    ProtocolOnexResult,
    ProtocolSerializedBlock,
)


@runtime_checkable
class ProtocolStampOptions(Protocol):
    """Protocol for stamping operation options."""

    force: bool
    backup: bool
    dry_run: bool


@runtime_checkable
class ProtocolValidationOptions(Protocol):
    """Protocol for validation operation options."""

    strict: bool
    verbose: bool
    check_syntax: bool


class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type handlers in the ONEX stamper engine.
    All methods and metadata must use canonical result models per typing_and_protocols rule.
    """

    @property
    def metadata(self) -> ProtocolHandlerMetadata:
        ...

    @property
    def handler_name(self) -> str:
        ...

    @property
    def handler_version(self) -> ProtocolSemVer:
        ...

    @property
    def handler_author(self) -> str:
        ...

    @property
    def handler_description(self) -> str:
        ...

    @property
    def supported_extensions(self) -> list[str]:
        ...

    @property
    def supported_filenames(self) -> list[str]:
        ...

    @property
    def handler_priority(self) -> int:
        ...

    @property
    def requires_content_analysis(self) -> bool:
        ...

    def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult:
        ...

    def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock:
        ...

    def serialize_block(self, meta: ProtocolExtractedBlock) -> ProtocolSerializedBlock:
        ...

    def normalize_rest(self, rest: str) -> str:
        ...

    def stamp(
        self, path: Path, content: str, options: ProtocolStampOptions
    ) -> ProtocolOnexResult:
        ...

    def pre_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]:
        ...

    def post_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]:
        ...

    def validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult:
        ...
