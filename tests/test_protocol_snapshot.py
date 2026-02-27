"""
Protocol signature snapshot tests for omnibase_spi.

Detects protocol signature drift across commits by comparing current protocol
signatures against a stored snapshot. Prevents accidental breaking changes to
the SPI contract.

Usage:
    # Run snapshot tests (compare against stored snapshot)
    uv run pytest tests/test_protocol_snapshot.py -v

    # Update snapshot after intentional changes
    uv run pytest tests/test_protocol_snapshot.py --update-snapshots

    # Generate snapshot without running comparison
    uv run python tests/test_protocol_snapshot.py

Ticket: OMN-359
"""

from __future__ import annotations

import inspect
import json
import sys
import typing
from pathlib import Path
from typing import Any, get_type_hints

import pytest

# Add src directory to Python path for testing
src_dir = Path(__file__).parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
SNAPSHOT_FILE = SNAPSHOT_DIR / "protocol_signatures.json"


def _normalize_type_annotation(annotation: Any) -> str:
    """Normalize a type annotation to a stable string representation.

    Handles forward references, generic aliases, typing constructs, and
    ensures consistent output across Python versions.

    Args:
        annotation: A type annotation (type, string, or typing construct).

    Returns:
        A stable string representation of the type.
    """
    if annotation is inspect.Parameter.empty or annotation is inspect.Signature.empty:
        return "<empty>"

    # Handle string forward references
    if isinstance(annotation, str):
        return annotation

    # Handle None / NoneType
    if annotation is type(None):
        return "None"

    # Handle typing.ForwardRef
    if isinstance(annotation, typing.ForwardRef):
        return annotation.__forward_arg__

    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", None)

    # Handle Union types (X | Y syntax in Python 3.10+)
    if origin is typing.Union:
        if args:
            normalized = [_normalize_type_annotation(a) for a in args]
            return " | ".join(normalized)
        return "Union"

    # Handle generic types like list[str], dict[str, int], etc.
    if origin is not None and args is not None:
        origin_name = getattr(origin, "__qualname__", None) or getattr(
            origin, "__name__", str(origin)
        )
        # Normalize common origins
        origin_map: dict[str, str] = {
            "list": "list",
            "dict": "dict",
            "set": "set",
            "frozenset": "frozenset",
            "tuple": "tuple",
            "type": "type",
            "Type": "type",
            "List": "list",
            "Dict": "dict",
            "Set": "set",
            "FrozenSet": "frozenset",
            "Tuple": "tuple",
            "Callable": "Callable",
            "Awaitable": "Awaitable",
            "Coroutine": "Coroutine",
            "AsyncIterator": "AsyncIterator",
            "Iterator": "Iterator",
            "Generator": "Generator",
            "AsyncGenerator": "AsyncGenerator",
            "Sequence": "Sequence",
            "Mapping": "Mapping",
            "MutableMapping": "MutableMapping",
            "MutableSequence": "MutableSequence",
        }
        normalized_origin = origin_map.get(str(origin_name), str(origin_name))
        normalized_args = ", ".join(_normalize_type_annotation(a) for a in args)
        return f"{normalized_origin}[{normalized_args}]"

    # Handle Literal types
    if origin is typing.Literal:
        if args:
            return f"Literal[{', '.join(repr(a) for a in args)}]"
        return "Literal"

    # Handle plain generic origins without args
    if origin is not None:
        return getattr(origin, "__qualname__", str(origin))

    # Handle regular types
    if isinstance(annotation, type):
        module = getattr(annotation, "__module__", "")
        qualname = getattr(annotation, "__qualname__", annotation.__name__)
        if module in ("builtins", ""):
            return qualname
        return qualname

    # Fallback
    return str(annotation)


def _extract_method_signature(
    protocol_cls: type, method_name: str
) -> dict[str, Any] | None:
    """Extract a normalized signature for a single method.

    Args:
        protocol_cls: The protocol class.
        method_name: Name of the method to extract.

    Returns:
        Dictionary with method signature details, or None if extraction fails.
    """
    attr = getattr(protocol_cls, method_name, None)
    if attr is None:
        return None

    # Check if it's a property
    for cls in protocol_cls.__mro__:
        if method_name in cls.__dict__:
            class_attr = cls.__dict__[method_name]
            if isinstance(class_attr, property):
                # Extract property type from fget return annotation
                fget = class_attr.fget
                if fget is not None:
                    try:
                        hints = get_type_hints(fget, include_extras=True)
                    except Exception:
                        try:
                            hints = fget.__annotations__
                        except Exception:
                            hints = {}
                    return_type = hints.get("return", inspect.Parameter.empty)
                    return {
                        "kind": "property",
                        "return_type": _normalize_type_annotation(return_type),
                    }
                return {"kind": "property", "return_type": "<empty>"}
            break

    if not callable(attr):
        return None

    # Get the actual function object (unwrap if needed)
    func = attr
    if hasattr(func, "__func__"):
        func = func.__func__

    # Try to get type hints first (resolves forward references)
    try:
        hints = get_type_hints(func, include_extras=True)
    except Exception:
        # Fall back to raw annotations if get_type_hints fails
        try:
            hints = func.__annotations__
        except Exception:
            hints = {}

    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return None

    parameters: dict[str, dict[str, str]] = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        param_type = hints.get(param_name, param.annotation)
        param_info: dict[str, str] = {
            "type": _normalize_type_annotation(param_type),
        }
        if param.default is not inspect.Parameter.empty:
            param_info["default"] = repr(param.default)
        parameters[param_name] = param_info

    return_type = hints.get("return", sig.return_annotation)
    is_async = inspect.iscoroutinefunction(func)

    return {
        "kind": "async_method" if is_async else "method",
        "parameters": parameters,
        "return_type": _normalize_type_annotation(return_type),
    }


