# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.306553'
# description: Stamped by ToolPython
# entrypoint: python://protocol_validate
# hash: 88bcd387819771c90df72a41a04b454ace7a2a24a936c1523ec962441e80c78c
# last_modified_at: '2025-05-29T14:14:00.395638+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_validate.py
# namespace: python://omnibase.protocol.protocol_validate
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: a79401fb-e7c9-4265-b352-dcb2e7c29717
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import TYPE_CHECKING, Any, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger

from omnibase_spi.protocols.cli.protocol_cli import ProtocolCLI
from omnibase_spi.protocols.types import ProtocolNodeMetadataBlock, ProtocolOnexResult


# Protocol interfaces for validation results
@runtime_checkable
class ProtocolValidateResultModel(Protocol):
    """Protocol for validation result models."""

    success: bool
    errors: list["ProtocolValidateMessageModel"]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolValidateMessageModel(Protocol):
    """Protocol for validation message models."""

    message: str
    severity: str
    location: Optional[str]

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolModelMetadataConfig(Protocol):
    """Protocol for metadata configuration models."""

    config_path: Optional[str]
    validation_rules: dict[str, Any]

    async def get_config_value(self, key: str) -> Any: ...


@runtime_checkable
class ProtocolCLIArgsModel(Protocol):
    """Protocol for CLI argument models."""

    command: str
    args: list[str]
    options: dict[str, Any]

    async def get_option(self, key: str) -> Any: ...


@runtime_checkable
class ProtocolValidate(ProtocolCLI, Protocol):
    """
    Protocol for validators that check ONEX node metadata conformance.

    Example:
        class MyValidator(ProtocolValidate):
            def validate(self, path: str, config: Optional[ProtocolModelMetadataConfig] = None) -> ProtocolValidateResultModel:
                ...
            def get_validation_errors(self) -> list[ProtocolValidateMessageModel]:
                ...
    """

    logger: "ProtocolLogger"  # Protocol-pure logger interface

    async def validate_main(
        self, args: "ProtocolCLIArgsModel"
    ) -> ProtocolOnexResult: ...

    async def validate(
        self,
        target: str,
        config: Optional["ProtocolModelMetadataConfig"] = None,
    ) -> ProtocolValidateResultModel: ...

    async def get_name(self) -> str: ...

    async def get_validation_errors(self) -> list[ProtocolValidateMessageModel]: ...
    async def discover_plugins(self) -> list[ProtocolNodeMetadataBlock]:
        """
        Returns a list of plugin metadata blocks supported by this validator.
            ...
        Enables dynamic test/validator scaffolding and runtime plugin contract enforcement.
        Compliant with ONEX execution model and Cursor Rule.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        ...

    def validate_node(self, node: ProtocolNodeMetadataBlock) -> bool: ...
