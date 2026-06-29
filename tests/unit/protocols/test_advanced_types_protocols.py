# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Unit tests for protocol_advanced_types.py."""

from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace
from typing import Protocol, get_args, get_origin, get_type_hints
from uuid import UUID

import pytest

from omnibase_spi.protocols.types.protocol_advanced_types import (
    LiteralActionType,
    LiteralContractType,
    LiteralDocumentType,
    LiteralFixtureType,
    LiteralOutputFormat,
    ProtocolAdaptiveChunk,
    ProtocolAgentAction,
    ProtocolAgentDebugIntelligence,
    ProtocolAIExecutionMetrics,
    ProtocolChunkingQualityMetrics,
    ProtocolContractDocument,
    ProtocolFixtureData,
    ProtocolIndexingConfiguration,
    ProtocolInputDocument,
    ProtocolIntelligenceResult,
    ProtocolMultiVectorDocument,
    ProtocolOutputData,
    ProtocolOutputFormat,
    ProtocolPRTicket,
    ProtocolSchemaDefinition,
    ProtocolVelocityLog,
)
from omnibase_spi.protocols.types.protocol_core_types import ContextValue

MODULE_NAME = "omnibase_spi.protocols.types.protocol_advanced_types"
UUID_VALUE = UUID("00000000-0000-0000-0000-000000000001")
NONE_TYPE = type(None)
_mod = importlib.import_module(MODULE_NAME)

LOCAL_PROTOCOL_ATTRS = {
    ProtocolOutputFormat: (
        "format_name",
        "file_extension",
        "content_type",
        "supports_metadata",
    ),
    ProtocolOutputData: (
        "content",
        "metadata",
        "format_type",
        "timestamp",
        "correlation_id",
    ),
    ProtocolMultiVectorDocument: (
        "document_id",
        "content_vectors",
        "metadata",
        "chunk_info",
        "embedding_models",
    ),
    ProtocolInputDocument: (
        "document_id",
        "content",
        "content_type",
        "metadata",
        "source_uri",
    ),
    ProtocolFixtureData: (
        "fixture_id",
        "fixture_type",
        "data",
        "dependencies",
        "setup_actions",
        "teardown_actions",
    ),
    ProtocolSchemaDefinition: (
        "schema_name",
        "schema_version",
        "fields",
        "validation_rules",
        "relationships",
    ),
    ProtocolContractDocument: (
        "contract_id",
        "contract_type",
        "parties",
        "terms",
        "effective_date",
        "expiration_date",
    ),
    ProtocolIndexingConfiguration: (
        "chunk_size",
        "chunk_overlap",
        "strategy",
        "metadata_extraction",
        "preprocessing_options",
    ),
    ProtocolAdaptiveChunk: (
        "chunk_id",
        "content",
        "start_position",
        "end_position",
        "metadata",
        "embedding_vector",
    ),
    ProtocolChunkingQualityMetrics: (
        "total_chunks",
        "average_chunk_size",
        "quality_score",
        "coherence_score",
        "semantic_density",
        "metadata_coverage",
    ),
}

VALUE_BY_ATTR = {
    "format_name": "JSON",
    "file_extension": ".json",
    "content_type": "text/plain",
    "supports_metadata": True,
    "content": "content",
    "metadata": {},
    "format_type": SimpleNamespace(
        format_name="JSON",
        file_extension=".json",
        content_type="application/json",
        supports_metadata=True,
    ),
    "timestamp": "2024-01-01T00:00:00Z",
    "correlation_id": UUID_VALUE,
    "document_id": UUID_VALUE,
    "content_vectors": {"content": [0.1, 0.2]},
    "chunk_info": {},
    "embedding_models": ["model-v1"],
    "source_uri": "file:///doc.txt",
    "fixture_id": "fixture-001",
    "fixture_type": "database",
    "data": {},
    "dependencies": [],
    "setup_actions": ["truncate"],
    "teardown_actions": ["truncate"],
    "schema_name": "User",
    "schema_version": "1.0.0",
    "fields": {},
    "validation_rules": [],
    "relationships": {},
    "contract_id": UUID_VALUE,
    "contract_type": "SLA",
    "parties": ["svc-a", "svc-b"],
    "terms": {},
    "effective_date": "2024-01-01",
    "expiration_date": None,
    "chunk_size": 512,
    "chunk_overlap": 50,
    "strategy": "fixed",
    "metadata_extraction": True,
    "preprocessing_options": {},
    "chunk_id": UUID_VALUE,
    "start_position": 0,
    "end_position": 512,
    "embedding_vector": None,
    "total_chunks": 10,
    "average_chunk_size": 256.0,
    "quality_score": 0.9,
    "coherence_score": 0.85,
    "semantic_density": 0.7,
    "metadata_coverage": 0.95,
}

