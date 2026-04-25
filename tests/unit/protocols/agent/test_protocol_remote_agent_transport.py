# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Unit tests for ProtocolRemoteAgentTransport."""

from __future__ import annotations

import inspect
import typing
from collections.abc import AsyncIterator

import pytest

from omnibase_core.models.common.model_schema_value import ModelSchemaValue
from omnibase_core.models.delegation.model_agent_task_lifecycle_event import (
    ModelAgentTaskLifecycleEvent,
)
from omnibase_spi.protocols.agent.protocol_remote_agent_transport import (
    ProtocolRemoteAgentTransport,
)

pytestmark = pytest.mark.unit


def test_protocol_declares_submit_and_watch() -> None:
    members = dict(inspect.getmembers(ProtocolRemoteAgentTransport))
    assert "submit" in members
    assert "watch" in members


def test_submit_is_async_with_typed_payload() -> None:
    assert inspect.iscoroutinefunction(ProtocolRemoteAgentTransport.submit)

    hints = typing.get_type_hints(ProtocolRemoteAgentTransport.submit)
    payload_type = hints["payload"]
    assert typing.get_origin(payload_type) is dict
    assert typing.get_args(payload_type) == (str, ModelSchemaValue)
    assert hints["return"] is str


def test_watch_is_async_generator_protocol() -> None:
    sig = inspect.signature(ProtocolRemoteAgentTransport.watch)
    assert "remote_task_handle" in sig.parameters

    hints = typing.get_type_hints(ProtocolRemoteAgentTransport.watch)
    ret = hints["return"]
    assert typing.get_origin(ret) is AsyncIterator
    assert typing.get_args(ret) == (ModelAgentTaskLifecycleEvent,)
