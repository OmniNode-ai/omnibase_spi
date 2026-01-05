"""
Handler Contract Factory Implementation.

This module provides the HandlerContractFactory class and related utilities
for creating default handler contracts based on handler type category.

The factory pattern is used to encapsulate the complexity of loading YAML
templates and constructing validated ModelHandlerContract instances with
appropriate defaults for each handler type (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE).

Key Components:
    - HandlerContractFactory: Main factory class implementing ProtocolHandlerContractFactory
    - get_default_handler_contract: Convenience function for quick contract creation
    - Template loading utilities: Internal functions for YAML template management

Security Note:
    The YAML templates loaded by this factory are bundled with the omnibase_spi
    package and should be treated as trusted input. The templates are loaded using
    yaml.safe_load() which prevents arbitrary code execution. However, if you
    extend this factory to load templates from external sources, additional
    validation should be implemented.

Usage:
    The recommended way to use this module is via the convenience function:

    >>> from omnibase_core.enums import EnumHandlerTypeCategory
    >>> from omnibase_spi.factories import get_default_handler_contract
    >>> contract = get_default_handler_contract(
    ...     handler_type=EnumHandlerTypeCategory.COMPUTE,
    ...     handler_name="my_handler"
    ... )

    Or for more control, instantiate the factory directly:

    >>> factory = HandlerContractFactory()
    >>> contract = factory.get_default(
    ...     handler_type=EnumHandlerTypeCategory.EFFECT,
    ...     handler_name="my_effect_handler",
    ...     version="2.0.0"
    ... )

See Also:
    - ProtocolHandlerContractFactory: Protocol this factory implements
    - ModelHandlerContract: The contract model returned by this factory
    - EnumHandlerTypeCategory: Enum of supported handler types
"""

from __future__ import annotations

import copy
import functools
import importlib.resources
import re
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from omnibase_core.enums import EnumHandlerTypeCategory
from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract
from omnibase_core.models.primitives.model_semver import ModelSemVer
from omnibase_spi.exceptions import TemplateNotFoundError, TemplateParseError

# Regex pattern for validating semantic version strings.
# Matches: major.minor.patch[-prerelease][+build]
# Examples: "1.0.0", "2.1.0-alpha.1", "1.0.0+build.123", "3.0.0-beta+build.456"
_SEMVER_PATTERN = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Mapping from handler type category to their default template YAML filenames.
# These templates are located in the omnibase_spi.contracts.defaults package
# and provide production-ready default configurations for each handler type.
#
# Template files define:
#   - permissions (network, filesystem, etc.)
#   - resource limits (memory, CPU, timeout)
#   - retry policies and error handling
#   - handler-type-specific configurations
_DEFAULT_TEMPLATE_MAP: dict[EnumHandlerTypeCategory, str] = {
    EnumHandlerTypeCategory.COMPUTE: "default_compute_handler.yaml",
    EnumHandlerTypeCategory.EFFECT: "default_effect_handler.yaml",
    EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE: "default_nondeterministic_compute_handler.yaml",
}


def _validate_handler_name(handler_name: str | None) -> str:
    """Validate handler_name parameter.

    Args:
        handler_name: The handler name to validate. Must be non-None and non-empty.

    Returns:
        The validated handler_name (stripped of leading/trailing whitespace).

    Raises:
        ValueError: If handler_name is None, empty, or whitespace-only.
    """
    if handler_name is None:
        raise ValueError("handler_name cannot be None")
    if not isinstance(handler_name, str):
        raise ValueError(
            f"handler_name must be a string, got {type(handler_name).__name__}"
        )
    handler_name = handler_name.strip()
    if not handler_name:
        raise ValueError("handler_name cannot be empty or whitespace-only")
    return handler_name


