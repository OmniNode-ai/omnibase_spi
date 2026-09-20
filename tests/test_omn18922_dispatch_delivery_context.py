# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""OMN-18922: the dispatch protocol accepts an optional delivery context.

Step 2 of the OMN-18918 chain, under the operator ruling selecting option C3.
Additive by construction, and these tests exist to prove that rather than to
restate the signature: the whole reason the chain is four steps landing one
repo at a time is that each step must be safe on its own.

What `delivery` is for: every in-process projection writer builds its message
metadata from `_partition`/`_offset`, the runtime injects neither, so every
snapshot delta is published at offset 0. The serving cache refuses a delta
whose offset does not exceed the one it holds for that key, and a constant
never exceeds itself, so every delta after the first per key is discarded as
a replay. Dashboard panels freeze at their oldest retained record — at zero
consumer lag, behind a green readiness endpoint (OMN-18905).
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import pytest

from omnibase_spi.protocols.runtime.protocol_dispatch_engine import (
    ProtocolDispatchEngine,
)

if TYPE_CHECKING:
    from omnibase_core.models.dispatch.model_dispatch_result import ModelDispatchResult
    from omnibase_core.models.events.model_event_envelope import ModelEventEnvelope

pytestmark = pytest.mark.unit

_METHODS = ("dispatch", "dispatch_with_transaction")


@pytest.mark.parametrize("method_name", _METHODS)
def test_delivery_is_keyword_only_with_a_none_default(method_name: str) -> None:
    """AC1. Positional would silently break every existing implementor.

    Asserted on the parameter KIND rather than on the source text, because a
    positional parameter added in the same place would read identically in a
    diff and fail only at the call sites.
    """
    signature = inspect.signature(getattr(ProtocolDispatchEngine, method_name))
    delivery = signature.parameters["delivery"]

    assert delivery.kind is inspect.Parameter.KEYWORD_ONLY
    assert delivery.default is None


@pytest.mark.parametrize("method_name", _METHODS)
def test_the_pre_existing_parameters_are_untouched(method_name: str) -> None:
    """Additive means additive: nothing was reordered or renamed.

    A rename here would be a silent break for every keyword caller, and the
    ordering matters for `dispatch`, whose first two parameters are
    positional.
    """
    signature = inspect.signature(getattr(ProtocolDispatchEngine, method_name))
    names = [n for n in signature.parameters if n != "self"]

    if method_name == "dispatch":
        assert names == ["topic", "envelope", "delivery"]
    else:
        assert names == ["topic", "envelope", "tx", "delivery"]


def test_an_implementor_that_ignores_delivery_still_satisfies_the_protocol() -> None:
    """AC2. The property that makes this landable before any implementor moves.

    `omnibase_infra`'s concrete engine is not updated until step 3, and it
    must keep satisfying the protocol in the meantime. If this ever fails,
    the chain has stopped being safe to land one repo at a time.
    """

    class LegacyEngine:
        async def dispatch(
            self, topic: str, envelope: ModelEventEnvelope[object]
        ) -> ModelDispatchResult | None:
            return None

        async def dispatch_with_transaction(
            self, *, topic: str, envelope: ModelEventEnvelope[object], tx: object
        ) -> ModelDispatchResult | None:
            return None

    assert isinstance(LegacyEngine(), ProtocolDispatchEngine)


def test_an_implementor_that_accepts_delivery_also_satisfies_the_protocol() -> None:
    """The other direction, so the runtime-checkable check is not vacuous.

    `isinstance` against a runtime-checkable Protocol tests method NAMES, not
    signatures, so on its own the test above would pass against almost
    anything. This pins that the post-step-3 shape is accepted too, and the
    signature assertions higher up carry the actual contract.
    """

    class DeliveryAwareEngine:
        async def dispatch(
            self,
            topic: str,
            envelope: ModelEventEnvelope[object],
            *,
            delivery: object | None = None,
        ) -> ModelDispatchResult | None:
            return None

        async def dispatch_with_transaction(
            self,
            *,
            topic: str,
            envelope: ModelEventEnvelope[object],
            tx: object,
            delivery: object | None = None,
        ) -> ModelDispatchResult | None:
            return None

    assert isinstance(DeliveryAwareEngine(), ProtocolDispatchEngine)


def test_the_model_is_importable_from_core_at_the_pinned_floor() -> None:
    """AC5's runtime half. The annotation is only as good as the dependency.

    The protocol references this type, so a resolve that satisfies the pin
    but predates the model would leave the annotation dangling. This is the
    check that the floor was actually raised rather than merely intended.
    """
    from omnibase_core.models.dispatch import ModelMessageDeliveryContext

    context = ModelMessageDeliveryContext(
        topic="onex.evt.omnibase-infra.runner-fleet.v1", partition=0, offset=16698
    )
    assert context.offset == 16698
    assert context.broker_timestamp is None


def test_nothing_in_this_repo_passes_delivery_yet() -> None:
    """AC4. This step cannot change behaviour on its own, and proves it.

    The walk is asserted non-empty first: a search that finds nothing because
    it looked in the wrong place is indistinguishable from a real zero.
    """
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "src"
    sources = list(src.rglob("*.py"))
    assert sources, "the walk found no sources at all — it is inert"

    callers = [
        path for path in sources if "delivery=" in path.read_text(encoding="utf-8")
    ]
    assert callers == [], [str(p) for p in callers]
