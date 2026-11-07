# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""OMN-22854: conformance of ProtocolFactSource and ProtocolFloorTicketStore, and their wire shapes.

The in-memory adapters live here, not in the package: the omnibase_spi purity gate allows no
concrete class in ``src``. Each check reads only what the protocol returns, and each suite has a
positive control: a deliberately broken adapter the suite must refuse.
"""

from collections.abc import Callable
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from omnibase_spi.contracts import services as services_contracts
from omnibase_spi.contracts.services import (
    ModelFloorTicketCreateRequest,
    ModelFloorTicketCreateResult,
    ModelFloorTicketLookupRequest,
    ModelFloorTicketLookupResult,
    ModelFloorTicketSearchRequest,
    ModelFloorTicketSearchResult,
)
from omnibase_spi.protocols.lane import ProtocolFactSource, ProtocolFloorTicketStore


class InMemoryFactSource:
    """A scripted fact source: texts by key, a brake flag and one refused class."""

    synchronous_execution = True

    def __init__(self) -> None:
        self.floor = '{"lines": []}'
        self.plans = {"alpha": "# plan alpha"}
        self.brake = False
        self.refused: dict[str, str] = {}

    def read_floor(self, url: str) -> str:
        if not url:
            raise ValueError("no url")
        return self.floor

    def read_plan(self, plans_root: str, line_id: str) -> str:
        if line_id not in self.plans:
            raise FileNotFoundError(line_id)
        return self.plans[line_id]

    def landing_only(self) -> bool:
        return self.brake

    def stop_refuses(self, task_class: str) -> str | None:
        return self.refused.get(task_class)


class _BrokenFactSource(InMemoryFactSource):
    """A source that answers an unreadable plan with an empty text instead of raising."""

    def read_plan(self, plans_root: str, line_id: str) -> str:
        return self.plans.get(line_id, "")


class InMemoryFloorTicketStore:
    """A ticket store held as a dict of ticket id to (status, floor key)."""

    synchronous_execution = True

    def __init__(self) -> None:
        self.tickets: dict[str, tuple[str, str]] = {"OMN-1": ("Backlog", "floor:a:t1")}
        self.refuse_titles: set[str] = set()

    def read(
        self, request: ModelFloorTicketLookupRequest
    ) -> ModelFloorTicketLookupResult:
        row = self.tickets.get(request.ticket)
        if row is None:
            return ModelFloorTicketLookupResult(state="missing")
        return ModelFloorTicketLookupResult(
            state="found", ticket=request.ticket, status=row[0]
        )

    def search_by_floor_key(
        self, request: ModelFloorTicketSearchRequest
    ) -> ModelFloorTicketSearchResult:
        return ModelFloorTicketSearchResult(
            state="answered",
            tickets=tuple(
                t for t, (_, key) in self.tickets.items() if key == request.floor_key
            ),
        )

    def create(
        self, request: ModelFloorTicketCreateRequest
    ) -> ModelFloorTicketCreateResult:
        if request.title in self.refuse_titles:
            return ModelFloorTicketCreateResult(state="refused", cause="gate")
        ticket = f"OMN-{len(self.tickets) + 1}"
        self.tickets[ticket] = ("Backlog", request.floor_key)
        return ModelFloorTicketCreateResult(state="created", ticket=ticket)


class _BrokenTicketStore(InMemoryFloorTicketStore):
    """search_by_floor_key matches by prefix, so one key finds another key's ticket."""

    def search_by_floor_key(
        self, request: ModelFloorTicketSearchRequest
    ) -> ModelFloorTicketSearchResult:
        return ModelFloorTicketSearchResult(
            state="answered",
            tickets=tuple(
                t
                for t, (_, key) in self.tickets.items()
                if key.startswith(request.floor_key)
            ),
        )


def _create(**overrides: Any) -> ModelFloorTicketCreateRequest:
    fields: dict[str, Any] = {
        "floor_key": "floor:a:t2",
        "title": "t2",
        "description": "Floor key: floor:a:t2",
        "parent": "OMN-9",
    }
    fields.update(overrides)
    return ModelFloorTicketCreateRequest(**fields)