RETURN_EXPECTATIONS = {
    ProtocolOutputFormat: {
        "format_name": str,
        "file_extension": str,
        "content_type": str,
        "supports_metadata": bool,
    },
    ProtocolOutputData: {
        "content": str,
        "metadata": dict[str, ContextValue],
        "format_type": ProtocolOutputFormat,
        "timestamp": str,
        "correlation_id": UUID,
    },
    ProtocolMultiVectorDocument: {
        "document_id": UUID,
        "content_vectors": dict[str, list[float]],
        "metadata": dict[str, ContextValue],
        "chunk_info": dict[str, ContextValue],
        "embedding_models": list[str],
    },
    ProtocolInputDocument: {
        "document_id": UUID,
        "content": str,
        "content_type": str,
        "metadata": dict[str, ContextValue],
        "source_uri": str,
    },
    ProtocolFixtureData: {
        "fixture_id": str,
        "fixture_type": str,
        "data": dict[str, ContextValue],
        "dependencies": list[str],
        "setup_actions": list[str],
        "teardown_actions": list[str],
    },
    ProtocolSchemaDefinition: {
        "schema_name": str,
        "schema_version": str,
        "fields": dict[str, ContextValue],
        "validation_rules": list[dict[str, ContextValue]],
        "relationships": dict[str, ContextValue],
    },
    ProtocolContractDocument: {
        "contract_id": UUID,
        "contract_type": str,
        "parties": list[str],
        "terms": dict[str, ContextValue],
        "effective_date": str,
        "expiration_date": str | None,
    },
    ProtocolIndexingConfiguration: {
        "chunk_size": int,
        "chunk_overlap": int,
        "strategy": str,
        "metadata_extraction": bool,
        "preprocessing_options": dict[str, ContextValue],
    },
    ProtocolAdaptiveChunk: {
        "chunk_id": UUID,
        "content": str,
        "start_position": int,
        "end_position": int,
        "metadata": dict[str, ContextValue],
        "embedding_vector": list[float] | None,
    },
    ProtocolChunkingQualityMetrics: {
        "total_chunks": int,
        "average_chunk_size": float,
        "quality_score": float,
        "coherence_score": float,
        "semantic_density": float,
        "metadata_coverage": float,
    },
}

LOCAL_PROTOCOLS = tuple(LOCAL_PROTOCOL_ATTRS)
REEXPORTED_PROTOCOLS = (
    ProtocolAgentAction,
    ProtocolAgentDebugIntelligence,
    ProtocolAIExecutionMetrics,
    ProtocolIntelligenceResult,
    ProtocolPRTicket,
    ProtocolVelocityLog,
)
LITERAL_ALIASES = (
    LiteralOutputFormat,
    LiteralDocumentType,
    LiteralFixtureType,
    LiteralContractType,
    LiteralActionType,
)
RETURN_CASES = tuple(
    pytest.param(proto, attr, expected, id=f"{proto.__name__}.{attr}")
    for proto, expectations in RETURN_EXPECTATIONS.items()
    for attr, expected in expectations.items()
)


def _container_for(proto: type) -> SimpleNamespace:
    return SimpleNamespace(
        **{attr: VALUE_BY_ATTR[attr] for attr in LOCAL_PROTOCOL_ATTRS[proto]}
    )


def _container_missing(proto: type, missing_attr: str) -> SimpleNamespace:
    return SimpleNamespace(
        **{
            attr: VALUE_BY_ATTR[attr]
            for attr in LOCAL_PROTOCOL_ATTRS[proto]
            if attr != missing_attr
        }
    )


def _is_runtime_checkable(proto: type) -> bool:
    return bool(getattr(proto, "_is_runtime_protocol", False))


