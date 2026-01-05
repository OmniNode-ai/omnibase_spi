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
import importlib.resources
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

from omnibase_core.enums import EnumHandlerTypeCategory
from omnibase_core.models.contracts.model_handler_contract import ModelHandlerContract
from omnibase_core.models.primitives.model_semver import ModelSemVer

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
        FileNotFoundError: If the template file does not exist in the
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
        # Fallback for edge cases
        package_dir = Path(__file__).parent.parent / "contracts" / "defaults"
        path = package_dir / template_name
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}") from None
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
        FileNotFoundError: If the template file does not exist in the
            contracts/defaults directory.
        yaml.YAMLError: If the template file contains invalid YAML syntax.

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
    try:
        files = importlib.resources.files("omnibase_spi.contracts.defaults")
        template_resource = files.joinpath(template_name)
        content = template_resource.read_text(encoding="utf-8")
        return cast(dict[str, Any], yaml.safe_load(content))
    except (TypeError, AttributeError, FileNotFoundError):
        # Fallback to file path
        template_path = _get_template_path(template_name)
        with open(template_path, encoding="utf-8") as f:
            return cast(dict[str, Any], yaml.safe_load(f))


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

    Attributes:
        _template_cache: Internal cache mapping handler types to loaded templates.
            Populated lazily on first access to each handler type.

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

    def __init__(self) -> None:
        """Initialize a new HandlerContractFactory instance.

        Creates a new factory with an empty template cache. Templates are loaded
        lazily when first requested via get_default() and cached for subsequent
        requests.

        The factory does not perform any I/O during initialization; template
        loading is deferred until a contract is requested.

        Example:
            >>> factory = HandlerContractFactory()
            >>> len(factory._template_cache)  # Cache starts empty
            0
            >>> _ = factory.get_default(
            ...     handler_type=EnumHandlerTypeCategory.COMPUTE,
            ...     handler_name="test"
            ... )
            >>> len(factory._template_cache)  # Cache now has one entry
            1
        """
        self._template_cache: dict[EnumHandlerTypeCategory, dict[str, Any]] = {}

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
            ValueError: If handler_type is not one of the supported types
                (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE).
            pydantic.ValidationError: If the resulting contract data fails
                Pydantic model validation (indicates a malformed template).

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
            ModelSemVer(major=1, minor=0, patch=0)
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
        """
        return list(_DEFAULT_TEMPLATE_MAP.keys())


# Module-level convenience function for quick contract creation
def get_default_handler_contract(
    handler_type: EnumHandlerTypeCategory,
    handler_name: str,
    version: ModelSemVer | str = "1.0.0",
) -> ModelHandlerContract:
    """Get a default handler contract template with a single function call.

    This is a convenience function that creates a new HandlerContractFactory
    instance and calls get_default(). Use this for one-off contract creation.
    If creating multiple contracts, instantiate HandlerContractFactory directly
    to benefit from template caching.

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
        ValueError: If handler_type is not one of the supported types
            (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE).
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
    factory = HandlerContractFactory()
    return factory.get_default(handler_type, handler_name, version)
