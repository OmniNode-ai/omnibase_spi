"""
File Handling Protocols - SPI Interface Exports.

File type processing and stamping protocols:
- File type handler for metadata stamping operations
- Protocol definitions for file processing workflows
- File reader protocol for I/O abstraction
- Directory traverser for file discovery
- File writer for output operations
- File discovery source for multiple discovery strategies
- File I/O operations for unified access
- File processing for batch operations
- File type handler registry for management
"""

from .protocol_directory_traverser import ProtocolDirectoryTraverser
from .protocol_file_discovery_source import ProtocolFileDiscoverySource
from .protocol_file_io import ProtocolFileIO
from .protocol_file_processing import ProtocolFileProcessor
from .protocol_file_reader import ProtocolFileReader
from .protocol_file_type_handler import (
    ProtocolFileProcessingTypeHandler,
    ProtocolStampOptions,
    ProtocolValidationOptions,
)
from .protocol_file_type_handler_registry import ProtocolFileTypeHandlerRegistry
from .protocol_file_writer import ProtocolFileWriter

__all__ = [
    "ProtocolDirectoryTraverser",
    "ProtocolFileDiscoverySource",
    "ProtocolFileIO",
    "ProtocolFileProcessingTypeHandler",
    "ProtocolFileProcessor",
    "ProtocolFileReader",
    "ProtocolFileTypeHandlerRegistry",
    "ProtocolFileWriter",
    "ProtocolStampOptions",
    "ProtocolValidationOptions",
]
