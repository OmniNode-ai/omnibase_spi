"""
Handler Contract Factory Implementation.

Provides factory functions for creating default handler contracts
based on handler type category.
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

# Map handler type category to their default template files
_DEFAULT_TEMPLATE_MAP: dict[EnumHandlerTypeCategory, str] = {
    EnumHandlerTypeCategory.COMPUTE: "default_compute_handler.yaml",
    EnumHandlerTypeCategory.EFFECT: "default_effect_handler.yaml",
    EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE: "default_nondeterministic_compute_handler.yaml",
}


def _get_template_path(template_name: str) -> Path:
    """
    Get the path to a template file in the contracts/defaults directory.

    Args:
        template_name: Name of the template file

    Returns:
        Path to the template file

    Raises:
        FileNotFoundError: If template file does not exist
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
    """
    Load a YAML template file.

    Args:
        template_name: Name of the template file

    Returns:
        Parsed YAML content as dictionary

    Raises:
        FileNotFoundError: If template file does not exist
        yaml.YAMLError: If template is not valid YAML
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
    """
    Factory for creating default handler contracts.

    Implements ProtocolHandlerContractFactory protocol.

    This factory loads default contract templates from YAML files
    and creates validated ModelHandlerContract instances with safe defaults
    that can be customized via the patch system.

    Example:
        ```python
        from omnibase_core.enums import EnumHandlerTypeCategory
        from omnibase_spi.factories import HandlerContractFactory

        factory = HandlerContractFactory()

        # Get default effect handler contract
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="my_database_handler",
            version="1.0.0"
        )

        # Get nondeterministic compute (LLM) handler contract
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            handler_name="my_llm_handler",
            version="1.0.0"
        )

        # Check available types
        types = factory.available_types()
        # [EnumHandlerTypeCategory.COMPUTE, EnumHandlerTypeCategory.EFFECT, ...]
        ```
    """

    def __init__(self) -> None:
        """Initialize the factory with template cache."""
        self._template_cache: dict[EnumHandlerTypeCategory, dict[str, Any]] = {}

    def _get_template(self, handler_type: EnumHandlerTypeCategory) -> dict[str, Any]:
        """
        Get template for handler type, using cache.

        Args:
            handler_type: The handler type category

        Returns:
            Template dictionary

        Raises:
            ValueError: If handler type is not supported
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
        """
        Get a default handler contract for the given type.

        Creates a new validated ModelHandlerContract based on the default template
        for the specified handler type, customized with the provided
        handler name and version.

        Args:
            handler_type: The category of handler (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE)
            handler_name: Unique identifier for the handler
            version: Contract version as ModelSemVer or string (default: "1.0.0")

        Returns:
            A validated ModelHandlerContract with safe defaults for the handler type

        Raises:
            ValueError: If handler_type is not supported
            ValidationError: If the resulting contract fails Pydantic validation
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
        """
        Return list of handler types this factory supports.

        Returns:
            List of supported EnumHandlerTypeCategory values
        """
        return list(_DEFAULT_TEMPLATE_MAP.keys())


# Module-level convenience function
def get_default_handler_contract(
    handler_type: EnumHandlerTypeCategory,
    handler_name: str,
    version: ModelSemVer | str = "1.0.0",
) -> ModelHandlerContract:
    """
    Get a default handler contract template.

    Convenience function that uses the default HandlerContractFactory.

    Args:
        handler_type: The category of handler (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE)
        handler_name: Unique identifier for the handler
        version: Contract version as ModelSemVer or string (default: "1.0.0")

    Returns:
        A validated ModelHandlerContract with safe defaults for the handler type

    Raises:
        ValueError: If handler_type is not supported
        ValidationError: If the resulting contract fails Pydantic validation

    Example:
        ```python
        from omnibase_core.enums import EnumHandlerTypeCategory
        from omnibase_spi.factories import get_default_handler_contract
        from omnibase_core.models.primitives.model_semver import ModelSemVer

        # Using string version
        contract = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="my_compute_handler"
        )

        # Using ModelSemVer
        version = ModelSemVer(major=2, minor=1, patch=0)
        contract = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="my_compute_handler",
            version=version
        )

        # For LLM/AI handlers:
        llm_contract = get_default_handler_contract(
            handler_type=EnumHandlerTypeCategory.NONDETERMINISTIC_COMPUTE,
            handler_name="my_llm_handler"
        )
        ```
    """
    factory = HandlerContractFactory()
    return factory.get_default(handler_type, handler_name, version)
