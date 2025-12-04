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


from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger

from omnibase_spi.protocols.cli.protocol_cli import ProtocolCLI
from omnibase_spi.protocols.types import ProtocolNodeMetadataBlock, ProtocolOnexResult


# Protocol interfaces for validation results
@runtime_checkable
class ProtocolValidateResultModel(Protocol):
    """
    Protocol for validation operation result models.

    Encapsulates the outcome of validation operations including
    success status, error details, warnings, and serialization
    support for result persistence and reporting.

    Attributes:
        success: Whether validation passed
        errors: List of structured validation error messages
        warnings: List of warning message strings

    Example:
        ```python
        validator: ProtocolValidate = get_validator()
        result = await validator.validate("path/to/node", config)

        if result.success:
            print("Validation passed!")
            for warning in result.warnings:
                print(f"  Warning: {warning}")
        else:
            for error in result.errors:
                print(f"  Error: {error.message} at {error.location}")

        result_dict = result.to_dict()
        ```

    See Also:
        - ProtocolValidateMessageModel: Error message structure
        - ProtocolValidate: Validation interface
    """

    success: bool
    errors: list["ProtocolValidateMessageModel"]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolValidateMessageModel(Protocol):
    """
    Protocol for validation message structure representation.

    Represents a single validation message with severity level,
    message content, and optional location information for
    precise error/warning reporting.

    Attributes:
        message: Human-readable message content
        severity: Severity level (error, warning, info)
        location: Optional location in code or file

    Example:
        ```python
        result: ProtocolValidateResultModel = await validator.validate(path)

        for error in result.errors:
            severity_icon = "ERROR" if error.severity == "error" else "WARN"
            location_str = f" at {error.location}" if error.location else ""
            print(f"[{severity_icon}] {error.message}{location_str}")

            msg_dict = error.to_dict()
        ```

    See Also:
        - ProtocolValidateResultModel: Container for messages
        - ProtocolValidate: Validation interface
    """

    message: str
    severity: str
    location: str | None

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolModelMetadataConfig(Protocol):
    """
    Protocol for metadata validation configuration models.

    Provides configuration parameters for validation operations
    including configuration file path and validation rule
    definitions for customizable validation behavior.

    Attributes:
        config_path: Path to configuration file (optional)
        validation_rules: Dictionary of validation rule definitions

    Example:
        ```python
        config = ProtocolModelMetadataConfig(
            config_path="/path/to/.onexrc",
            validation_rules={
                "require_docstrings": True,
                "max_line_length": 100,
                "naming_conventions": ["Protocol*", "Model*"]
            }
        )

        validator: ProtocolValidate = get_validator()
        result = await validator.validate("path/to/node", config)

        # Get specific config value
        max_len = await config.get_config_value("max_line_length")
        ```

    See Also:
        - ProtocolValidate: Uses this configuration
        - ProtocolValidateResultModel: Validation results
    """

    config_path: str | None
    validation_rules: dict[str, Any]

    async def get_config_value(self, key: str) -> Any: ...


@runtime_checkable
class ProtocolCLIArgsModel(Protocol):
    """
    Protocol for parsed CLI argument model representation.

    Encapsulates CLI arguments including command name, positional
    arguments, and options/flags for validation tool invocation
    through command-line interfaces.

    Attributes:
        command: Name of the command being invoked
        args: List of positional arguments
        options: Dictionary of option/flag key-value pairs

    Example:
        ```python
        # CLI args from: onex validate --strict --config .onexrc ./src
        args = ProtocolCLIArgsModel(
            command="validate",
            args=["./src"],
            options={"strict": True, "config": ".onexrc"}
        )

        validator: ProtocolValidate = get_validator()
        result = await validator.validate_main(args)

        # Access specific option
        strict_mode = await args.get_option("strict")
        ```

    See Also:
        - ProtocolValidate: CLI entry point
        - ProtocolCLI: General CLI interface
    """

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
            def validate(self, path: str, config: ProtocolModelMetadataConfig | None = None) -> ProtocolValidateResultModel:
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
        config: "ProtocolModelMetadataConfig | None" = None,
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
