"""Protocols related to Command Line Interface (CLI) operations."""

from __future__ import annotations

from .protocol_cli import ProtocolCLI, ProtocolCLIResult
from .protocol_cli_dir_fixture_case import ProtocolCLIDirFixtureCase
from .protocol_cli_dir_fixture_registry import ProtocolCLIDirFixtureRegistry
from .protocol_cli_tool_discovery import (
    ProtocolCliDiscoveredTool,
    ProtocolCLIToolDiscovery,
)
from .protocol_cli_workflow import ProtocolCliWorkflow
from .protocol_node_cli_adapter import ProtocolNodeCliAdapter

__all__ = [
    "ProtocolCLI",
    "ProtocolCLIDirFixtureCase",
    "ProtocolCLIDirFixtureRegistry",
    "ProtocolCLIResult",
    "ProtocolCLIToolDiscovery",
    "ProtocolCliDiscoveredTool",
    "ProtocolCliWorkflow",
    "ProtocolNodeCliAdapter",
]