def _validate_version_string(version: str) -> None:
    """Validate that a version string follows semantic versioning format.

    Args:
        version: The version string to validate.

    Raises:
        ValueError: If version string does not follow semver format.
    """
    if not _SEMVER_PATTERN.match(version):
        raise ValueError(
            f"Invalid version format: '{version}'. "
            "Version must follow semantic versioning format (e.g., '1.0.0', "
            "'2.1.0-alpha.1', '1.0.0+build.123')."
        )


def _validate_handler_type(handler_type: EnumHandlerTypeCategory | None) -> None:
    """Validate handler_type parameter.

    Args:
        handler_type: The handler type to validate.

    Raises:
        ValueError: If handler_type is None or not an EnumHandlerTypeCategory.
    """
    if handler_type is None:
        raise ValueError("handler_type cannot be None")
    if not isinstance(handler_type, EnumHandlerTypeCategory):
        raise ValueError(
            f"handler_type must be an EnumHandlerTypeCategory, "
            f"got {type(handler_type).__name__}"
        )


def _get_template_path(template_name: str) -> Path:
    """Get the path to a template file in the contracts/defaults directory.

    This function resolves the path to YAML template files bundled with the
    omnibase_spi package. It uses importlib.resources for robust path resolution
    that works both in development and when installed as a package.

    Args:
        template_name: Name of the template file (e.g., "default_compute_handler.yaml").
            Must be a filename only, not a path.

    Returns:
        Absolute Path object pointing to the template file location.

    Raises:
        TemplateNotFoundError: If the template file does not exist in the
            contracts/defaults directory.

    Example:
        >>> path = _get_template_path("default_compute_handler.yaml")
        >>> path.name
        'default_compute_handler.yaml'
        >>> path.exists()
        True

    Note:
        This is a private function intended for internal use by the factory.
        External code should use HandlerContractFactory.get_default() instead.
    """
    # Use importlib.resources for package-relative path resolution
    try:
        # Python 3.9+ style
        files = importlib.resources.files("omnibase_spi.contracts.defaults")
        template_path = files.joinpath(template_name)
        # For traversable resources, get the actual path
        if hasattr(template_path, "__fspath__"):
            return Path(str(template_path))
        # Fallback: read directly
        return Path(str(template_path))
    except (TypeError, AttributeError):
        # Fallback for edge cases where importlib.resources is not available
        package_dir = Path(__file__).parent.parent / "contracts" / "defaults"
        path = package_dir / template_name
        if not path.exists():
            raise TemplateNotFoundError(
                f"Template file not found: {template_name}",
                context={
                    "template_name": template_name,
                    "search_path": str(package_dir),
                },
            ) from None
        return path


