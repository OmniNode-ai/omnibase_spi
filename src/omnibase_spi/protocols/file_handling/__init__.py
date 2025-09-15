"""
File Handling Protocols - SPI Interface Exports.

File type processing and stamping protocols:
- File type handler for metadata stamping operations
- Protocol definitions for file processing workflows
- File reader protocol for I/O abstraction
"""

from .protocol_file_reader import ProtocolFileReader
from .protocol_file_type_handler import (
    ProtocolFileTypeHandler,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)

__all__ = [
    "ProtocolFileTypeHandler",
    "ProtocolStampOptions",
    "ProtocolValidationOptions",
    "ProtocolFileReader",
]
