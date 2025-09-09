"""
File Handling Protocols - SPI Interface Exports.

File type processing and stamping protocols:
- File type handler for metadata stamping operations
- Protocol definitions for file processing workflows
"""

from .protocol_file_type_handler import (
    ProtocolFileTypeHandler,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)

__all__ = [
    "ProtocolFileTypeHandler",
    "ProtocolStampOptions",
    "ProtocolValidationOptions",
]
