"""Protocol for ONEX node metadata validation.

This module defines the interface for validators that check ONEX node metadata
conformance with comprehensive result reporting and CLI integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_core.types import JsonType

if TYPE_CHECKING:
    from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger

from omnibase_spi.protocols.cli.protocol_cli import ProtocolCLI
from omnibase_spi.protocols.types import ProtocolNodeMetadataBlock, ProtocolResult


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

    def to_dict(self) -> JsonType:
        """Convert the validation result to a dictionary representation.

        Serializes the result including success status, errors, and warnings
        for logging, reporting, or API responses.

        Returns:
            JSON-compatible dictionary containing 'success', 'errors',
            and 'warnings' keys with their respective values.

        Raises:
            SerializationError: If errors or warnings cannot be serialized
                to JSON-compatible format.
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

    def to_dict(self) -> JsonType:
        """Convert the validation message to a dictionary representation.

        Serializes the message including content, severity level, and
        optional location for structured logging or error reporting.

        Returns:
            JSON-compatible dictionary containing 'message', 'severity',
            and 'location' keys with their respective values.

        Raises:
            SerializationError: If message content cannot be serialized
                to JSON-compatible format.
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
    validation_rules: JsonType

    async def get_config_value(self, key: str) -> JsonType | None:
        """Retrieve a specific configuration value by key.

        Accesses the validation_rules dictionary or other configuration
        sources to return the value for the specified key.

        Args:
            key: The configuration key to look up.

        Returns:
            The configuration value for the specified key, or None if
            the key does not exist in the configuration.

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
    options: JsonType

    async def get_option(self, key: str) -> JsonType | None:
        """Retrieve a specific CLI option value by key.

        Accesses the parsed options dictionary to return the value
        for the specified option/flag key.

        Args:
            key: The option key to look up (e.g., 'strict', 'config').

        Returns:
            The option value for the specified key, or None if
            the option was not provided on the command line.

        Raises:
            KeyError: If the option key is not valid.
            CLIError: If there's an issue accessing the CLI options.
        """
        ...


@runtime_checkable
class ProtocolValidate(ProtocolCLI, Protocol):
    """
    Protocol for validators that check ONEX node metadata conformance.

    Provides a comprehensive interface for validating ONEX node metadata
    including CLI entry points, single-node validation, and plugin discovery.

    Attributes:
        logger: Protocol-pure logger interface for validation output and
            diagnostic messages during validation operations.

    Example:
        ```python
        class MyValidator(ProtocolValidate):
            async def validate(
                self,
                target: str,
                config: ProtocolModelMetadataConfig | None = None
            ) -> ProtocolValidateResultModel:
                ...

            async def get_validation_errors(self) -> list[ProtocolValidateMessageModel]:
                ...
        ```

    See Also:
        - ProtocolValidateResultModel: Validation result structure
        - ProtocolModelMetadataConfig: Validation configuration
        - ProtocolCLI: Base CLI interface
    """

    logger: ProtocolLogger

    async def validate_main(self, args: ProtocolCLIArgsModel) -> ProtocolResult:
        """Execute validation from CLI arguments.

        Main entry point for CLI-based validation, parsing the provided
        arguments and executing the appropriate validation workflow.

        Args:
            args: Parsed CLI arguments containing command, positional args,
                and options/flags for the validation operation.

        Returns:
            Result containing validation outcome, exit code, and
            any error or success messages.

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
        """Validate a target path against ONEX metadata conformance rules.

        Performs validation of the specified target (file or directory)
        using the provided configuration or default validation rules.

        Args:
            target: Path to the file or directory to validate.
            config: Optional validation configuration. If None, uses
                implementation defaults.

        Returns:
            Validation result containing success status, errors, and warnings.

        Raises:
            ValidationError: If validation cannot be performed due to
                configuration or system errors.
            FileNotFoundError: If target path does not exist.
        """
        ...

    async def get_name(self) -> str:
        """Get the name of this validator.

        Returns the human-readable name identifying this validator
        implementation for logging and reporting purposes.

        Returns:
            The validator name string.

        Raises:
            ValidatorError: If the validator name cannot be determined.
        """
        ...

    async def get_validation_errors(self) -> list[ProtocolValidateMessageModel]:
        """Get all validation errors from the last validation run.

        Returns the accumulated error messages from the most recent
        validation operation for detailed error reporting.

        Returns:
            List of validation error messages with severity and location.

        Raises:
            ValidationError: If errors cannot be retrieved from the validator state.
        """
        ...

    async def discover_plugins(self) -> list[ProtocolNodeMetadataBlock]:
        """Discover and return plugin metadata blocks supported by this validator.

        Scans for available validation plugins and returns their metadata
        blocks for dynamic test/validator scaffolding and runtime plugin
        contract enforcement.

        Returns:
            List of plugin metadata blocks describing available validation
            plugins and their capabilities.

        Raises:
            PluginDiscoveryError: If plugin discovery fails due to
                configuration or filesystem errors.
            ValidationError: If discovered plugin metadata is malformed
                or does not conform to ONEX requirements.

        Note:
            Compliant with ONEX execution model and Cursor Rule.
            See ONEX protocol spec for required fields and extension policy.
        """
        ...

    async def validate_node(self, node: ProtocolNodeMetadataBlock) -> bool:
        """Validate a single node metadata block.

        Checks whether the provided node metadata block conforms to
        ONEX metadata requirements and validation rules.

        Args:
            node: The node metadata block to validate.

        Returns:
            True if the node is valid, False otherwise.

        Raises:
            ValidationError: If the node cannot be validated due to
                malformed metadata or internal validation errors.
        """
        ...