def _extract_protocol_attributes(protocol_cls: type) -> dict[str, dict[str, str]]:
    """Extract typed attributes (non-method members) from a protocol class.

    Protocol classes can define structural contracts via typed attributes
    (e.g., ``name: str``) in addition to methods. This function extracts
    those attribute annotations.

    Args:
        protocol_cls: The protocol class to introspect.

    Returns:
        Dictionary mapping attribute names to their type information.
    """
    attributes: dict[str, dict[str, str]] = {}

    # Get annotations directly defined on the protocol (not inherited from Protocol)
    for cls in protocol_cls.__mro__:
        if cls.__name__ == "Protocol" and cls.__module__ == "typing":
            break
        if cls is object:
            break
        annotations = getattr(cls, "__annotations__", {})
        for attr_name, attr_type in annotations.items():
            if attr_name.startswith("_"):
                continue
            if attr_name not in attributes:
                attributes[attr_name] = {
                    "kind": "attribute",
                    "type": _normalize_type_annotation(attr_type),
                }

    return attributes


def _extract_protocol_signature(protocol_cls: type) -> dict[str, Any]:
    """Extract a full normalized signature for a protocol class.

    Captures all public methods, properties, and typed attributes with their
    parameter types, return types, and whether they are async.

    Args:
        protocol_cls: The protocol class to introspect.

    Returns:
        Dictionary mapping member names to their signature details.
    """
    members: dict[str, Any] = {}

    # Collect typed attributes first
    attributes = _extract_protocol_attributes(protocol_cls)
    members.update(attributes)

    # Dunder methods that are meaningful for protocol contracts
    _PROTOCOL_DUNDERS = frozenset(
        {
            "__call__",
            "__aenter__",
            "__aexit__",
            "__enter__",
            "__exit__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__contains__",
            "__len__",
            "__iter__",
            "__next__",
            "__aiter__",
            "__anext__",
            "__hash__",
            "__eq__",
            "__lt__",
            "__le__",
            "__gt__",
            "__ge__",
        }
    )

    # Collect all public methods/properties defined in the protocol
    for name in sorted(dir(protocol_cls)):
        # Skip private/dunder unless it's in the meaningful set
        if name.startswith("_") and name not in _PROTOCOL_DUNDERS:
            continue
        # Skip if already captured as an attribute
        if name in members:
            continue

        sig = _extract_method_signature(protocol_cls, name)
        if sig is not None:
            members[name] = sig

    return members


def _collect_all_protocol_signatures() -> dict[str, dict[str, Any]]:
    """Collect signatures for all protocols exported from omnibase_spi.protocols.

    Returns:
        Dictionary mapping protocol names to their method signatures.
    """
    import omnibase_spi.protocols as protocols_pkg

    all_names: list[str] = getattr(protocols_pkg, "__all__", [])

    signatures: dict[str, dict[str, Any]] = {}

    for name in sorted(all_names):
        obj = getattr(protocols_pkg, name, None)
        if obj is None:
            continue

        # Only process Protocol classes (skip Literal types, enums, etc.)
        if not isinstance(obj, type):
            continue

        # Check if it's a Protocol subclass
        is_protocol = False
        for base in getattr(obj, "__mro__", []):
            if base.__name__ == "Protocol" and base.__module__ == "typing":
                is_protocol = True
                break

        if not is_protocol:
            continue

        protocol_sig = _extract_protocol_signature(obj)
        if protocol_sig:  # Only include protocols with extractable methods
            signatures[name] = protocol_sig

    return signatures


