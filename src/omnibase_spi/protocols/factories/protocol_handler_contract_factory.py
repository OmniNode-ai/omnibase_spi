"""Protocol definition for handler contract factory.

This module defines the ProtocolHandlerContractFactory protocol, which
specifies the interface for creating default handler contracts based on
handler type categories. Implementations provide safe, pre-configured
contract templates that can be extended via the patch system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.enums import EnumHandlerTypeCategory
    from omnibase_core.models.contracts.model_handler_contract import (
        ModelHandlerContract,
    )
    from omnibase_core.models.primitives.model_semver import ModelSemVer


@runtime_checkable
class ProtocolHandlerContractFactory(Protocol):
    """
    Factory interface for creating handler contracts.

    This protocol defines the interface for creating default handler
    contracts based on handler type category. Implementations provide
    safe default templates that can be extended via the patch system.

    Contract Factory vs Direct Construction:
        Using a factory provides several benefits over direct ModelHandlerContract
        instantiation:
        - Consistent defaults per handler type (COMPUTE, EFFECT, etc.)
        - Type-safe template generation
        - Centralized contract configuration management
        - Easier testing through factory substitution

    Version Flexibility:
        The version parameter accepts either a string (e.g., "1.0.0") or a
        ModelSemVer instance for semantic version specification. String versions
        are parsed automatically.

    Example:
        ```python
        factory: ProtocolHandlerContractFactory = HandlerContractFactory()

        # Using string version
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.EFFECT,
            handler_name="my_effect_handler",
            version="1.0.0"
        )

        # Using ModelSemVer
        from omnibase_core.models.primitives.model_semver import ModelSemVer
        contract = factory.get_default(
            handler_type=EnumHandlerTypeCategory.COMPUTE,
            handler_name="my_compute_handler",
            version=ModelSemVer(major=2, minor=1, patch=0)
        )

        # Check supported types
        supported = factory.available_types()
        print(f"Factory supports: {[t.value for t in supported]}")
        ```

    See Also:
        - ModelHandlerContract: The contract model returned by this factory
        - EnumHandlerTypeCategory: Handler type categories (COMPUTE, EFFECT, etc.)
    """

    def get_default(
        self,
        handler_type: EnumHandlerTypeCategory,
        handler_name: str,
        version: ModelSemVer | str = "1.0.0",
    ) -> ModelHandlerContract:
        """
        Get a default handler contract template for the given type.

        Creates a new ModelHandlerContract instance pre-configured with safe
        defaults appropriate for the specified handler type category. The
        returned contract can be used directly or customized via the patch
        system.

        Safe Defaults:
            Each handler type category has specific default settings:
            - COMPUTE: Deterministic execution, no side effects permitted
            - EFFECT: External I/O allowed, retry policies configured
            - NONDETERMINISTIC_COMPUTE: Non-deterministic output permitted

        Args:
            handler_type: The category of handler to create a contract for.
                Must be one of the supported EnumHandlerTypeCategory values
                (COMPUTE, EFFECT, NONDETERMINISTIC_COMPUTE).
            handler_name: Unique identifier for the handler. This name is
                used for registration, logging, and metrics collection.
                Should follow snake_case naming convention.
            version: Contract version as ModelSemVer or string (default: "1.0.0").
                String versions are parsed using semantic versioning rules.

        Returns:
            A ModelHandlerContract instance configured with safe defaults
            for the specified handler type. The contract includes appropriate
            settings for idempotency, retry behavior, timeout values, and
            capability declarations.

        Raises:
            ValueError: If handler_type is not supported by this factory.
                Use available_types() to check supported categories.

        Example:
            ```python
            # Create an effect handler contract
            contract = factory.get_default(
                handler_type=EnumHandlerTypeCategory.EFFECT,
                handler_name="database_writer",
                version="2.0.0"
            )

            # The contract is ready to use or can be customized
            print(f"Contract: {contract.handler_name} v{contract.version}")
            ```
        """
        ...

    def available_types(self) -> list[EnumHandlerTypeCategory]:
        """
        Return list of handler types this factory supports.

        Use this method to discover which handler type categories are supported
        before calling get_default(). This enables runtime introspection and
        validation of handler type requests.

        Returns:
            List of EnumHandlerTypeCategory values that this factory can
            create contracts for. Typically includes COMPUTE, EFFECT, and
            NONDETERMINISTIC_COMPUTE, but implementations may support a
            subset or additional custom categories.

        Example:
            ```python
            # Check if a handler type is supported before creating a contract
            supported = factory.available_types()

            if EnumHandlerTypeCategory.EFFECT in supported:
                contract = factory.get_default(
                    handler_type=EnumHandlerTypeCategory.EFFECT,
                    handler_name="my_handler"
                )
            else:
                raise RuntimeError("EFFECT handlers not supported")
            ```

        Note:
            This method does not raise exceptions. It returns an empty list if
            no handler types are configured, though standard implementations
            always return at least the core types (COMPUTE, EFFECT,
            NONDETERMINISTIC_COMPUTE).
        """
        ...