def check_fact_source_is_protocol_instance(source: Any) -> None:
    assert isinstance(source, ProtocolFactSource)


def check_fact_source_answers_what_it_reads(source: Any) -> None:
    source.brake = True
    source.refused["floor-task"] = "stop-line"
    assert source.read_floor("u") == '{"lines": []}'
    assert source.read_plan("/p", "alpha") == "# plan alpha"
    assert source.landing_only() is True
    assert source.stop_refuses("floor-task") == "stop-line"
    assert source.stop_refuses("other") is None


def check_fact_source_raises_for_what_it_cannot_read(source: Any) -> None:
    with pytest.raises((OSError, LookupError, ValueError)):
        source.read_plan("/p", "missing-line")


FACT_CHECKS: tuple[Callable[[Any], None], ...] = (
    check_fact_source_is_protocol_instance,
    check_fact_source_answers_what_it_reads,
    check_fact_source_raises_for_what_it_cannot_read,
)


def check_ticket_store_is_protocol_instance(store: Any) -> None:
    assert isinstance(store, ProtocolFloorTicketStore)


def check_ticket_store_reads_found_and_missing(store: Any) -> None:
    found = store.read(ModelFloorTicketLookupRequest(ticket="OMN-1"))
    assert found.state == "found" and found.status == "Backlog"
    assert (
        store.read(ModelFloorTicketLookupRequest(ticket="OMN-404")).state == "missing"
    )


def check_ticket_store_search_matches_the_whole_key(store: Any) -> None:
    hit = store.search_by_floor_key(
        ModelFloorTicketSearchRequest(floor_key="floor:a:t1")
    )
    assert hit.state == "answered" and hit.tickets == ("OMN-1",)
    near = store.search_by_floor_key(
        ModelFloorTicketSearchRequest(floor_key="floor:a:t")
    )
    assert near.state == "answered" and near.tickets == ()


def check_ticket_store_create_then_search_finds_it(store: Any) -> None:
    created = store.create(_create())
    assert created.state == "created" and created.ticket is not None
    found = store.search_by_floor_key(
        ModelFloorTicketSearchRequest(floor_key="floor:a:t2")
    )
    assert found.tickets == (created.ticket,)


def check_ticket_store_refusal_is_typed_with_its_cause(store: Any) -> None:
    store.refuse_titles.add("bad")
    refused = store.create(_create(title="bad"))
    assert (
        refused.state == "refused"
        and refused.ticket is None
        and refused.cause == "gate"
    )


TICKET_CHECKS: tuple[Callable[[Any], None], ...] = (
    check_ticket_store_is_protocol_instance,
    check_ticket_store_reads_found_and_missing,
    check_ticket_store_search_matches_the_whole_key,
    check_ticket_store_create_then_search_finds_it,
    check_ticket_store_refusal_is_typed_with_its_cause,
)


def _ids(checks: tuple[Callable[[Any], None], ...]) -> list[str]:
    return [c.__name__.removeprefix("check_") for c in checks]


@pytest.mark.unit
@pytest.mark.parametrize("check", FACT_CHECKS, ids=_ids(FACT_CHECKS))
def test_fact_source_conformance(check: Callable[[Any], None]) -> None:
    check(InMemoryFactSource())


@pytest.mark.unit
@pytest.mark.parametrize("check", TICKET_CHECKS, ids=_ids(TICKET_CHECKS))
def test_floor_ticket_store_conformance(check: Callable[[Any], None]) -> None:
    check(InMemoryFloorTicketStore())


@pytest.mark.unit
def test_control_fact_source_suite_refuses_an_unreadable_plan_answered_as_empty() -> (
    None
):
    with pytest.raises(pytest.fail.Exception):
        check_fact_source_raises_for_what_it_cannot_read(_BrokenFactSource())


