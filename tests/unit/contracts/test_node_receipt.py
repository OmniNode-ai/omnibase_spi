# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Tests for ProtocolNodeReceipt — OMN-8748."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.services.contract_node_receipt import ProtocolNodeReceipt


@pytest.mark.unit
class TestProtocolNodeReceipt:
    def _valid(self, **overrides: object) -> dict:
        base: dict = {
            "node_id": "node-01",
            "correlation_id": uuid4(),
            "action_taken": "invoke_skill",
            "status": "success",
        }
        base.update(overrides)
        return base

    def test_minimal_success_receipt(self) -> None:
        r = ProtocolNodeReceipt(**self._valid())
        assert r.node_id == "node-01"
        assert r.status == "success"
        assert r.dry_run is False
        assert r.output == {}

    def test_frozen(self) -> None:
        r = ProtocolNodeReceipt(**self._valid())
        with pytest.raises(ValidationError):
            r.node_id = "other"  # type: ignore[misc]

    def test_failure_requires_error_type(self) -> None:
        with pytest.raises(ValidationError, match="error_type"):
            ProtocolNodeReceipt(**self._valid(status="failure", error_type=None))

    def test_failure_with_error_type_ok(self) -> None:
        r = ProtocolNodeReceipt(**self._valid(status="failure", error_type="permanent"))
        assert r.error_type == "permanent"

    def test_empty_dict_does_not_pass(self) -> None:
        with pytest.raises((ValidationError, TypeError)):
            ProtocolNodeReceipt()  # type: ignore[call-arg]

    def test_target_entity_ids_default_empty(self) -> None:
        r = ProtocolNodeReceipt(**self._valid())
        assert r.target_entity_ids == []

    def test_extra_fields_allowed(self) -> None:
        r = ProtocolNodeReceipt(**self._valid(unknown_field="x"))
        assert r.node_id == "node-01"

    def test_correlation_id_is_uuid(self) -> None:
        uid = uuid4()
        r = ProtocolNodeReceipt(**self._valid(correlation_id=uid))
        assert r.correlation_id == uid
        assert isinstance(r.correlation_id, UUID)

    def test_schema_version_default(self) -> None:
        r = ProtocolNodeReceipt(**self._valid())
        assert r.schema_version == "1.0"

    def test_dry_run_flag(self) -> None:
        r = ProtocolNodeReceipt(**self._valid(dry_run=True))
        assert r.dry_run is True

    def test_output_dict_stored(self) -> None:
        r = ProtocolNodeReceipt(**self._valid(output={"result": "ok"}))
        assert r.output["result"] == "ok"
