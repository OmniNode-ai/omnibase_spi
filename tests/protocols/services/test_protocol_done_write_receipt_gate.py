# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Contract test: omnibase_core's done-write gate handler satisfies the SPI protocols (OMN-17427).

``ProtocolDoneWriteReceiptGate`` and ``ProtocolDoneWriteReceiptQueries`` type the
public module surface of ``node_done_write_receipt_gate_compute``. The SPI source
imports no core implementation (only core models, under ``TYPE_CHECKING``); this
test imports core's handler because tests may. It pins that:

* every protocol member other than ``decide`` is exported by the handler module
  (in ``__all__``) and callable, so a rename in core fails here and not at a
  caller's contract-resolution time;
* each protocol signature equals the handler function's signature;
* a stand-in built from the handler module plus the handler class's ``handle``
  satisfies the runtime-checkable protocols, and one missing a member does not.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from omnibase_core.nodes.node_done_write_receipt_gate_compute import (
    handler_done_write_receipt_gate as handler_module,
)
from omnibase_spi.protocols.services.protocol_done_write_receipt_gate import (
    ProtocolDoneWriteReceiptGate,
)
from omnibase_spi.protocols.services.protocol_done_write_receipt_queries import (
    ProtocolDoneWriteReceiptQueries,
)

pytestmark = pytest.mark.unit

_HANDLER_CLASS = "HandlerDoneWriteReceiptGate"


def _members(protocol: type) -> tuple[str, ...]:
    return tuple(
        name
        for base in protocol.__mro__
        for name in vars(base)
        if callable(getattr(base, name))
        and not name.startswith("_")
        and name != "decide"
    )


def _core_names(signature: inspect.Signature) -> inspect.Signature:
    """Drop ``self`` and undo the protocol's import aliases for the core models."""
    aliases = {
        "ModelDoneDecision": "ModelDoneWriteDecision",
        "ModelDoneReceiptRequest": "ModelDoneWriteReceiptRequest",
    }

    def resolve(annotation: object) -> object:
        if not isinstance(annotation, str):
            return annotation
        for alias, name in aliases.items():
            annotation = annotation.replace(alias, name)
        return annotation

    parameters = [
        parameter.replace(annotation=resolve(parameter.annotation))
        for parameter in list(signature.parameters.values())[1:]
    ]
    return signature.replace(
        parameters=parameters, return_annotation=resolve(signature.return_annotation)
    )


def _gate_stand_in() -> SimpleNamespace:
    """The handler module's exports plus ``decide`` bound to the handler class."""
    exports = {
        name: getattr(handler_module, name)
        for name in _members(ProtocolDoneWriteReceiptGate)
    }
    handler = getattr(handler_module, _HANDLER_CLASS)()
    return SimpleNamespace(synchronous_execution=True, decide=handler.handle, **exports)


def test_gate_protocol_extends_the_queries_protocol() -> None:
    assert issubclass(ProtocolDoneWriteReceiptGate, ProtocolDoneWriteReceiptQueries)


def test_gate_protocol_members_are_the_documented_surface() -> None:
    assert set(_members(ProtocolDoneWriteReceiptGate)) == {
        "has_verified_bound_check",
        "as_int",
        "extract_dod_verify_verdict",
        "live_acceptance_criteria_items",
        "canonical_ac_label",
        "criterion_is_state_shaped",
        "check_records",
        "check_status",
        "ac_binding_gap",
        "verdict_is_all_verified",
        "evaluate_done_write_receipt",
    }


@pytest.mark.parametrize("name", _members(ProtocolDoneWriteReceiptGate))
def test_handler_module_exports_every_protocol_member(name: str) -> None:
    assert name in handler_module.__all__
    assert callable(getattr(handler_module, name))


@pytest.mark.parametrize("name", _members(ProtocolDoneWriteReceiptGate))
def test_protocol_signature_matches_the_handler_function(name: str) -> None:
    expected = inspect.signature(getattr(handler_module, name))
    actual = inspect.signature(getattr(ProtocolDoneWriteReceiptGate, name))
    assert _core_names(actual) == expected


def test_decide_signature_matches_the_handler_class_handle() -> None:
    expected = inspect.signature(getattr(handler_module, _HANDLER_CLASS).handle)
    actual = inspect.signature(ProtocolDoneWriteReceiptGate.decide)
    assert _core_names(actual) == _core_names(expected)


def test_handler_class_is_exported_with_handle() -> None:
    assert _HANDLER_CLASS in handler_module.__all__
    assert callable(getattr(getattr(handler_module, _HANDLER_CLASS), "handle", None))


def test_handler_surface_satisfies_both_protocols() -> None:
    stand_in = _gate_stand_in()
    assert isinstance(stand_in, ProtocolDoneWriteReceiptGate)
    assert isinstance(stand_in, ProtocolDoneWriteReceiptQueries)


def test_queries_only_object_does_not_satisfy_the_gate_protocol() -> None:
    queries_only = SimpleNamespace(
        **{
            name: getattr(handler_module, name)
            for name in _members(ProtocolDoneWriteReceiptQueries)
        }
    )
    assert isinstance(queries_only, ProtocolDoneWriteReceiptQueries)
    assert not isinstance(queries_only, ProtocolDoneWriteReceiptGate)


def test_spi_protocol_sources_import_no_core_implementation() -> None:
    root = Path(__file__).resolve().parents[3] / "src/omnibase_spi/protocols/services"
    for name in (
        "protocol_done_write_receipt_gate.py",
        "protocol_done_write_receipt_queries.py",
    ):
        source = (root / name).read_text(encoding="utf-8")
        assert "omnibase_core.nodes" not in source