def _load_template(template_name: str) -> dict[str, Any]:
    """Load and parse a YAML template file into a dictionary.

    This function handles the complete loading process: locating the template
    file using importlib.resources, reading its contents, and parsing the YAML
    into a Python dictionary suitable for ModelHandlerContract construction.

    The function attempts to use importlib.resources first for proper package
    resource handling, falling back to direct file path resolution if needed.

    Args:
        template_name: Name of the template file to load (e.g.,
            "default_compute_handler.yaml"). Must be a filename only,
            not a full path.

    Returns:
        Dictionary containing the parsed YAML content. The structure matches
        the ModelHandlerContract schema with keys like "handler_id", "name",
        "version", "permissions", "resources", etc.

    Raises:
        TemplateNotFoundError: If the template file does not exist in the
            contracts/defaults directory.
        TemplateParseError: If the template file contains invalid YAML syntax.

    Example:
        >>> template = _load_template("default_compute_handler.yaml")
        >>> template["permissions"]["network"]
        False
        >>> template["resources"]["max_memory_mb"]
        512

    Note:
        This is a private function intended for internal use by the factory.
        The returned dictionary is typically modified (handler_name, version)
        before being validated as a ModelHandlerContract.
    """
    content: str | None = None
    source_path: str = (
        f"importlib.resources:omnibase_spi.contracts.defaults/{template_name}"
    )

    # Try importlib.resources first (preferred for package resources)
    try:
        files = importlib.resources.files("omnibase_spi.contracts.defaults")
        template_resource = files.joinpath(template_name)
        content = template_resource.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        # Template file not found via importlib.resources
        raise TemplateNotFoundError(
            f"Template file not found: {template_name}",
            context={
                "template_name": template_name,
                "source": "importlib.resources",
                "package": "omnibase_spi.contracts.defaults",
            },
        ) from e
    except (TypeError, AttributeError):
        # importlib.resources not available or incompatible, fallback to file path
        try:
            template_path = _get_template_path(template_name)
            source_path = str(template_path)
            with open(template_path, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError as e:
            raise TemplateNotFoundError(
                f"Template file not found: {template_name}",
                context={
                    "template_name": template_name,
                    "source": "filesystem",
                    "search_path": str(
                        Path(__file__).parent.parent / "contracts" / "defaults"
                    ),
                },
            ) from e

    # Parse YAML content
    try:
        result = yaml.safe_load(content)
        if result is None:
            raise TemplateParseError(
                f"Template file is empty or contains only null: {template_name}",
                context={
                    "template_name": template_name,
                    "source_path": source_path,
                },
            )
        return cast(dict[str, Any], result)
    except yaml.YAMLError as e:
        raise TemplateParseError(
            f"Invalid YAML in template: {template_name}",
            context={
                "template_name": template_name,
                "source_path": source_path,
                "yaml_error": str(e),
            },
        ) from e


class HandlerContractFactory:
    """Factory for creating default handler contracts based on handler type.

    This class implements the ProtocolHandlerContractFactory protocol, providing
    a standardized way to create ModelHandlerContract instances with appropriate
    default configurations for different handler categories.

    The factory uses a template-based approach where default contracts are defined
    in YAML files and loaded on demand. Templates are cached after first load to
    improve performance for repeated contract creation.

    Supported Handler Types:
        - COMPUTE: Pure computational handlers with no side effects.
          Default: No network access, filesystem read-only, 512MB memory limit.

        - EFFECT: Handlers that perform I/O operations (database, API calls, etc.).
          Default: Network access enabled, filesystem read/write, 1024MB memory limit.

        - NONDETERMINISTIC_COMPUTE: AI/ML handlers that may produce different outputs.
          Default: Network access for API calls, higher memory limits, retry configuration.

    Thread Safety:
        This class is NOT thread-safe. If used in a multi-threaded environment,
        external synchronization should be applied or separate factory instances
        should be used per thread.

    Security:
        YAML templates are bundled with the package and treated as trusted input.
        Templates are loaded using yaml.safe_load() to prevent code execution.
        If extending to load external templates, implement additional validation.

    Attributes:
        _template_cache: Class-level cache mapping handler types to loaded templates.
            Shared across all instances, populated lazily on first access to each
            handler type. This design avoids __init__ methods per SPI purity rules.

    Example:
        Basic usage with different handler types:

        >>> from omnibase_core.enums import EnumHandlerTypeCategory
        >>> from omnibase_spi.factories import HandlerContractFactory
        >>>
        >>> factory = HandlerContractFactory()
        >>>
        >>> # Create a compute handler contract
        >>> compute_contract = factory.get_default(
        ...     handler_type=EnumHandlerTypeCategory.COMPUTE,
        ...     handler_name="data_transformer",
        ...     version="1.0.0"
        ... )
        >>> compute_contract.permissions.network
        False
        >>>
        >>> # Create an effect handler contract for database operations
        >>> effect_contract = factory.get_default(
        ...     handler_type=EnumHandlerTypeCategory.EFFECT,
        ...     handler_name="postgres_writer",
        ...     version="2.1.0"
        ... )
        >>> effect_contract.permissions.network
        True
        >>>
        >>> # Create an LLM handler contract
        >>> llm_contract = factory.get_default(
        ...     handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ...     handler_name="openai_completion",
        ...     version="1.0.0-beta"
        ... )

    See Also:
        - ProtocolHandlerContractFactory: The protocol this class implements.
        - ModelHandlerContract: The contract model returned by get_default().
        - get_default_handler_contract: Module-level convenience function.
    """

    # Class-level template cache for lazy initialization (shared across instances).
    # This avoids __init__ which is not allowed in SPI protocol implementations.
    # The cache is populated lazily on first access to each handler type.
    _template_cache: dict[EnumHandlerTypeCategory, dict[str, Any]] = {}

    def _get_template(self, handler_type: EnumHandlerTypeCategory) -> dict[str, Any]:
        """Retrieve the template dictionary for a handler type, using cache.

        This method provides access to the raw template data for a given handler
        type. On first access, the template is loaded from the corresponding YAML
        file and cached. Subsequent calls return a deep copy of the cached template
        to prevent accidental mutation of the cached data.

        Args:
            handler_type: The handler type category to get the template for.
                Must be one of the types returned by available_types().

        Returns:
            A deep copy of the template dictionary containing default values
            for the handler contract. The dictionary structure matches the
            ModelHandlerContract schema.

        Raises:
            ValueError: If handler_type is not one of the supported types
                (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE).
            TemplateNotFoundError: If the template file for the handler type
                cannot be found.
            TemplateParseError: If the template file contains invalid YAML.

        Example:
            >>> factory = HandlerContractFactory()
            >>> template = factory._get_template(EnumHandlerTypeCategory.COMPUTE)
            >>> template["permissions"]["network"]
            False
            >>> template["resources"]["max_memory_mb"]
            512

        Note:
            This is a private method. External code should use get_default()
            which handles template customization and Pydantic validation.
        """
        if handler_type not in _DEFAULT_TEMPLATE_MAP:
            raise ValueError(
                f"Unsupported handler type: {handler_type}. "
                f"Supported types: {list(_DEFAULT_TEMPLATE_MAP.keys())}"
            )

        if handler_type not in self._template_cache:
            template_name = _DEFAULT_TEMPLATE_MAP[handler_type]
            self._template_cache[handler_type] = _load_template(template_name)

        # Return a deep copy to prevent mutation of nested structures
        return copy.deepcopy(self._template_cache[handler_type])

    def get_default(
        self,
        handler_type: EnumHandlerTypeCategory,
        handler_name: str,
        version: ModelSemVer | str = "1.0.0",
    ) -> ModelHandlerContract:
        """Get a default handler contract for the given handler type.

        Creates a new validated ModelHandlerContract based on the default template
        for the specified handler type. The template provides safe, production-ready
        defaults that are customized with the provided handler name and version.

        The returned contract can be used directly or further customized via the
        ONEX patch system to adjust permissions, resources, or other settings
        for specific deployment environments.

        Args:
            handler_type: The category of handler determining which template to use.
                - COMPUTE: For pure computational operations (no I/O side effects)
                - EFFECT: For handlers that perform I/O (database, network, filesystem)
                - NONDETERMINISTIC_COMPUTE: For AI/ML handlers with variable outputs
            handler_name: Unique identifier for the handler. This becomes both the
                handler_id and name fields in the contract. Should follow the naming
                convention: lowercase with underscores (e.g., "my_data_transformer").
            version: Contract version as either a ModelSemVer instance or a semver
                string. Supports full semver format including prerelease and build
                metadata (e.g., "1.0.0", "2.1.0-beta.1", "1.0.0+build.123").
                Defaults to "1.0.0".

        Returns:
            A fully validated ModelHandlerContract instance with:
            - handler_id and name set to handler_name
            - version set to the provided version
            - permissions appropriate for the handler type
            - resource limits appropriate for the handler type
            - All other fields set to template defaults

        Raises:
            ValueError: If any of the following conditions are met:
                - handler_type is not one of the supported types
                  (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE)
                - handler_type is None or not an EnumHandlerTypeCategory
                - handler_name is None, empty, or whitespace-only
                - version string is malformed (e.g., "1.x.0", "invalid",
                  empty string, or doesn't follow semver format). Valid
                  formats include: "1.0.0", "2.1.0-alpha.1", "1.0.0+build.123"
            TemplateNotFoundError: If the template file for the handler type
                cannot be found in the contracts/defaults directory.
            TemplateParseError: If the template file contains invalid YAML.
            pydantic.ValidationError: If the resulting contract data fails
                Pydantic model validation (indicates a malformed template or
                invalid handler_name format for handler_id requirements).

        Example:
            Create contracts for different handler types:

            >>> from omnibase_core.enums import EnumHandlerTypeCategory
            >>> factory = HandlerContractFactory()
            >>>
            >>> # Compute handler with default version
            >>> contract = factory.get_default(
            ...     handler_type=EnumHandlerTypeCategory.COMPUTE,
            ...     handler_name="json_parser"
            ... )
            >>> contract.handler_id
            'json_parser'
            >>> contract.version
            '1.0.0'
            >>>
            >>> # Effect handler with custom version
            >>> contract = factory.get_default(
            ...     handler_type=EnumHandlerTypeCategory.EFFECT,
            ...     handler_name="s3_uploader",
            ...     version="2.3.1"
            ... )
            >>> contract.permissions.network
            True
            >>>
            >>> # Using ModelSemVer directly
            >>> from omnibase_core.models.primitives.model_semver import ModelSemVer
            >>> version = ModelSemVer(major=1, minor=0, patch=0, prerelease=("rc", "1"))
            >>> contract = factory.get_default(
            ...     handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            ...     handler_name="gpt4_completion",
            ...     version=version
            ... )
        """
        # Input validation - validate parameters before any processing
        _validate_handler_type(handler_type)
        handler_name = _validate_handler_name(handler_name)
        if isinstance(version, str):
            _validate_version_string(version)

        template = self._get_template(handler_type)

        # Convert string version to ModelSemVer if needed
        if isinstance(version, str):
            # Parse semver string: major.minor.patch[-prerelease][+build]
            # Split off build metadata first (after +)
            build = None
            if "+" in version:
                version, build = version.split("+", 1)

            # Split off prerelease (after -)
            prerelease = None
            if "-" in version:
                version_base, prerelease = version.split("-", 1)
            else:
                version_base = version

            # Parse major.minor.patch
            parts = version_base.split(".")
            version_obj = ModelSemVer(
                major=int(parts[0]) if len(parts) > 0 else 1,
                minor=int(parts[1]) if len(parts) > 1 else 0,
                patch=int(parts[2]) if len(parts) > 2 else 0,
                prerelease=tuple(prerelease.split(".")) if prerelease else None,
                build=tuple(build.split(".")) if build else None,
            )
        else:
            version_obj = version

        # Override with provided values
        template["handler_id"] = handler_name
        template["name"] = handler_name
        # Use string representation for the template
        template["version"] = str(version_obj)

        return ModelHandlerContract.model_validate(template)

    def available_types(self) -> list[EnumHandlerTypeCategory]:
        """Return the list of handler types this factory supports.

        This method provides discovery of which handler type categories have
        default templates available. Use this to validate handler types before
        calling get_default() or to display available options to users.

        Returns:
            A list of EnumHandlerTypeCategory values for which default templates
            exist. Currently includes:
            - EnumHandlerTypeCategory.COMPUTE
            - EnumHandlerTypeCategory.EFFECT
            - EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE

        Example:
            >>> factory = HandlerContractFactory()
            >>> types = factory.available_types()
            >>> EnumHandlerTypeCategory.COMPUTE in types
            True
            >>> EnumHandlerTypeCategory.EFFECT in types
            True
            >>> len(types)
            3
            >>>
            >>> # Use for validation before creating a contract
            >>> handler_type = EnumHandlerTypeCategory.COMPUTE
            >>> if handler_type in factory.available_types():
            ...     contract = factory.get_default(handler_type, "my_handler")

        Note:
            The returned list order is not guaranteed. If you need consistent
            ordering, sort the result.

            This method never raises exceptions. The list of supported types
            is determined at module load time from the _DEFAULT_TEMPLATE_MAP
            constant and is always available.
        """
        return list(_DEFAULT_TEMPLATE_MAP.keys())


@functools.lru_cache(maxsize=1)
def _get_cached_factory() -> HandlerContractFactory:
    """Get a cached singleton factory instance.

    This function returns a module-level cached HandlerContractFactory instance,
    ensuring that repeated calls to get_default_handler_contract() benefit from
    template caching without creating new factory instances.

    The factory is cached using lru_cache, making it thread-safe for reads and
    ensuring only one factory instance exists per process.

    Returns:
        A cached HandlerContractFactory instance.
    """
    return HandlerContractFactory()


# Module-level convenience function for quick contract creation
def get_default_handler_contract(
    handler_type: EnumHandlerTypeCategory,
    handler_name: str,
    version: ModelSemVer | str = "1.0.0",
) -> ModelHandlerContract:
    """Get a default handler contract template with a single function call.

    This convenience function uses a cached HandlerContractFactory instance,
    ensuring that repeated calls benefit from template caching without creating
    new factory instances on each call.

    This function is the recommended entry point for simple use cases where
    you need to quickly create a handler contract with sensible defaults.

    Args:
        handler_type: The category of handler determining which template to use.
            - COMPUTE: For pure computational operations (no I/O side effects)
            - EFFECT: For handlers that perform I/O (database, network, filesystem)
            - NONDETERMINISTIC_COMPUTE: For AI/ML handlers with variable outputs
        handler_name: Unique identifier for the handler. This becomes both the
            handler_id and name fields in the contract. Should follow the naming
            convention: lowercase with underscores (e.g., "my_data_transformer").
        version: Contract version as either a ModelSemVer instance or a semver
            string. Supports full semver format including prerelease and build
            metadata (e.g., "1.0.0", "2.1.0-beta.1", "1.0.0+build.123").
            Defaults to "1.0.0".

    Returns:
        A fully validated ModelHandlerContract instance with safe defaults
        appropriate for the specified handler type.

    Raises:
        ValueError: If handler_type is None, not an EnumHandlerTypeCategory,
            or not one of the supported types (COMPUTE, EFFECT,
            NONDETERMINISTIC_COMPUTE). Also raised if handler_name is None,
            empty, or whitespace-only, or if version string is not valid semver.
        TemplateNotFoundError: If the template file for the handler type
            cannot be found in the contracts/defaults directory.
        TemplateParseError: If the template file contains invalid YAML.
        pydantic.ValidationError: If the resulting contract data fails
            Pydantic model validation (indicates a malformed template).

    Example:
        Basic usage with string version:

        >>> from omnibase_core.enums import EnumHandlerTypeCategory
        >>> from omnibase_spi.factories import get_default_handler_contract
        >>>
        >>> contract = get_default_handler_contract(
        ...     handler_type=EnumHandlerTypeCategory.COMPUTE,
        ...     handler_name="my_compute_handler"
        ... )
        >>> contract.handler_id
        'my_compute_handler'

        Using ModelSemVer for version:

        >>> from omnibase_core.models.primitives.model_semver import ModelSemVer
        >>> version = ModelSemVer(major=2, minor=1, patch=0)
        >>> contract = get_default_handler_contract(
        ...     handler_type=EnumHandlerTypeCategory.COMPUTE,
        ...     handler_name="my_compute_handler",
        ...     version=version
        ... )

        Creating an LLM/AI handler contract:

        >>> llm_contract = get_default_handler_contract(
        ...     handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
        ...     handler_name="my_llm_handler"
        ... )
        >>> llm_contract.permissions.network  # LLM handlers typically need network
        True

    See Also:
        - HandlerContractFactory: For creating multiple contracts with caching.
        - ModelHandlerContract: The contract model returned by this function.
    """
    factory = _get_cached_factory()
    return factory.get_default(handler_type, handler_name, version)