def _matches_expected_return(return_type: object, expected: object) -> bool:
    if return_type == expected:
        return True

    expected_origin = get_origin(expected)
    return_origin = get_origin(return_type)

    if expected_origin is types.UnionType:
        args = get_args(expected)
        if NONE_TYPE in args and len(args) == 2:
            concrete = next(arg for arg in args if arg is not NONE_TYPE)
            if return_origin is not types.UnionType:
                return False
            return_args = get_args(return_type)
            non_none_return = next(arg for arg in return_args if arg is not NONE_TYPE)
            return NONE_TYPE in return_args and _matches_expected_return(
                non_none_return, concrete
            )

    if expected_origin is not None:
        if return_origin is not expected_origin:
            return False
        return_args = get_args(return_type)
        expected_args = get_args(expected)
        return len(return_args) == len(expected_args) and all(
            _matches_expected_return(actual, wanted)
            for actual, wanted in zip(return_args, expected_args, strict=True)
        )

    return return_type is expected


@pytest.mark.unit
class TestModuleImport:
    """Module can be imported and all expected names are exported."""

    def test_module_imports_cleanly(self) -> None:
        """Fresh import raises no circular-import or other errors."""
        original = sys.modules.pop(MODULE_NAME, None)
        try:
            mod = importlib.import_module(MODULE_NAME)
            assert mod is not None
        finally:
            if original is not None:
                sys.modules[MODULE_NAME] = original

    def test_all_contains_ten_protocol_classes(self) -> None:
        for proto in LOCAL_PROTOCOLS:
            assert proto.__name__ in _mod.__all__, f"{proto.__name__!r} missing"

    def test_all_contains_reexported_agent_ai_names(self) -> None:
        for proto in REEXPORTED_PROTOCOLS:
            assert proto.__name__ in _mod.__all__, f"{proto.__name__!r} missing"

    def test_all_contains_literal_aliases(self) -> None:
        aliases = [
            "LiteralActionType",
            "LiteralOutputFormat",
            "LiteralDocumentType",
            "LiteralFixtureType",
            "LiteralContractType",
        ]
        for name in aliases:
            assert name in _mod.__all__, f"{name!r} missing from __all__"

    def test_all_names_are_importable(self) -> None:
        for name in _mod.__all__:
            assert hasattr(_mod, name), f"{name!r} in __all__ but not found"


@pytest.mark.unit
@pytest.mark.parametrize("alias", LITERAL_ALIASES)
def test_literal_type_aliases_are_str(alias: object) -> None:
    assert alias is str


@pytest.mark.unit
@pytest.mark.parametrize("proto", REEXPORTED_PROTOCOLS)
def test_reexported_agent_ai_names_are_protocols(proto: type) -> None:
    assert issubclass(proto, Protocol)


@pytest.mark.unit
@pytest.mark.parametrize("proto", LOCAL_PROTOCOLS)
def test_local_protocols_are_protocols(proto: type) -> None:
    assert issubclass(proto, Protocol)


@pytest.mark.unit
@pytest.mark.parametrize("proto", LOCAL_PROTOCOLS)
def test_local_protocols_are_runtime_checkable(proto: type) -> None:
    assert _is_runtime_checkable(proto)


@pytest.mark.unit
@pytest.mark.parametrize("proto", LOCAL_PROTOCOLS)
def test_anonymous_container_satisfies_protocol(proto: type) -> None:
    assert isinstance(_container_for(proto), proto)


@pytest.mark.unit
@pytest.mark.parametrize("proto", LOCAL_PROTOCOLS)
def test_missing_required_attr_fails_isinstance(proto: type) -> None:
    missing_attr = LOCAL_PROTOCOL_ATTRS[proto][-1]
    assert not isinstance(_container_missing(proto, missing_attr), proto)


@pytest.mark.unit
@pytest.mark.parametrize("proto", LOCAL_PROTOCOLS)
def test_protocol_attrs_contain_all_declared_properties(proto: type) -> None:
    assert set(LOCAL_PROTOCOL_ATTRS[proto]) <= set(proto.__protocol_attrs__)


@pytest.mark.unit
@pytest.mark.parametrize(("proto", "attr", "expected"), RETURN_CASES)
def test_protocol_property_return_hints(
    proto: type, attr: str, expected: object
) -> None:
    prop = proto.__dict__[attr]
    assert isinstance(prop, property)
    assert prop.fget is not None
    return_type = get_type_hints(prop.fget)["return"]
    assert _matches_expected_return(return_type, expected)
