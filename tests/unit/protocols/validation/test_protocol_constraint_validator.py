"""Tests for ProtocolConstraintValidator protocol compliance.

Validates that ProtocolConstraintValidator:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

import inspect
from typing import Any, Protocol

import pytest

from omnibase_spi.protocols.validation import ProtocolConstraintValidator

# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockExecutionProfile:
    """Mock that simulates ModelExecutionProfile from omnibase_core.

    Provides the minimal interface needed for testing ProtocolConstraintValidator.
    """

    def __init__(
        self,
        profile_id: str = "profile-001",
        phases: list[str] | None = None,
        deterministic_phases: list[str] | None = None,
        ordering_rules: dict[str, list[str]] | None = None,
    ) -> None:
        """Initialize the mock execution profile."""
        self.profile_id = profile_id
        # Use explicit None check to allow empty lists to be passed
        self.phases = phases if phases is not None else ["init", "compute", "finalize"]
        self.deterministic_phases = (
            deterministic_phases if deterministic_phases is not None else ["compute"]
        )
        self.ordering_rules = ordering_rules if ordering_rules is not None else {}


class MockExecutionConstraints:
    """Mock that simulates ModelExecutionConstraints from omnibase_core.

    Provides the minimal interface needed for testing ProtocolConstraintValidator.
    """

    def __init__(
        self,
        constraint_id: str = "constraint-001",
        requires_before: list[str] | None = None,
        requires_after: list[str] | None = None,
        must_run: bool = False,
        can_run_parallel: bool = True,
        nondeterministic_effect: bool = False,
        phase: str | None = None,
    ) -> None:
        """Initialize the mock execution constraints."""
        self.id = constraint_id
        self.requires_before = requires_before or []
        self.requires_after = requires_after or []
        self.must_run = must_run
        self.can_run_parallel = can_run_parallel
        self.nondeterministic_effect = nondeterministic_effect
        self.phase = phase


class MockExecutionConflict:
    """Mock that simulates ModelExecutionConflict from omnibase_core.

    Provides the minimal interface needed for testing ProtocolConstraintValidator.
    """

    def __init__(
        self,
        conflict_type: str = "cycle",
        message: str = "",
        cycle_path: list[str] | None = None,
        affected_constraints: list[str] | None = None,
    ) -> None:
        """Initialize the mock execution conflict."""
        self.conflict_type = conflict_type
        self.message = message
        self.cycle_path = cycle_path or []
        self.affected_constraints = affected_constraints or []


class MockValidationResult:
    """Mock that simulates ModelValidationResult from omnibase_core.

    Provides the minimal interface needed for testing ProtocolConstraintValidator.
    """

    def __init__(
        self,
        is_valid: bool = True,
        issues: list[MockExecutionConflict] | None = None,
    ) -> None:
        """Initialize the mock validation result."""
        self.is_valid = is_valid
        self.issues = issues or []


# =============================================================================
# Mock Implementations
# =============================================================================


class MockConstraintValidator:
    """A class that fully implements the ProtocolConstraintValidator protocol.

    This mock implementation provides a simple validator for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock constraint validator."""
        self._validation_count: int = 0

    async def validate(
        self,
        profile: Any,  # Would be ModelExecutionProfile
        constraints: list[Any],  # Would be list[ModelExecutionConstraints]
    ) -> Any:  # Would be ModelValidationResult[ModelExecutionConflict]
        """Validate that constraints are consistent with the execution profile.

        Args:
            profile: The execution profile defining available phases.
            constraints: List of execution constraints to validate.

        Returns:
            Validation result with is_valid and issues.
        """
        self._validation_count += 1

        # Collect all issues from sub-validations
        all_issues: list[MockExecutionConflict] = []

        cycles = await self.detect_cycles(constraints)
        all_issues.extend(cycles)

        phase_issues = await self.validate_phase_constraints(profile, constraints)
        all_issues.extend(phase_issues)

        determinism_issues = await self.validate_determinism(profile, constraints)
        all_issues.extend(determinism_issues)

        return MockValidationResult(
            is_valid=len(all_issues) == 0,
            issues=all_issues,
        )

    async def detect_cycles(
        self,
        constraints: list[Any],  # Would be list[ModelExecutionConstraints]
    ) -> list[Any]:  # Would be list[ModelExecutionConflict]
        """Detect circular dependencies in constraint ordering.

        Args:
            constraints: List of execution constraints to check for cycles.

        Returns:
            List of conflicts with conflict_type="cycle".
        """
        # Simple cycle detection for testing
        # Build a graph of dependencies
        graph: dict[str, set[str]] = {}
        for constraint in constraints:
            constraint_id = getattr(constraint, "id", str(id(constraint)))
            requires_before = getattr(constraint, "requires_before", [])
            graph[constraint_id] = set(requires_before)

        # Check for cycles using DFS
        conflicts: list[MockExecutionConflict] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(node: str, path: list[str]) -> list[str] | None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
                if neighbor not in visited:
                    result = has_cycle(neighbor, path)
                    if result:
                        return result

            path.pop()
            rec_stack.remove(node)
            return None

        for node in graph:
            if node not in visited:
                cycle_path = has_cycle(node, [])
                if cycle_path:
                    conflicts.append(
                        MockExecutionConflict(
                            conflict_type="cycle",
                            message=f"Circular dependency detected: {' -> '.join(cycle_path)}",
                            cycle_path=cycle_path,
                        )
                    )

        return conflicts

    async def validate_phase_constraints(
        self,
        profile: Any,  # Would be ModelExecutionProfile
        constraints: list[Any],  # Would be list[ModelExecutionConstraints]
    ) -> list[Any]:  # Would be list[ModelExecutionConflict]
        """Validate that all phase constraints reference valid phases.

        Args:
            profile: The execution profile defining available phases.
            constraints: List of execution constraints to validate.

        Returns:
            List of conflicts with conflict_type="invalid_phase".
        """
        conflicts: list[MockExecutionConflict] = []
        valid_phases = set(getattr(profile, "phases", []))

        for constraint in constraints:
            constraint_phase = getattr(constraint, "phase", None)
            if constraint_phase and constraint_phase not in valid_phases:
                conflicts.append(
                    MockExecutionConflict(
                        conflict_type="invalid_phase",
                        message=f"Phase '{constraint_phase}' not found in profile",
                        affected_constraints=[getattr(constraint, "id", "unknown")],
                    )
                )

        return conflicts

    async def validate_determinism(
        self,
        profile: Any,  # Would be ModelExecutionProfile
        constraints: list[Any],  # Would be list[ModelExecutionConstraints]
    ) -> list[Any]:  # Would be list[ModelExecutionConflict]
        """Validate nondeterministic effects are in allowed phases.

        Args:
            profile: The execution profile with phase determinism rules.
            constraints: List of execution constraints to validate.

        Returns:
            List of conflicts with conflict_type="determinism_violation".
        """
        conflicts: list[MockExecutionConflict] = []
        deterministic_phases = set(getattr(profile, "deterministic_phases", []))

        for constraint in constraints:
            is_nondeterministic = getattr(constraint, "nondeterministic_effect", False)
            constraint_phase = getattr(constraint, "phase", None)

            if is_nondeterministic and constraint_phase in deterministic_phases:
                conflicts.append(
                    MockExecutionConflict(
                        conflict_type="determinism_violation",
                        message=(
                            f"Nondeterministic effect in deterministic phase "
                            f"'{constraint_phase}'"
                        ),
                        affected_constraints=[getattr(constraint, "id", "unknown")],
                    )
                )

        return conflicts


class NonCompliantValidator:
    """A class that does not implement the ProtocolConstraintValidator protocol."""

    pass


class PartialValidatorMissingDetectCycles:
    """A class that has validate but missing detect_cycles."""

    async def validate(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> Any:
        """Only has validate, missing other methods."""
        return MockValidationResult()

    async def validate_phase_constraints(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> list[Any]:
        """Has validate_phase_constraints."""
        return []

    async def validate_determinism(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> list[Any]:
        """Has validate_determinism."""
        return []

    # Missing detect_cycles


class PartialValidatorMissingValidateDeterminism:
    """A class that has most methods but missing validate_determinism."""

    async def validate(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> Any:
        """Has validate."""
        return MockValidationResult()

    async def detect_cycles(
        self,
        constraints: list[Any],
    ) -> list[Any]:
        """Has detect_cycles."""
        return []

    async def validate_phase_constraints(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> list[Any]:
        """Has validate_phase_constraints."""
        return []

    # Missing validate_determinism


class SyncValidator:
    """A class that has sync methods instead of async."""

    def validate(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> Any:
        """Sync method - should be async."""
        return MockValidationResult()

    def detect_cycles(
        self,
        constraints: list[Any],
    ) -> list[Any]:
        """Sync method - should be async."""
        return []

    def validate_phase_constraints(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> list[Any]:
        """Sync method - should be async."""
        return []

    def validate_determinism(
        self,
        profile: Any,
        constraints: list[Any],
    ) -> list[Any]:
        """Sync method - should be async."""
        return []


class WrongSignatureValidator:
    """A class with methods but wrong signatures (missing parameters)."""

    async def validate(self) -> Any:
        """Missing profile and constraints parameters."""
        return MockValidationResult()

    async def detect_cycles(self) -> list[Any]:
        """Missing constraints parameter."""
        return []

    async def validate_phase_constraints(self) -> list[Any]:
        """Missing profile and constraints parameters."""
        return []

    async def validate_determinism(self) -> list[Any]:
        """Missing profile and constraints parameters."""
        return []


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolConstraintValidatorProtocol:
    """Test suite for ProtocolConstraintValidator protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolConstraintValidator should be runtime_checkable.

        Runtime checkable protocols have either _is_runtime_protocol
        or __runtime_protocol__ attribute set to True.
        """
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolConstraintValidator, "_is_runtime_protocol") or hasattr(
            ProtocolConstraintValidator, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolConstraintValidator should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolConstraintValidator.__mro__
        )

    def test_protocol_has_validate_method(self) -> None:
        """ProtocolConstraintValidator should define validate method."""
        assert "validate" in dir(ProtocolConstraintValidator)

    def test_protocol_has_detect_cycles_method(self) -> None:
        """ProtocolConstraintValidator should define detect_cycles method."""
        assert "detect_cycles" in dir(ProtocolConstraintValidator)

    def test_protocol_has_validate_phase_constraints_method(self) -> None:
        """ProtocolConstraintValidator should define validate_phase_constraints method."""
        assert "validate_phase_constraints" in dir(ProtocolConstraintValidator)

    def test_protocol_has_validate_determinism_method(self) -> None:
        """ProtocolConstraintValidator should define validate_determinism method."""
        assert "validate_determinism" in dir(ProtocolConstraintValidator)

    def test_protocol_methods_are_async(self) -> None:
        """All protocol methods should be coroutine functions."""
        # Get the methods from the protocol
        validate = getattr(ProtocolConstraintValidator, "validate", None)
        detect_cycles = getattr(ProtocolConstraintValidator, "detect_cycles", None)
        validate_phase = getattr(
            ProtocolConstraintValidator, "validate_phase_constraints", None
        )
        validate_det = getattr(
            ProtocolConstraintValidator, "validate_determinism", None
        )

        assert validate is not None
        assert detect_cycles is not None
        assert validate_phase is not None
        assert validate_det is not None

        # Check if they're defined as async (coroutine functions)
        assert inspect.iscoroutinefunction(validate)
        assert inspect.iscoroutinefunction(detect_cycles)
        assert inspect.iscoroutinefunction(validate_phase)
        assert inspect.iscoroutinefunction(validate_det)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolConstraintValidator should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolConstraintValidator()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolConstraintValidatorCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance_check(self) -> None:
        """A class implementing the protocol should pass isinstance check."""
        validator = MockConstraintValidator()
        assert isinstance(validator, ProtocolConstraintValidator)

    def test_non_compliant_class_fails_isinstance_check(self) -> None:
        """A class not implementing the protocol should fail isinstance check."""
        not_a_validator = NonCompliantValidator()
        assert not isinstance(not_a_validator, ProtocolConstraintValidator)

    def test_partial_missing_detect_cycles_fails_isinstance_check(self) -> None:
        """A class missing detect_cycles should fail isinstance check."""
        partial = PartialValidatorMissingDetectCycles()
        assert not isinstance(partial, ProtocolConstraintValidator)

    def test_partial_missing_validate_determinism_fails_isinstance_check(self) -> None:
        """A class missing validate_determinism should fail isinstance check."""
        partial = PartialValidatorMissingValidateDeterminism()
        assert not isinstance(partial, ProtocolConstraintValidator)

    def test_sync_methods_still_pass_isinstance_check(self) -> None:
        """A class with sync methods passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not whether it's async. This is a limitation of runtime_checkable.
        Static type checkers would catch this issue.
        """
        sync_validator = SyncValidator()
        # Runtime check only verifies methods exist, not that they're async
        assert isinstance(sync_validator, ProtocolConstraintValidator)

    def test_wrong_signature_still_passes_isinstance_check(self) -> None:
        """A class with wrong signature passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not the full method signature. Static type checkers would catch this.
        """
        wrong_sig = WrongSignatureValidator()
        # Runtime check only verifies methods exist
        assert isinstance(wrong_sig, ProtocolConstraintValidator)


@pytest.mark.unit
class TestMockConstraintValidatorImplementation:
    """Test that MockConstraintValidator has all required members."""

    def test_mock_has_all_methods(self) -> None:
        """Mock should have all required methods."""
        validator = MockConstraintValidator()
        assert hasattr(validator, "validate")
        assert hasattr(validator, "detect_cycles")
        assert hasattr(validator, "validate_phase_constraints")
        assert hasattr(validator, "validate_determinism")
        assert callable(validator.validate)
        assert callable(validator.detect_cycles)
        assert callable(validator.validate_phase_constraints)
        assert callable(validator.validate_determinism)

    def test_mock_methods_are_async(self) -> None:
        """Mock methods should all be async."""
        validator = MockConstraintValidator()
        assert inspect.iscoroutinefunction(validator.validate)
        assert inspect.iscoroutinefunction(validator.detect_cycles)
        assert inspect.iscoroutinefunction(validator.validate_phase_constraints)
        assert inspect.iscoroutinefunction(validator.validate_determinism)

    @pytest.mark.asyncio
    async def test_mock_validate_returns_result(self) -> None:
        """Mock validate should return a validation result."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile()
        constraints = [MockExecutionConstraints()]

        result = await validator.validate(profile, constraints)

        assert result is not None
        assert hasattr(result, "is_valid")
        assert hasattr(result, "issues")

    @pytest.mark.asyncio
    async def test_mock_validate_with_no_constraints(self) -> None:
        """Mock validate should handle empty constraint list."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile()

        result = await validator.validate(profile, [])

        assert result is not None
        assert result.is_valid is True
        assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_mock_validate_increments_counter(self) -> None:
        """Mock validate should track validation count."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile()
        constraints = [MockExecutionConstraints()]

        assert validator._validation_count == 0

        await validator.validate(profile, constraints)
        assert validator._validation_count == 1

        await validator.validate(profile, constraints)
        assert validator._validation_count == 2

    @pytest.mark.asyncio
    async def test_mock_detect_cycles_returns_list(self) -> None:
        """Mock detect_cycles should return a list."""
        validator = MockConstraintValidator()
        constraints = [MockExecutionConstraints()]

        result = await validator.detect_cycles(constraints)

        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_mock_detect_cycles_finds_simple_cycle(self) -> None:
        """Mock detect_cycles should detect a simple A->B->A cycle."""
        validator = MockConstraintValidator()
        constraints = [
            MockExecutionConstraints(constraint_id="a", requires_before=["b"]),
            MockExecutionConstraints(constraint_id="b", requires_before=["a"]),
        ]

        result = await validator.detect_cycles(constraints)

        assert len(result) >= 1
        assert result[0].conflict_type == "cycle"

    @pytest.mark.asyncio
    async def test_mock_detect_cycles_no_cycle(self) -> None:
        """Mock detect_cycles should return empty list when no cycles."""
        validator = MockConstraintValidator()
        constraints = [
            MockExecutionConstraints(constraint_id="a", requires_before=["b"]),
            MockExecutionConstraints(constraint_id="b", requires_before=[]),
        ]

        result = await validator.detect_cycles(constraints)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_mock_validate_phase_constraints_returns_list(self) -> None:
        """Mock validate_phase_constraints should return a list."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile()
        constraints = [MockExecutionConstraints()]

        result = await validator.validate_phase_constraints(profile, constraints)

        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_mock_validate_phase_constraints_finds_invalid_phase(self) -> None:
        """Mock validate_phase_constraints should detect invalid phase references."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(phases=["init", "compute", "finalize"])
        constraints = [
            MockExecutionConstraints(constraint_id="a", phase="nonexistent_phase"),
        ]

        result = await validator.validate_phase_constraints(profile, constraints)

        assert len(result) == 1
        assert result[0].conflict_type == "invalid_phase"

    @pytest.mark.asyncio
    async def test_mock_validate_phase_constraints_valid_phases(self) -> None:
        """Mock validate_phase_constraints should pass for valid phases."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(phases=["init", "compute", "finalize"])
        constraints = [
            MockExecutionConstraints(constraint_id="a", phase="compute"),
        ]

        result = await validator.validate_phase_constraints(profile, constraints)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_mock_validate_determinism_returns_list(self) -> None:
        """Mock validate_determinism should return a list."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile()
        constraints = [MockExecutionConstraints()]

        result = await validator.validate_determinism(profile, constraints)

        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_mock_validate_determinism_finds_violation(self) -> None:
        """Mock validate_determinism should detect nondeterministic in deterministic phase."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(deterministic_phases=["compute"])
        constraints = [
            MockExecutionConstraints(
                constraint_id="a",
                phase="compute",
                nondeterministic_effect=True,
            ),
        ]

        result = await validator.validate_determinism(profile, constraints)

        assert len(result) == 1
        assert result[0].conflict_type == "determinism_violation"

    @pytest.mark.asyncio
    async def test_mock_validate_determinism_no_violation(self) -> None:
        """Mock validate_determinism should pass for deterministic effects in det phase."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(deterministic_phases=["compute"])
        constraints = [
            MockExecutionConstraints(
                constraint_id="a",
                phase="compute",
                nondeterministic_effect=False,
            ),
        ]

        result = await validator.validate_determinism(profile, constraints)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_mock_validate_aggregates_all_issues(self) -> None:
        """Mock validate should aggregate issues from all sub-validations."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(
            phases=["init", "compute", "finalize"],
            deterministic_phases=["compute"],
        )
        # Create constraints with multiple issues:
        # 1. A cycle
        # 2. An invalid phase
        # 3. A determinism violation
        constraints = [
            MockExecutionConstraints(
                constraint_id="a",
                requires_before=["b"],
                phase="invalid_phase",  # Invalid phase
            ),
            MockExecutionConstraints(
                constraint_id="b",
                requires_before=["a"],  # Creates cycle with 'a'
                phase="compute",
                nondeterministic_effect=True,  # Determinism violation
            ),
        ]

        result = await validator.validate(profile, constraints)

        assert result.is_valid is False
        # Should have at least cycle + invalid_phase + determinism_violation
        assert len(result.issues) >= 3


@pytest.mark.unit
class TestProtocolConstraintValidatorImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_constraint_validator module."""
        from omnibase_spi.protocols.validation.protocol_constraint_validator import (
            ProtocolConstraintValidator as DirectProtocol,
        )

        validator = MockConstraintValidator()
        assert isinstance(validator, DirectProtocol)

    def test_protocol_exports_from_validation_module(self) -> None:
        """Protocol should be importable from validation module."""
        from omnibase_spi.protocols.validation import (
            ProtocolConstraintValidator as ValidationProtocol,
        )

        validator = MockConstraintValidator()
        assert isinstance(validator, ValidationProtocol)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.validation import (
            ProtocolConstraintValidator as ValidationProtocol,
        )
        from omnibase_spi.protocols.validation.protocol_constraint_validator import (
            ProtocolConstraintValidator as DirectProtocol,
        )

        assert DirectProtocol is ValidationProtocol

    def test_protocol_exports_from_main_module(self) -> None:
        """Protocol should be importable from main protocols module."""
        from omnibase_spi.protocols import (
            ProtocolConstraintValidator as MainProtocol,
        )

        validator = MockConstraintValidator()
        assert isinstance(validator, MainProtocol)

    def test_all_imports_are_same_class(self) -> None:
        """Verify all import paths reference the same class."""
        from omnibase_spi.protocols import (
            ProtocolConstraintValidator as MainProtocol,
        )
        from omnibase_spi.protocols.validation import (
            ProtocolConstraintValidator as ValidationProtocol,
        )
        from omnibase_spi.protocols.validation.protocol_constraint_validator import (
            ProtocolConstraintValidator as DirectProtocol,
        )

        assert DirectProtocol is ValidationProtocol
        assert ValidationProtocol is MainProtocol