def _load_snapshot() -> dict[str, dict[str, Any]] | None:
    """Load the stored protocol signature snapshot.

    Returns:
        The snapshot data, or None if no snapshot file exists.
    """
    if not SNAPSHOT_FILE.exists():
        return None
    return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _save_snapshot(signatures: dict[str, dict[str, Any]]) -> None:
    """Save the current protocol signatures as the snapshot.

    Args:
        signatures: The protocol signatures to save.
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(
        json.dumps(signatures, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _diff_signatures(
    snapshot: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
) -> list[str]:
    """Compare snapshot against current signatures and produce human-readable diffs.

    Args:
        snapshot: The stored snapshot signatures.
        current: The current protocol signatures.

    Returns:
        List of human-readable diff messages. Empty if signatures match.
    """
    diffs: list[str] = []

    # Check for removed protocols
    for proto_name in sorted(set(snapshot.keys()) - set(current.keys())):
        diffs.append(f"REMOVED protocol: {proto_name}")

    # Check for added protocols
    for proto_name in sorted(set(current.keys()) - set(snapshot.keys())):
        methods = current[proto_name]
        diffs.append(f"ADDED protocol: {proto_name} ({len(methods)} method(s))")

    # Check for modified protocols
    for proto_name in sorted(set(snapshot.keys()) & set(current.keys())):
        snap_methods = snapshot[proto_name]
        curr_methods = current[proto_name]

        # Removed methods
        for method_name in sorted(set(snap_methods.keys()) - set(curr_methods.keys())):
            diffs.append(f"REMOVED method: {proto_name}.{method_name}")

        # Added methods
        for method_name in sorted(set(curr_methods.keys()) - set(snap_methods.keys())):
            kind = curr_methods[method_name].get("kind", "method")
            diffs.append(f"ADDED method: {proto_name}.{method_name} ({kind})")

        # Changed methods
        for method_name in sorted(set(snap_methods.keys()) & set(curr_methods.keys())):
            snap_method = snap_methods[method_name]
            curr_method = curr_methods[method_name]

            if snap_method != curr_method:
                changes: list[str] = []

                # Check kind change
                if snap_method.get("kind") != curr_method.get("kind"):
                    changes.append(
                        f"kind: {snap_method.get('kind')} -> {curr_method.get('kind')}"
                    )

                # Check return type change
                if snap_method.get("return_type") != curr_method.get("return_type"):
                    changes.append(
                        f"return: {snap_method.get('return_type')} -> "
                        f"{curr_method.get('return_type')}"
                    )

                # Check parameter changes
                snap_params = snap_method.get("parameters", {})
                curr_params = curr_method.get("parameters", {})

                for param in sorted(set(snap_params.keys()) - set(curr_params.keys())):
                    changes.append(f"removed param: {param}")

                for param in sorted(set(curr_params.keys()) - set(snap_params.keys())):
                    changes.append(
                        f"added param: {param}: {curr_params[param].get('type')}"
                    )

                for param in sorted(set(snap_params.keys()) & set(curr_params.keys())):
                    if snap_params[param] != curr_params[param]:
                        changes.append(
                            f"changed param {param}: "
                            f"{snap_params[param].get('type')} -> "
                            f"{curr_params[param].get('type')}"
                        )

                if changes:
                    change_detail = "; ".join(changes)
                    diffs.append(
                        f"CHANGED method: {proto_name}.{method_name} [{change_detail}]"
                    )

    return diffs


# --- pytest fixtures and configuration ---


def pytest_addoption(parser: Any) -> None:
    """Add --update-snapshots option to pytest."""
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Update protocol signature snapshots instead of comparing.",
    )


@pytest.fixture
def update_snapshots(request: pytest.FixtureRequest) -> bool:
    """Fixture to check if snapshot update was requested."""
    return bool(request.config.getoption("--update-snapshots", default=False))


# --- Test functions ---


@pytest.mark.unit
class TestProtocolSignatureSnapshot:
    """Protocol signature snapshot tests to detect SPI contract drift."""

    def test_snapshot_matches_current_signatures(self, update_snapshots: bool) -> None:
        """Compare current protocol signatures against stored snapshot.

        When --update-snapshots is passed, updates the snapshot file instead
        of failing on differences.

        This test ensures that any change to protocol method signatures
        (additions, removals, type changes) is intentional and explicitly
        acknowledged by updating the snapshot.
        """
        current = _collect_all_protocol_signatures()

        if update_snapshots:
            _save_snapshot(current)
            pytest.skip(
                f"Snapshot updated with {len(current)} protocols at {SNAPSHOT_FILE}"
            )
            return  # pragma: no cover

        snapshot = _load_snapshot()

        if snapshot is None:
            _save_snapshot(current)
            pytest.skip(
                f"No snapshot found. Generated initial snapshot with "
                f"{len(current)} protocols at {SNAPSHOT_FILE}. "
                f"Commit this file to enable drift detection."
            )
            return  # pragma: no cover

        diffs = _diff_signatures(snapshot, current)

        if diffs:
            diff_report = "\n".join(f"  - {d}" for d in diffs)
            pytest.fail(
                f"Protocol signature drift detected!\n\n"
                f"{len(diffs)} change(s) found:\n{diff_report}\n\n"
                f"If these changes are intentional, update the snapshot:\n"
                f"  uv run pytest tests/test_protocol_snapshot.py "
                f"--update-snapshots\n\n"
                f"Then commit the updated snapshot file."
            )

    def test_all_exported_protocols_have_members(self) -> None:
        """Verify that all exported Protocol classes have at least one member.

        Protocols with zero methods or attributes provide no contract and
        should be reviewed. Both method-based and attribute-based (structural)
        protocols are valid.
        """
        import omnibase_spi.protocols as protocols_pkg

        all_names: list[str] = getattr(protocols_pkg, "__all__", [])
        empty_protocols: list[str] = []

        for name in sorted(all_names):
            obj = getattr(protocols_pkg, name, None)
            if obj is None or not isinstance(obj, type):
                continue

            # Check if it's a Protocol
            is_protocol = any(
                base.__name__ == "Protocol" and base.__module__ == "typing"
                for base in getattr(obj, "__mro__", [])
            )
            if not is_protocol:
                continue

            sig = _extract_protocol_signature(obj)
            if not sig:
                empty_protocols.append(name)

        if empty_protocols:
            pytest.fail(
                f"Found {len(empty_protocols)} protocol(s) with no "
                f"extractable members (methods or attributes): "
                f"{', '.join(empty_protocols)}"
            )

    def test_protocol_count_stability(self) -> None:
        """Verify protocol count has not dropped unexpectedly.

        A significant drop in protocol count may indicate accidental removal.
        """
        current = _collect_all_protocol_signatures()
        # The SPI currently exports 150+ protocols. A drop below 100
        # would indicate a major regression.
        assert len(current) >= 100, (
            f"Expected at least 100 protocols, found {len(current)}. "
            f"This may indicate accidental protocol removal."
        )

    def test_snapshot_includes_method_details(self) -> None:
        """Verify snapshot captures method names, parameter types, and return types.

        Ensures the snapshot mechanism is comprehensive enough to detect
        meaningful signature changes.
        """
        current = _collect_all_protocol_signatures()

        # Check a well-known protocol for expected detail
        assert "ProtocolLogger" in current, "ProtocolLogger not found in signatures"
        logger_sig = current["ProtocolLogger"]

        # ProtocolLogger should have emit, log, is_level_enabled
        assert "emit" in logger_sig, "ProtocolLogger.emit not captured"
        assert "log" in logger_sig, "ProtocolLogger.log not captured"
        assert "is_level_enabled" in logger_sig, (
            "ProtocolLogger.is_level_enabled not captured"
        )

        # Verify emit has expected structure
        emit_sig = logger_sig["emit"]
        assert "parameters" in emit_sig, "emit signature missing parameters"
        assert "return_type" in emit_sig, "emit signature missing return_type"
        assert "kind" in emit_sig, "emit signature missing kind"
        assert emit_sig["kind"] == "async_method", (
            f"emit should be async, got {emit_sig['kind']}"
        )

        # Verify parameters include type information
        params = emit_sig["parameters"]
        assert "level" in params, "emit missing 'level' parameter"
        assert "message" in params, "emit missing 'message' parameter"
        assert "correlation_id" in params, "emit missing 'correlation_id' parameter"

        # Verify parameter types are captured
        assert params["level"]["type"] != "<empty>", "emit.level type not captured"
        assert params["message"]["type"] != "<empty>", "emit.message type not captured"

    def test_snapshot_captures_properties(self) -> None:
        """Verify snapshot captures property signatures on protocols."""
        current = _collect_all_protocol_signatures()

        # ProtocolPrimitiveEffectExecutor has executor_id property
        assert "ProtocolPrimitiveEffectExecutor" in current, (
            "ProtocolPrimitiveEffectExecutor not found"
        )
        executor_sig = current["ProtocolPrimitiveEffectExecutor"]
        assert "executor_id" in executor_sig, "executor_id property not captured"
        assert executor_sig["executor_id"]["kind"] == "property", (
            f"executor_id should be property, got {executor_sig['executor_id']['kind']}"
        )


# --- CLI entry point for generating snapshots ---

if __name__ == "__main__":
    print("Generating protocol signature snapshot...")
    signatures = _collect_all_protocol_signatures()
    _save_snapshot(signatures)
    print(f"Snapshot saved to {SNAPSHOT_FILE}")
    print(f"Total protocols captured: {len(signatures)}")
    total_methods = sum(len(methods) for methods in signatures.values())
    print(f"Total methods captured: {total_methods}")
