# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Unit tests for the standalone protocol duplicate validator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_VALIDATION_ROOT = Path(__file__).resolve().parents[3] / "scripts" / "validation"
sys.path.insert(0, str(SCRIPTS_VALIDATION_ROOT))

from scripts.validation.validate_protocol_duplicates import (
    ProtocolClassification,
    ProtocolInfo,
    _determine_protocol_type,
    _filter_real_duplicates,
    analyze_duplicates,
)


def _protocol(
    *,
    name: str = "ProtocolStore",
    file_path: str = "src/omnibase_spi/protocols/cache/protocol_store.py",
    domain: str = "cache",
    methods: list[str] | None = None,
    properties: list[str] | None = None,
    base_protocols: list[str] | None = None,
    protocol_type: ProtocolClassification = ProtocolClassification.FUNCTIONAL,
    signature_hash: str = "same",
    line_number: int = 1,
) -> ProtocolInfo:
    return ProtocolInfo(
        name=name,
        file_path=file_path,
        module_path="omnibase_spi.protocols.cache.protocol_store",
        methods=methods if methods is not None else ["get(key: str) -> str"],
        signature_hash=signature_hash,
        line_count=1,
        imports=[],
        line_number=line_number,
        domain=domain,
        properties=properties if properties is not None else [],
        base_protocols=base_protocols if base_protocols is not None else [],
        protocol_type=protocol_type,
    )


@pytest.mark.unit
class TestProtocolClassification:
    @pytest.mark.parametrize(
        ("methods", "properties", "base_protocols", "expected"),
        [
            ([], [], [], ProtocolClassification.MARKER),
            ([], ["id: str"], [], ProtocolClassification.PROPERTY_ONLY),
            (
                ["publish(event: object) -> None"],
                [],
                ["ProtocolBasePublisher"],
                ProtocolClassification.MIXIN,
            ),
            (
                ["get(key: str) -> str"],
                [],
                [],
                ProtocolClassification.FUNCTIONAL,
            ),
        ],
    )
    def test_classifies_protocol_structure(
        self,
        methods: list[str],
        properties: list[str],
        base_protocols: list[str],
        expected: ProtocolClassification,
    ) -> None:
        assert _determine_protocol_type(methods, properties, base_protocols) is expected

    def test_protocol_info_rejects_unknown_classification(self) -> None:
        with pytest.raises(ValueError, match="Unknown protocol classification"):
            ProtocolInfo(
                name="ProtocolStore",
                file_path="src/protocol_store.py",
                module_path="protocol_store",
                methods=[],
                signature_hash="hash",
                line_count=0,
                imports=[],
                line_number=1,
                protocol_type="unknown",  # type: ignore[arg-type]
            )


@pytest.mark.unit
class TestDuplicateFiltering:
    def test_keeps_true_duplicate_in_same_domain_and_classification(self) -> None:
        first = _protocol(line_number=10)
        second = _protocol(
            file_path="src/omnibase_spi/protocols/cache/protocol_store_copy.py",
            line_number=20,
        )

        assert _filter_real_duplicates([first, second]) == [first, second]

    def test_property_only_duplicates_require_identical_properties(self) -> None:
        first = _protocol(
            methods=[],
            properties=["store_id: str"],
            protocol_type=ProtocolClassification.PROPERTY_ONLY,
            line_number=10,
        )
        second = _protocol(
            file_path="src/omnibase_spi/protocols/cache/protocol_store_copy.py",
            methods=[],
            properties=["store_id: str"],
            protocol_type=ProtocolClassification.PROPERTY_ONLY,
            line_number=20,
        )

        assert _filter_real_duplicates([first, second]) == [first, second]

    def test_domain_specific_protocols_are_not_reported_as_duplicates(self) -> None:
        cache_protocol = _protocol(domain="cache")
        event_protocol = _protocol(
            file_path="src/omnibase_spi/protocols/event_bus/protocol_store.py",
            domain="events",
        )

        analysis = analyze_duplicates([cache_protocol, event_protocol])

        assert analysis["exact_duplicates"] == {}

    def test_semantically_different_protocols_are_not_reported_as_duplicates(
        self,
    ) -> None:
        reader = _protocol(methods=["get(key: str) -> str"])
        writer = _protocol(
            file_path="src/omnibase_spi/protocols/cache/protocol_store_writer.py",
            methods=["put(key: str, value: str) -> None"],
        )

        assert _filter_real_duplicates([reader, writer]) == []
