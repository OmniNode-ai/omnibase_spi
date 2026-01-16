"""Protocol for ONEX node metadata validation.

This module defines the interface for validators that check ONEX node metadata
conformance with comprehensive result reporting and CLI integration.
"""

from __future__ import annotations

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
    errors: list[ProtocolValidateMessageModel]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Serialize validation result to dictionary representation.

        Returns:
            Dictionary containing success status, errors list, and warnings list.

        Raises:
            SerializationError: If the result cannot be serialized to dictionary format.
        """
        ...


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

    def to_dict(self) -> dict[str, Any]:
        """Serialize validation message to dictionary representation.

        Returns:
            Dictionary containing message, severity, and location fields.

        Raises:
            SerializationError: If the message cannot be serialized to dictionary format.
        """
        ...


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

    async def get_config_value(self, key: str) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration key to look up.

        Returns:
            The configuration value associated with the key, or None if not found.

        Raises:
            ConfigurationError: If the configuration cannot be accessed.
        """
        ...


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

    async def get_option(self, key: str) -> Any:
        """Retrieve a CLI option value by key.

        Args:
            key: The option key to look up.

        Returns:
            The option value associated with the key, or None if not found.

        Raises:
            KeyError: If the option key is not valid.
            CLIError: If there's an issue accessing the CLI options.
        """
        ...


@runtime_checkable
class ProtocolValidate(ProtocolCLI, Protocol):
    """
    Protocol for validators that check ONEX node metadata conformance.

    Provides comprehensive validation of ONEX nodes including metadata
    verification, plugin discovery, and CLI integration for validation
    tool invocation.

    Attributes:
        logger: Protocol-pure logger interface for validation output and
            diagnostic messages during validation operations.

    Example:
        ```python
        class MyValidator(ProtocolValidate):
            async def validate(
                self,
                path: str,
                config: ProtocolModelMetadataConfig | None = None
            ) -> ProtocolValidateResultModel:
                ...

            async def get_validation_errors(self) -> list[ProtocolValidateMessageModel]:
                ...
        ```

    See Also:
        - ProtocolValidateResultModel: Validation result container
        - ProtocolModelMetadataConfig: Validation configuration
        - ProtocolCLI: Base CLI interface
    """

    logger: ProtocolLogger  # Protocol-pure logger interface

    async def validate_main(self, args: ProtocolCLIArgsModel) -> ProtocolOnexResult:
        """Execute the main validation workflow from CLI arguments.

        This is the primary entry point for CLI-driven validation operations.
        It parses the provided arguments, configures the validation context,
        and executes the appropriate validation workflow.

        Args:
            args: Parsed CLI arguments containing command, positional args,
                and options/flags for the validation operation.

        Returns:
            ProtocolOnexResult containing the validation outcome with status,
            any errors or warnings, and metadata about the validation run.

        Raises:
            ValidationError: If validation encounters an unrecoverable error.
            CLIError: If the CLI arguments are invalid or malformed.
        """
        ...

    async def validate(
        self,
        target: str,
        config: ProtocolModelMetadataConfig | None = None,
    ) -> ProtocolValidateResultModel:
        """Validate a target path against ONEX metadata requirements.

        Performs comprehensive validation of the specified target, checking
        for metadata conformance, naming conventions, and structural requirements.

        Args:
            target: Path to the file or directory to validate.
            config: Optional validation configuration with custom rules.
                If None, default validation rules are applied.

        Returns:
            ProtocolValidateResultModel containing success status, list of
            errors, and list of warnings from the validation operation.

        Raises:
            ValidationError: If validation cannot be performed due to
                configuration or system errors.
            FileNotFoundError: If the target path does not exist.
        """
        ...

    async def get_name(self) -> str:
        """Retrieve the unique name identifier for this validator.

        The name is used for registration, logging, and identification
        purposes within the validation framework.

        Returns:
            The unique string identifier for this validator instance.

        Raises:
            ValidatorError: If the validator name cannot be determined.
        """
        ...

    async def get_validation_errors(self) -> list[ProtocolValidateMessageModel]:
        """Retrieve all validation errors accumulated during validation.

        Returns the complete list of structured validation error messages
        collected from the most recent validation operation.

        Returns:
            List of validation message models containing error details
            including message content, severity level, and location.

        Raises:
            ValidationError: If errors cannot be retrieved from the validator state.
        """
        ...
    async def discover_plugins(self) -> list[ProtocolNodeMetadataBlock]:
        """Discover and return plugin metadata blocks supported by this validator.

        Enables dynamic test/validator scaffolding and runtime plugin contract
        enforcement. Compliant with ONEX execution model and Cursor Rule.

        Returns:
            List of ProtocolNodeMetadataBlock instances representing the
            plugins supported by this validator.

        Raises:
            PluginDiscoveryError: If plugin discovery fails due to
                configuration or filesystem errors.
            ValidationError: If discovered plugin metadata is malformed
                or does not conform to ONEX requirements.

        See Also:
            ONEX protocol spec and Cursor Rule for required fields and
            extension policy.
        """
        ...

    def validate_node(self, node: ProtocolNodeMetadataBlock) -> bool:
        """Validate a single node's metadata block synchronously.

        Performs validation of a node's metadata against ONEX requirements
        without full file system traversal. This is a synchronous operation
        for quick validation checks.

        Args:
            node: The node metadata block to validate.

        Returns:
            True if the node passes all validation checks, False otherwise.

        Raises:
            ValidationError: If the node cannot be validated due to
                malformed metadata or internal validation errors.
        """
        ...
