"""Protocols for managing data storage and persistence."""

from __future__ import annotations

from abc import ABC

from .protocol_database_connection import ProtocolDatabaseConnection
from .protocol_storage_backend import (
    ProtocolStorageBackend,
    ProtocolStorageBackendFactory,
)

__all__ = [
    "ProtocolDatabaseConnection",
    "ProtocolStorageBackend",
    "ProtocolStorageBackendFactory",
]