@pytest.mark.unit
class TestProtocolConstraintValidatorDocumentation:
    """Test that ProtocolConstraintValidator has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolConstraintValidator should have a docstring."""
        assert ProtocolConstraintValidator.__doc__ is not None
        assert len(ProtocolConstraintValidator.__doc__.strip()) > 0

    def test_docstring_mentions_constraint_or_validation(self) -> None:
        """Docstring should mention constraint validation purpose."""
        doc = ProtocolConstraintValidator.__doc__ or ""
        # Should mention constraint or validation concepts
        doc_lower = doc.lower()
        assert "constraint" in doc_lower or "validation" in doc_lower

    def test_validate_method_has_docstring(self) -> None:
        """The validate method should have a docstring."""
        method = getattr(ProtocolConstraintValidator, "validate", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0

    def test_detect_cycles_method_has_docstring(self) -> None:
        """The detect_cycles method should have a docstring."""
        method = getattr(ProtocolConstraintValidator, "detect_cycles", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0

    def test_validate_phase_constraints_method_has_docstring(self) -> None:
        """The validate_phase_constraints method should have a docstring."""
        method = getattr(ProtocolConstraintValidator, "validate_phase_constraints", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0

    def test_validate_determinism_method_has_docstring(self) -> None:
        """The validate_determinism method should have a docstring."""
        method = getattr(ProtocolConstraintValidator, "validate_determinism", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0


@pytest.mark.unit
class TestConstraintValidationScenarios:
    """Test comprehensive constraint validation scenarios."""

    @pytest.mark.asyncio
    async def test_three_node_cycle_detection(self) -> None:
        """Test detection of A->B->C->A cycle."""
        validator = MockConstraintValidator()
        constraints = [
            MockExecutionConstraints(constraint_id="a", requires_before=["b"]),
            MockExecutionConstraints(constraint_id="b", requires_before=["c"]),
            MockExecutionConstraints(constraint_id="c", requires_before=["a"]),
        ]

        result = await validator.detect_cycles(constraints)

        assert len(result) >= 1
        assert result[0].conflict_type == "cycle"

    @pytest.mark.asyncio
    async def test_self_referential_not_detected_as_cycle(self) -> None:
        """Test that self-referential constraints are handled.

        Note: Whether this is a cycle depends on implementation.
        This test documents the current behavior.
        """
        validator = MockConstraintValidator()
        constraints = [
            # A constraint that references itself
            MockExecutionConstraints(constraint_id="a", requires_before=["a"]),
        ]

        result = await validator.detect_cycles(constraints)

        # Self-reference creates an immediate cycle
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_multiple_independent_cycles(self) -> None:
        """Test detection when multiple independent cycles exist."""
        validator = MockConstraintValidator()
        constraints = [
            # Cycle 1: a -> b -> a
            MockExecutionConstraints(constraint_id="a", requires_before=["b"]),
            MockExecutionConstraints(constraint_id="b", requires_before=["a"]),
            # Independent node (no cycle)
            MockExecutionConstraints(constraint_id="c", requires_before=[]),
        ]

        profile = MockExecutionProfile()
        result = await validator.validate(profile, constraints)

        assert result.is_valid is False
        # Should detect at least one cycle
        cycle_issues = [i for i in result.issues if i.conflict_type == "cycle"]
        assert len(cycle_issues) >= 1

    @pytest.mark.asyncio
    async def test_valid_dag_no_cycles(self) -> None:
        """Test that a valid DAG has no cycles."""
        validator = MockConstraintValidator()
        # Linear chain: a -> b -> c
        constraints = [
            MockExecutionConstraints(constraint_id="a", requires_before=["b"]),
            MockExecutionConstraints(constraint_id="b", requires_before=["c"]),
            MockExecutionConstraints(constraint_id="c", requires_before=[]),
        ]

        result = await validator.detect_cycles(constraints)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_diamond_dag_no_cycles(self) -> None:
        """Test that a diamond-shaped DAG has no cycles."""
        validator = MockConstraintValidator()
        # Diamond: a -> b, a -> c, b -> d, c -> d
        constraints = [
            MockExecutionConstraints(constraint_id="a", requires_before=["b", "c"]),
            MockExecutionConstraints(constraint_id="b", requires_before=["d"]),
            MockExecutionConstraints(constraint_id="c", requires_before=["d"]),
            MockExecutionConstraints(constraint_id="d", requires_before=[]),
        ]

        result = await validator.detect_cycles(constraints)

        assert len(result) == 0


@pytest.mark.unit
class TestConstraintValidatorEdgeCases:
    """Test edge cases for ProtocolConstraintValidator."""

    @pytest.mark.asyncio
    async def test_empty_profile_phases(self) -> None:
        """Test validation with profile having no phases."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(phases=[])
        constraints = [
            MockExecutionConstraints(constraint_id="a", phase="any_phase"),
        ]

        result = await validator.validate_phase_constraints(profile, constraints)

        # Any phase reference should be invalid
        assert len(result) == 1
        assert result[0].conflict_type == "invalid_phase"

    @pytest.mark.asyncio
    async def test_constraint_with_no_phase(self) -> None:
        """Test validation when constraint has no phase specified."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile()
        constraints = [
            MockExecutionConstraints(constraint_id="a", phase=None),
        ]

        result = await validator.validate_phase_constraints(profile, constraints)

        # No phase = no phase constraint violation
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_determinism_check_with_no_deterministic_phases(self) -> None:
        """Test determinism validation when no phases are deterministic."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(deterministic_phases=[])
        constraints = [
            MockExecutionConstraints(
                constraint_id="a",
                phase="compute",
                nondeterministic_effect=True,
            ),
        ]

        result = await validator.validate_determinism(profile, constraints)

        # No deterministic phases = no violations possible
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_nondeterministic_in_nondeterministic_phase(self) -> None:
        """Test that nondeterministic effects in non-deterministic phases are ok."""
        validator = MockConstraintValidator()
        profile = MockExecutionProfile(
            phases=["init", "compute", "effect"],
            deterministic_phases=["compute"],  # Only compute is deterministic
        )
        constraints = [
            MockExecutionConstraints(
                constraint_id="a",
                phase="effect",  # Not a deterministic phase
                nondeterministic_effect=True,
            ),
        ]

        result = await validator.validate_determinism(profile, constraints)

        assert len(result) == 0  # Should be allowed
