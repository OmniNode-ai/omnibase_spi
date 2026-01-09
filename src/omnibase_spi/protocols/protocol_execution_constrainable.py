"""
Protocol for objects that can declare execution constraints.

Domain: Execution constraint declaration for handlers and contracts.

This module defines a mixin-style protocol for objects that can declare
execution constraints such as ordering dependencies and parallelism settings.
Handlers, contracts, and other runtime objects can implement this protocol
to declare their execution ordering requirements.

See Also:
    - ProtocolExecutionConstraints: The constraints definition protocol
    - ProtocolHandlerContract: Contract interface that uses this protocol
    - docs/architecture/HANDLER_PROTOCOL_DRIVEN_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.contracts.protocol_handler_contract_types import (
        ProtocolExecutionConstraints,
    )


@runtime_checkable
class ProtocolExecutionConstrainable(Protocol):
    """
    Protocol for objects that can declare execution constraints.

    This is a mixin-style protocol that can be implemented by handlers,
    contracts, or other objects that need to declare execution constraints
    such as ordering dependencies and parallelism settings.

    Execution constraints allow the runtime to correctly order handler
    executions and determine which handlers can run concurrently. When
    constraints are not defined (None), the runtime applies default
    constraints appropriate for the execution context.

    This protocol enables:
        - Explicit ordering dependencies between handlers (requires_before/after)
        - Parallel execution control (can_run_parallel)
        - Mandatory execution flags for side-effect handlers (must_run)
        - Nondeterminism tracking for replay/recovery (nondeterministic_effect)

    Example:
        ```python
        class MyHandler:
            '''Handler with execution constraints.'''

            def __init__(self) -> None:
                self._constraints: ProtocolExecutionConstraints | None = None

            @property
            def execution_constraints(self) -> ProtocolExecutionConstraints | None:
                return self._constraints

            def has_constraints(self) -> bool:
                return self._constraints is not None

        handler = MyHandler()
        assert isinstance(handler, ProtocolExecutionConstrainable)

        if handler.has_constraints():
            constraints = handler.execution_constraints
            print(f"Can run parallel: {constraints.can_run_parallel}")
            print(f"Must run: {constraints.must_run}")
        ```

    Note:
        Objects implementing this protocol should return consistent values
        from both methods. If ``has_constraints()`` returns True, then
        ``execution_constraints`` should return a non-None value. Similarly,
        if ``has_constraints()`` returns False, ``execution_constraints``
        should return None.

        This protocol defines execution ORDERING constraints, not resource
        settings. Resource settings (such as timeout_ms and isolation_policy)
        are defined in ProtocolHandlerBehaviorDescriptor.

    See Also:
        ProtocolExecutionConstraints: The constraints definition protocol.
        ProtocolHandlerBehaviorDescriptor: Defines resource settings and policies.
        ProtocolHandlerContract: Contract interface that uses this protocol.
    """

    @property
    def execution_constraints(self) -> ProtocolExecutionConstraints | None:
        """
        Get the execution constraints for this object.

        Execution constraints define ordering requirements and parallelism
        settings for how this object should be executed by the runtime.
        Constraint properties include:
            - requires_before: Handlers that must complete first
            - requires_after: Handlers that must run after
            - must_run: Whether this handler must always run
            - can_run_parallel: Whether parallel execution is allowed
            - nondeterministic_effect: Whether effects are nondeterministic

        Returns:
            Execution constraints if defined, None otherwise.
            When None, default constraints should be applied by the runtime.
            The runtime determines appropriate defaults based on the
            execution context and system configuration.

        Note:
            Implementations SHOULD return the same instance on repeated
            calls unless the constraints have been explicitly modified.
            Callers SHOULD treat the returned constraints as read-only.

            Resource settings (such as timeout_ms and isolation_policy) are
            defined in ProtocolHandlerBehaviorDescriptor, not in execution
            constraints.
        """
        ...

    def has_constraints(self) -> bool:
        """
        Check if this object has execution constraints defined.

        This method provides a fast check for constraint presence without
        requiring the caller to handle None values. It enables efficient
        conditional logic in the runtime:

        Example:
            ```python
            if constrainable.has_constraints():
                # Apply custom constraints
                apply_constraints(constrainable.execution_constraints)
            else:
                # Apply default constraints
                apply_default_constraints()
            ```

        Returns:
            True if constraints are defined, False otherwise.
            Returns True if and only if ``execution_constraints`` would
            return a non-None value.
        """
        ...


# ==============================================================================
# Module Exports
# ==============================================================================

__all__ = [
    "ProtocolExecutionConstrainable",
]