@pytest.mark.unit
def test_control_ticket_suite_refuses_a_prefix_match_on_the_floor_key() -> None:
    with pytest.raises(AssertionError):
        check_ticket_store_search_matches_the_whole_key(_BrokenTicketStore())


@pytest.mark.unit
def test_read_result_shapes() -> None:
    assert (
        ModelFloorTicketLookupResult(state="found", ticket="T", status="s").ticket
        == "T"
    )
    assert ModelFloorTicketLookupResult(state="missing").status is None
    assert ModelFloorTicketLookupResult(state="failed", cause="x").cause == "x"
    for bad in (
        {"state": "found"},
        {"state": "found", "ticket": "T", "status": "s", "cause": "x"},
        {"state": "missing", "ticket": "T"},
        {"state": "failed"},
        {"state": "failed", "cause": "x", "ticket": "T"},
    ):
        with pytest.raises(ValidationError):
            ModelFloorTicketLookupResult(**bad)


@pytest.mark.unit
def test_read_result_carries_the_facts_a_reader_judges_a_ticket_by() -> None:
    found = ModelFloorTicketLookupResult(
        state="found",
        ticket="T",
        status="Backlog",
        description="Floor key: floor:a:t1",
        project="Sprint",
        labels=("lane-created",),
        pillar="delegation",
        has_children=True,
    )
    assert found.description == "Floor key: floor:a:t1"
    assert (found.project, found.labels, found.pillar) == (
        "Sprint",
        ("lane-created",),
        "delegation",
    )
    assert found.has_children is True
    bare = ModelFloorTicketLookupResult(state="found", ticket="T", status="s")
    assert (bare.description, bare.project, bare.labels, bare.pillar) == (
        None,
        None,
        (),
        None,
    )
    assert bare.has_children is False
    for bad_facts in (
        {"state": "missing", "description": "x"},
        {"state": "missing", "labels": ("x",)},
        {"state": "failed", "cause": "x", "project": "p"},
        {"state": "failed", "cause": "x", "has_children": True},
        {"state": "failed", "cause": "x", "pillar": "p"},
    ):
        with pytest.raises(ValidationError):
            ModelFloorTicketLookupResult(**bad_facts)


@pytest.mark.unit
def test_search_and_create_result_shapes() -> None:
    assert ModelFloorTicketSearchResult(state="answered").tickets == ()
    assert ModelFloorTicketSearchResult(state="failed", cause="x").cause == "x"
    for bad_search in (
        {"state": "answered", "cause": "x"},
        {"state": "failed"},
        {"state": "failed", "cause": "x", "tickets": ("T",)},
    ):
        with pytest.raises(ValidationError):
            ModelFloorTicketSearchResult(**bad_search)
    assert ModelFloorTicketCreateResult(state="created", ticket="T").ticket == "T"
    assert ModelFloorTicketCreateResult(state="refused", cause="x").ticket is None
    for bad_create in (
        {"state": "created"},
        {"state": "created", "ticket": "T", "cause": "x"},
        {"state": "refused"},
        {"state": "failed", "cause": "x", "ticket": "T"},
    ):
        with pytest.raises(ValidationError):
            ModelFloorTicketCreateResult(**bad_create)


@pytest.mark.unit
@pytest.mark.parametrize(
    "overrides",
    [{"floor_key": ""}, {"title": ""}, {"description": ""}, {"parent": ""}],
)
def test_a_create_request_needs_every_field(overrides: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        _create(**overrides)


@pytest.mark.unit
def test_the_floor_ticket_models_are_frozen_described_and_exported() -> None:
    names = [n for n in services_contracts.__all__ if n.startswith("ModelFloorTicket")]
    assert len(names) == 6
    for name in names:
        model = getattr(services_contracts, name)
        assert issubclass(model, BaseModel)
        assert model.model_config["frozen"] is True, name
        assert model.model_config["extra"] == "forbid", name
        for field_name, field in model.model_fields.items():
            assert field.description, f"{name}.{field_name} has no description"
