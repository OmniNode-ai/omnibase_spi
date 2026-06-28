# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Unit tests for protocol_advanced_types.py.

Covers all 10 @runtime_checkable Protocol classes:
  ProtocolOutputFormat, ProtocolOutputData, ProtocolMultiVectorDocument,
  ProtocolInputDocument, ProtocolFixtureData, ProtocolSchemaDefinition,
  ProtocolContractDocument, ProtocolIndexingConfiguration,
  ProtocolAdaptiveChunk, ProtocolChunkingQualityMetrics.

Also verifies:
  - Module imports cleanly (no circular-import errors)
  - Re-exported names from protocol_agent_ai_types are present in __all__
  - Literal* type aliases resolve to str
  - Conforming stubs satisfy isinstance(); non-conforming stubs do not
  - Property return-type signatures via typing.get_type_hints()

Ticket: OMN-13742
"""

from __future__ import annotations

import importlib
from typing import Protocol, get_type_hints
from uuid import UUID

import pytest

import omnibase_spi.protocols.types.protocol_advanced_types as _mod
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

# ---------------------------------------------------------------------------
# Conforming concrete stubs — one per Protocol
# ---------------------------------------------------------------------------


class _OutputFormat:
    @property
    def format_name(self) -> str:
        return "JSON"

    @property
    def file_extension(self) -> str:
        return ".json"

    @property
    def content_type(self) -> str:
        return "application/json"

    @property
    def supports_metadata(self) -> bool:
        return True


class _OutputData:
    @property
    def content(self) -> str:
        return "data"

    @property
    def metadata(self) -> dict:
        return {}

    @property
    def format_type(self) -> _OutputFormat:
        return _OutputFormat()

    @property
    def timestamp(self) -> str:
        return "2024-01-01T00:00:00Z"

    @property
    def correlation_id(self) -> UUID:
        return UUID("00000000-0000-0000-0000-000000000001")


class _MultiVectorDocument:
    @property
    def document_id(self) -> UUID:
        return UUID("00000000-0000-0000-0000-000000000002")

    @property
    def content_vectors(self) -> dict:
        return {"content": [0.1, 0.2]}

    @property
    def metadata(self) -> dict:
        return {}

    @property
    def chunk_info(self) -> dict:
        return {}

    @property
    def embedding_models(self) -> list:
        return ["model-v1"]


class _InputDocument:
    @property
    def document_id(self) -> UUID:
        return UUID("00000000-0000-0000-0000-000000000003")

    @property
    def content(self) -> str:
        return "raw text"

    @property
    def content_type(self) -> str:
        return "text/plain"

    @property
    def metadata(self) -> dict:
        return {}

    @property
    def source_uri(self) -> str:
        return "file:///doc.txt"


class _FixtureData:
    @property
    def fixture_id(self) -> str:
        return "fix-001"

    @property
    def fixture_type(self) -> str:
        return "database"

    @property
    def data(self) -> dict:
        return {}

    @property
    def dependencies(self) -> list:
        return []

    @property
    def setup_actions(self) -> list:
        return ["truncate"]

    @property
    def teardown_actions(self) -> list:
        return ["truncate"]


class _SchemaDefinition:
    @property
    def schema_name(self) -> str:
        return "User"

    @property
    def schema_version(self) -> str:
        return "1.0.0"

    @property
    def fields(self) -> dict:
        return {}

    @property
    def validation_rules(self) -> list:
        return []

    @property
    def relationships(self) -> dict:
        return {}


class _ContractDocument:
    @property
    def contract_id(self) -> UUID:
        return UUID("00000000-0000-0000-0000-000000000004")

    @property
    def contract_type(self) -> str:
        return "SLA"

    @property
    def parties(self) -> list:
        return ["svc-a", "svc-b"]

    @property
    def terms(self) -> dict:
        return {}

    @property
    def effective_date(self) -> str:
        return "2024-01-01"

    @property
    def expiration_date(self) -> str | None:
        return None


class _IndexingConfiguration:
    @property
    def chunk_size(self) -> int:
        return 512

    @property
    def chunk_overlap(self) -> int:
        return 50

    @property
    def strategy(self) -> str:
        return "fixed"

    @property
    def metadata_extraction(self) -> bool:
        return True

    @property
    def preprocessing_options(self) -> dict:
        return {}


class _AdaptiveChunk:
    @property
    def chunk_id(self) -> UUID:
        return UUID("00000000-0000-0000-0000-000000000005")

    @property
    def content(self) -> str:
        return "chunk text"

    @property
    def start_position(self) -> int:
        return 0

    @property
    def end_position(self) -> int:
        return 512

    @property
    def metadata(self) -> dict:
        return {}

    @property
    def embedding_vector(self) -> list | None:
        return None


class _ChunkingQualityMetrics:
    @property
    def total_chunks(self) -> int:
        return 10

    @property
    def average_chunk_size(self) -> float:
        return 256.0

    @property
    def quality_score(self) -> float:
        return 0.9

    @property
    def coherence_score(self) -> float:
        return 0.85

    @property
    def semantic_density(self) -> float:
        return 0.7

    @property
    def metadata_coverage(self) -> float:
        return 0.95


# ---------------------------------------------------------------------------
# Helper: check that a Protocol is @runtime_checkable
# ---------------------------------------------------------------------------


def _is_runtime_checkable(proto: type) -> bool:
    return bool(
        getattr(proto, "__protocol_attrs__", None) is not None
        or hasattr(proto, "_is_runtime_protocol")
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestModuleImport:
    """Module can be imported and all expected names are exported."""

    def test_module_imports_cleanly(self) -> None:
        """Reimporting module raises no circular-import or other errors."""
        mod = importlib.import_module(
            "omnibase_spi.protocols.types.protocol_advanced_types"
        )
        assert mod is not None

    def test_all_contains_ten_protocol_classes(self) -> None:
        """__all__ exposes the ten Protocol classes defined in this module."""
        local_protocols = [
            "ProtocolOutputFormat",
            "ProtocolOutputData",
            "ProtocolMultiVectorDocument",
            "ProtocolInputDocument",
            "ProtocolFixtureData",
            "ProtocolSchemaDefinition",
            "ProtocolContractDocument",
            "ProtocolIndexingConfiguration",
            "ProtocolAdaptiveChunk",
            "ProtocolChunkingQualityMetrics",
        ]
        for name in local_protocols:
            assert name in _mod.__all__, f"{name!r} missing from __all__"

    def test_all_contains_reexported_agent_ai_names(self) -> None:
        """Re-exported names from protocol_agent_ai_types appear in __all__."""
        reexported = [
            "LiteralActionType",
            "ProtocolAgentAction",
            "ProtocolAgentDebugIntelligence",
            "ProtocolAIExecutionMetrics",
            "ProtocolIntelligenceResult",
            "ProtocolPRTicket",
            "ProtocolVelocityLog",
        ]
        for name in reexported:
            assert name in _mod.__all__, f"re-exported {name!r} missing from __all__"

    def test_all_contains_literal_aliases(self) -> None:
        """LiteralOutputFormat, LiteralDocumentType, etc. are in __all__."""
        aliases = [
            "LiteralOutputFormat",
            "LiteralDocumentType",
            "LiteralFixtureType",
            "LiteralContractType",
        ]
        for name in aliases:
            assert name in _mod.__all__, f"{name!r} missing from __all__"

    def test_all_names_are_importable(self) -> None:
        """Every name in __all__ is actually importable from the module."""
        for name in _mod.__all__:
            assert hasattr(_mod, name), f"{name!r} in __all__ but not found on module"


@pytest.mark.unit
class TestLiteralTypeAliases:
    """Literal* type aliases are str (per module comment: 'Would be a Literal')."""

    def test_literal_output_format_is_str(self) -> None:
        assert LiteralOutputFormat is str

    def test_literal_document_type_is_str(self) -> None:
        assert LiteralDocumentType is str

    def test_literal_fixture_type_is_str(self) -> None:
        assert LiteralFixtureType is str

    def test_literal_contract_type_is_str(self) -> None:
        assert LiteralContractType is str

    def test_literal_action_type_is_str(self) -> None:
        """Re-exported LiteralActionType is also str."""
        assert LiteralActionType is str


@pytest.mark.unit
class TestReExportedProtocols:
    """Names re-exported from protocol_agent_ai_types are accessible here."""

    def test_protocol_agent_action_is_protocol(self) -> None:
        assert issubclass(ProtocolAgentAction, Protocol)

    def test_protocol_agent_debug_intelligence_is_protocol(self) -> None:
        assert issubclass(ProtocolAgentDebugIntelligence, Protocol)

    def test_protocol_ai_execution_metrics_is_protocol(self) -> None:
        assert issubclass(ProtocolAIExecutionMetrics, Protocol)

    def test_protocol_intelligence_result_is_protocol(self) -> None:
        assert issubclass(ProtocolIntelligenceResult, Protocol)

    def test_protocol_pr_ticket_is_protocol(self) -> None:
        assert issubclass(ProtocolPRTicket, Protocol)

    def test_protocol_velocity_log_is_protocol(self) -> None:
        assert issubclass(ProtocolVelocityLog, Protocol)


@pytest.mark.unit
class TestProtocolOutputFormat:
    """ProtocolOutputFormat: runtime-checkable, 4 properties."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolOutputFormat, Protocol)

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolOutputFormat)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_OutputFormat(), ProtocolOutputFormat)

    def test_missing_file_extension_fails_isinstance(self) -> None:
        class Partial:
            @property
            def format_name(self) -> str:
                return "X"

            @property
            def content_type(self) -> str:
                return "text/plain"

            @property
            def supports_metadata(self) -> bool:
                return False

        assert not isinstance(Partial(), ProtocolOutputFormat)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolOutputFormat.__protocol_attrs__)
        assert {
            "format_name",
            "file_extension",
            "content_type",
            "supports_metadata",
        } <= attrs

    def test_format_name_return_type_is_str(self) -> None:
        prop = ProtocolOutputFormat.__dict__["format_name"]
        assert isinstance(prop, property)
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_file_extension_return_type_is_str(self) -> None:
        prop = ProtocolOutputFormat.__dict__["file_extension"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_content_type_return_type_is_str(self) -> None:
        prop = ProtocolOutputFormat.__dict__["content_type"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str


@pytest.mark.unit
class TestProtocolOutputData:
    """ProtocolOutputData: 5 properties; correlation_id -> UUID."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolOutputData)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_OutputData(), ProtocolOutputData)

    def test_missing_correlation_id_fails_isinstance(self) -> None:
        class Partial:
            @property
            def content(self) -> str:
                return ""

            @property
            def metadata(self) -> dict:
                return {}

            @property
            def format_type(self) -> object:
                return None

            @property
            def timestamp(self) -> str:
                return ""

        assert not isinstance(Partial(), ProtocolOutputData)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolOutputData.__protocol_attrs__)
        assert {
            "content",
            "metadata",
            "format_type",
            "timestamp",
            "correlation_id",
        } <= attrs

    def test_correlation_id_return_type_is_uuid(self) -> None:
        prop = ProtocolOutputData.__dict__["correlation_id"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is UUID

    def test_content_return_type_is_str(self) -> None:
        prop = ProtocolOutputData.__dict__["content"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str


@pytest.mark.unit
class TestProtocolMultiVectorDocument:
    """ProtocolMultiVectorDocument: 5 properties; document_id -> UUID."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolMultiVectorDocument)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_MultiVectorDocument(), ProtocolMultiVectorDocument)

    def test_missing_embedding_models_fails_isinstance(self) -> None:
        class Partial:
            @property
            def document_id(self) -> UUID:
                return UUID("00000000-0000-0000-0000-000000000001")

            @property
            def content_vectors(self) -> dict:
                return {}

            @property
            def metadata(self) -> dict:
                return {}

            @property
            def chunk_info(self) -> dict:
                return {}

        assert not isinstance(Partial(), ProtocolMultiVectorDocument)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolMultiVectorDocument.__protocol_attrs__)
        expected = {
            "document_id",
            "content_vectors",
            "metadata",
            "chunk_info",
            "embedding_models",
        }
        assert expected <= attrs

    def test_document_id_return_type_is_uuid(self) -> None:
        prop = ProtocolMultiVectorDocument.__dict__["document_id"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is UUID

    def test_embedding_models_return_type_origin_is_list(self) -> None:
        import typing

        prop = ProtocolMultiVectorDocument.__dict__["embedding_models"]
        hints = get_type_hints(prop.fget)
        return_type = hints["return"]
        assert typing.get_origin(return_type) is list


@pytest.mark.unit
class TestProtocolInputDocument:
    """ProtocolInputDocument: 5 properties."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolInputDocument)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_InputDocument(), ProtocolInputDocument)

    def test_missing_source_uri_fails_isinstance(self) -> None:
        class Partial:
            @property
            def document_id(self) -> UUID:
                return UUID("00000000-0000-0000-0000-000000000001")

            @property
            def content(self) -> str:
                return ""

            @property
            def content_type(self) -> str:
                return "text/plain"

            @property
            def metadata(self) -> dict:
                return {}

        assert not isinstance(Partial(), ProtocolInputDocument)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolInputDocument.__protocol_attrs__)
        assert {
            "document_id",
            "content",
            "content_type",
            "metadata",
            "source_uri",
        } <= attrs

    def test_document_id_return_type_is_uuid(self) -> None:
        prop = ProtocolInputDocument.__dict__["document_id"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is UUID

    def test_source_uri_return_type_is_str(self) -> None:
        prop = ProtocolInputDocument.__dict__["source_uri"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str


@pytest.mark.unit
class TestProtocolFixtureData:
    """ProtocolFixtureData: 6 properties."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolFixtureData)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_FixtureData(), ProtocolFixtureData)

    def test_missing_teardown_actions_fails_isinstance(self) -> None:
        class Partial:
            @property
            def fixture_id(self) -> str:
                return "x"

            @property
            def fixture_type(self) -> str:
                return "mock"

            @property
            def data(self) -> dict:
                return {}

            @property
            def dependencies(self) -> list:
                return []

            @property
            def setup_actions(self) -> list:
                return []

        assert not isinstance(Partial(), ProtocolFixtureData)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolFixtureData.__protocol_attrs__)
        expected = {
            "fixture_id",
            "fixture_type",
            "data",
            "dependencies",
            "setup_actions",
            "teardown_actions",
        }
        assert expected <= attrs

    def test_fixture_id_return_type_is_str(self) -> None:
        prop = ProtocolFixtureData.__dict__["fixture_id"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_fixture_type_return_type_is_str(self) -> None:
        prop = ProtocolFixtureData.__dict__["fixture_type"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_dependencies_return_type_origin_is_list(self) -> None:
        import typing

        prop = ProtocolFixtureData.__dict__["dependencies"]
        hints = get_type_hints(prop.fget)
        assert typing.get_origin(hints["return"]) is list


@pytest.mark.unit
class TestProtocolSchemaDefinition:
    """ProtocolSchemaDefinition: 5 properties."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolSchemaDefinition)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_SchemaDefinition(), ProtocolSchemaDefinition)

    def test_missing_relationships_fails_isinstance(self) -> None:
        class Partial:
            @property
            def schema_name(self) -> str:
                return "T"

            @property
            def schema_version(self) -> str:
                return "1.0.0"

            @property
            def fields(self) -> dict:
                return {}

            @property
            def validation_rules(self) -> list:
                return []

        assert not isinstance(Partial(), ProtocolSchemaDefinition)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolSchemaDefinition.__protocol_attrs__)
        expected = {
            "schema_name",
            "schema_version",
            "fields",
            "validation_rules",
            "relationships",
        }
        assert expected <= attrs

    def test_schema_name_return_type_is_str(self) -> None:
        prop = ProtocolSchemaDefinition.__dict__["schema_name"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_schema_version_return_type_is_str(self) -> None:
        prop = ProtocolSchemaDefinition.__dict__["schema_version"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_fields_return_type_origin_is_dict(self) -> None:
        import typing

        prop = ProtocolSchemaDefinition.__dict__["fields"]
        hints = get_type_hints(prop.fget)
        assert typing.get_origin(hints["return"]) is dict


@pytest.mark.unit
class TestProtocolContractDocument:
    """ProtocolContractDocument: 6 properties; contract_id -> UUID."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolContractDocument)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_ContractDocument(), ProtocolContractDocument)

    def test_missing_parties_fails_isinstance(self) -> None:
        class Partial:
            @property
            def contract_id(self) -> UUID:
                return UUID("00000000-0000-0000-0000-000000000001")

            @property
            def contract_type(self) -> str:
                return "API"

            @property
            def terms(self) -> dict:
                return {}

            @property
            def effective_date(self) -> str:
                return "2024-01-01"

            @property
            def expiration_date(self) -> str | None:
                return None

        assert not isinstance(Partial(), ProtocolContractDocument)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolContractDocument.__protocol_attrs__)
        expected = {
            "contract_id",
            "contract_type",
            "parties",
            "terms",
            "effective_date",
            "expiration_date",
        }
        assert expected <= attrs

    def test_contract_id_return_type_is_uuid(self) -> None:
        prop = ProtocolContractDocument.__dict__["contract_id"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is UUID

    def test_contract_type_return_type_is_str(self) -> None:
        prop = ProtocolContractDocument.__dict__["contract_type"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str

    def test_parties_return_type_origin_is_list(self) -> None:
        import typing

        prop = ProtocolContractDocument.__dict__["parties"]
        hints = get_type_hints(prop.fget)
        assert typing.get_origin(hints["return"]) is list


@pytest.mark.unit
class TestProtocolIndexingConfiguration:
    """ProtocolIndexingConfiguration: 5 properties; chunk_size/overlap -> int."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolIndexingConfiguration)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_IndexingConfiguration(), ProtocolIndexingConfiguration)

    def test_missing_strategy_fails_isinstance(self) -> None:
        class Partial:
            @property
            def chunk_size(self) -> int:
                return 512

            @property
            def chunk_overlap(self) -> int:
                return 50

            @property
            def metadata_extraction(self) -> bool:
                return True

            @property
            def preprocessing_options(self) -> dict:
                return {}

        assert not isinstance(Partial(), ProtocolIndexingConfiguration)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolIndexingConfiguration.__protocol_attrs__)
        expected = {
            "chunk_size",
            "chunk_overlap",
            "strategy",
            "metadata_extraction",
            "preprocessing_options",
        }
        assert expected <= attrs

    def test_chunk_size_return_type_is_int(self) -> None:
        prop = ProtocolIndexingConfiguration.__dict__["chunk_size"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is int

    def test_chunk_overlap_return_type_is_int(self) -> None:
        prop = ProtocolIndexingConfiguration.__dict__["chunk_overlap"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is int

    def test_strategy_return_type_is_str(self) -> None:
        prop = ProtocolIndexingConfiguration.__dict__["strategy"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str


@pytest.mark.unit
class TestProtocolAdaptiveChunk:
    """ProtocolAdaptiveChunk: 6 properties; chunk_id -> UUID."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolAdaptiveChunk)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_AdaptiveChunk(), ProtocolAdaptiveChunk)

    def test_missing_end_position_fails_isinstance(self) -> None:
        class Partial:
            @property
            def chunk_id(self) -> UUID:
                return UUID("00000000-0000-0000-0000-000000000001")

            @property
            def content(self) -> str:
                return ""

            @property
            def start_position(self) -> int:
                return 0

            @property
            def metadata(self) -> dict:
                return {}

            @property
            def embedding_vector(self) -> list | None:
                return None

        assert not isinstance(Partial(), ProtocolAdaptiveChunk)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolAdaptiveChunk.__protocol_attrs__)
        expected = {
            "chunk_id",
            "content",
            "start_position",
            "end_position",
            "metadata",
            "embedding_vector",
        }
        assert expected <= attrs

    def test_chunk_id_return_type_is_uuid(self) -> None:
        prop = ProtocolAdaptiveChunk.__dict__["chunk_id"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is UUID

    def test_start_position_return_type_is_int(self) -> None:
        prop = ProtocolAdaptiveChunk.__dict__["start_position"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is int

    def test_end_position_return_type_is_int(self) -> None:
        prop = ProtocolAdaptiveChunk.__dict__["end_position"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is int

    def test_content_return_type_is_str(self) -> None:
        prop = ProtocolAdaptiveChunk.__dict__["content"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is str


@pytest.mark.unit
class TestProtocolChunkingQualityMetrics:
    """ProtocolChunkingQualityMetrics: 6 properties; scores are float."""

    def test_is_runtime_checkable(self) -> None:
        assert _is_runtime_checkable(ProtocolChunkingQualityMetrics)

    def test_conforming_stub_satisfies_isinstance(self) -> None:
        assert isinstance(_ChunkingQualityMetrics(), ProtocolChunkingQualityMetrics)

    def test_missing_semantic_density_fails_isinstance(self) -> None:
        class Partial:
            @property
            def total_chunks(self) -> int:
                return 10

            @property
            def average_chunk_size(self) -> float:
                return 256.0

            @property
            def quality_score(self) -> float:
                return 0.9

            @property
            def coherence_score(self) -> float:
                return 0.85

            @property
            def metadata_coverage(self) -> float:
                return 0.95

        assert not isinstance(Partial(), ProtocolChunkingQualityMetrics)

    def test_has_required_attrs(self) -> None:
        attrs = set(ProtocolChunkingQualityMetrics.__protocol_attrs__)
        expected = {
            "total_chunks",
            "average_chunk_size",
            "quality_score",
            "coherence_score",
            "semantic_density",
            "metadata_coverage",
        }
        assert expected <= attrs

    def test_total_chunks_return_type_is_int(self) -> None:
        prop = ProtocolChunkingQualityMetrics.__dict__["total_chunks"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is int

    def test_quality_score_return_type_is_float(self) -> None:
        prop = ProtocolChunkingQualityMetrics.__dict__["quality_score"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is float

    def test_coherence_score_return_type_is_float(self) -> None:
        prop = ProtocolChunkingQualityMetrics.__dict__["coherence_score"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is float

    def test_semantic_density_return_type_is_float(self) -> None:
        prop = ProtocolChunkingQualityMetrics.__dict__["semantic_density"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is float

    def test_metadata_coverage_return_type_is_float(self) -> None:
        prop = ProtocolChunkingQualityMetrics.__dict__["metadata_coverage"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is float

    def test_average_chunk_size_return_type_is_float(self) -> None:
        prop = ProtocolChunkingQualityMetrics.__dict__["average_chunk_size"]
        hints = get_type_hints(prop.fget)
        assert hints["return"] is float
