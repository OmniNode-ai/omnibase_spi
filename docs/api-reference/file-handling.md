# File Handling Protocols API Reference

## Overview

The ONEX file handling protocols provide comprehensive file processing capabilities for the stamper engine and distributed file operations. These protocols enable type-safe file operations, content extraction, metadata stamping, validation workflows, and sophisticated file processing pipelines with full lifecycle management.

## Protocol Architecture

The file handling domain consists of specialized protocols that provide complete file processing capabilities:

### File Type Handler Protocol

```python
from omnibase_spi.protocols.file_handling import ProtocolFileTypeHandler
from omnibase_spi.protocols.types.file_handling_types import (
    ProtocolCanHandleResult,
    ProtocolExtractedBlock,
    ProtocolSerializedBlock,
    ProtocolOnexResult
)

@runtime_checkable
class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type handlers in the ONEX stamper engine.
    
    Provides comprehensive file processing capabilities including detection,
    extraction, stamping, and validation of file metadata blocks.
    
    Features:
        - File type detection and capability assessment
        - Metadata extraction from file content
        - Block serialization for stamping operations
        - Content normalization and formatting
        - Comprehensive validation workflows
        - Pre/post validation hooks for custom logic
        - Priority-based handler selection
    """
    
    @property
    def metadata(self) -> ProtocolNodeMetadata:
        """Handler metadata information."""
        ...
    
    @property
    def node_name(self) -> str:
        """Human-readable handler name."""
        ...
    
    @property
    def node_version(self) -> ProtocolSemVer:
        """Handler version for compatibility tracking."""
        ...
    
    @property
    def node_author(self) -> str:
        """Handler author information."""
        ...
    
    @property
    def node_description(self) -> str:
        """Handler description and purpose."""
        ...
    
    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        ...
    
    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        ...
    
    @property
    def node_priority(self) -> int:
        """Handler priority for conflict resolution (higher = more priority)."""
        ...
    
    @property
    def requires_content_analysis(self) -> bool:
        """Whether handler needs file content for type determination."""
        ...
    
    def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult:
        """
        Determine if this handler can process the given file.
        
        Args:
            path: File path for extension/name analysis
            content: File content for content-based analysis
            
        Returns:
            ProtocolCanHandleResult with capability assessment
        """
        ...
    
    def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock:
        """
        Extract metadata block from file content.
        
        Args:
            path: File path for context
            content: File content to analyze
            
        Returns:
            ProtocolExtractedBlock with extracted metadata
            
        Raises:
            ExtractionError: If metadata extraction fails
        """
        ...
    
    def serialize_block(
        self, meta: ProtocolExtractedBlock
    ) -> ProtocolSerializedBlock:
        """
        Serialize metadata block for stamping.
        
        Args:
            meta: Extracted metadata block
            
        Returns:
            ProtocolSerializedBlock ready for injection
        """
        ...
    
    def normalize_rest(self, rest: str) -> str:
        """
        Normalize remaining file content after block extraction.
        
        Args:
            rest: File content after metadata block removal
            
        Returns:
            Normalized content ready for recombination
        """
        ...
    
    def stamp(
        self, path: Path, content: str, options: ProtocolStampOptions
    ) -> ProtocolOnexResult:
        """
        Stamp file with metadata block.
        
        Args:
            path: File path for stamping
            content: File content to stamp
            options: Stamping operation options
            
        Returns:
            ProtocolOnexResult with stamping results
        """
        ...
    
    def pre_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]:
        """
        Pre-validation hook for custom validation logic.
        
        Args:
            path: File path for validation
            content: File content to validate
            options: Validation options
            
        Returns:
            Optional validation result (None = continue with normal validation)
        """
        ...
    
    def post_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]:
        """
        Post-validation hook for additional validation logic.
        
        Args:
            path: File path for validation
            content: File content to validate
            options: Validation options
            
        Returns:
            Optional validation result (None = use main validation result)
        """
        ...
    
    def validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult:
        """
        Validate file content and metadata compliance.
        
        Args:
            path: File path for validation
            content: File content to validate
            options: Validation options and flags
            
        Returns:
            ProtocolOnexResult with validation results
        """
        ...
```

### Operation Options Protocols

```python
@runtime_checkable
class ProtocolStampOptions(Protocol):
    """Protocol for stamping operation options."""
    
    force: bool        # Force stamping even if metadata exists
    backup: bool       # Create backup before stamping
    dry_run: bool      # Simulate stamping without file changes

@runtime_checkable
class ProtocolValidationOptions(Protocol):
    """Protocol for validation operation options."""
    
    strict: bool       # Enable strict validation mode
    verbose: bool      # Enable verbose validation output
    check_syntax: bool # Perform syntax validation
```

## Type Definitions

### Core File Handling Types

```python
from omnibase_spi.protocols.types.file_handling_types import (
    FileOperation,
    FileStatus,
    ProcessingStatus,
    FileContent,
    ProtocolFileMetadata,
    ProtocolFileInfo,
    ProtocolFileContent,
    ProtocolProcessingResult,
    ProtocolFileFilter
)

# File operation types
FileOperation = Literal["read", "write", "append", "delete", "move", "copy"]

# File status enumeration
FileStatus = Literal["exists", "missing", "locked", "corrupted", "accessible"]

# Processing status
ProcessingStatus = BaseStatus  # "success", "error", "warning", "pending"

# File content types
FileContent = str | bytes

@runtime_checkable
class ProtocolFileMetadata(Protocol):
    """Protocol for file metadata objects."""
    
    size: int
    mime_type: str
    encoding: Optional[str]
    created_at: float
    modified_at: float

@runtime_checkable
class ProtocolFileInfo(Protocol):
    """Protocol for comprehensive file information."""
    
    file_path: Path
    file_size: int
    file_type: str
    mime_type: str
    last_modified: float
    status: FileStatus

@runtime_checkable
class ProtocolFileContent(Protocol):
    """Protocol for file content objects."""
    
    file_path: Path
    content: FileContent
    encoding: str | None
    content_hash: str
    is_binary: bool

@runtime_checkable
class ProtocolProcessingResult(Protocol):
    """Protocol for file processing results."""
    
    file_path: Path
    operation: FileOperation
    status: ProcessingStatus
    processing_time: float
    error_message: str | None
    file_metadata: ProtocolFileMetadata

@runtime_checkable
class ProtocolFileFilter(Protocol):
    """Protocol for file filtering criteria."""
    
    include_extensions: list[str]
    exclude_extensions: list[str]
    min_size: int | None
    max_size: int | None
    modified_after: float | None
    modified_before: float | None
```

### Handler-Specific Types

```python
from omnibase_spi.protocols.types.file_handling_types import (
    ProtocolCanHandleResult,
    ProtocolHandlerMetadata,
    ProtocolExtractedBlock,
    ProtocolSerializedBlock,
    ProtocolOnexResult,
    ProtocolResultData
)

@runtime_checkable
class ProtocolCanHandleResult(Protocol):
    """Protocol for can-handle determination results."""
    
    can_handle: bool
    confidence: float      # 0.0 to 1.0 confidence score
    reason: str           # Human-readable reason
    file_metadata: ProtocolFileMetadata

@runtime_checkable
class ProtocolHandlerMetadata(Protocol):
    """Protocol for comprehensive handler metadata."""
    
    name: str
    version: ProtocolSemVer
    author: str
    description: str
    supported_extensions: list[str]
    supported_filenames: list[str]
    priority: int
    requires_content_analysis: bool

@runtime_checkable
class ProtocolExtractedBlock(Protocol):
    """Protocol for extracted metadata blocks."""
    
    content: str
    file_metadata: ProtocolFileMetadata
    block_type: str
    start_line: Optional[int]
    end_line: Optional[int]
    path: Path

@runtime_checkable
class ProtocolSerializedBlock(Protocol):
    """Protocol for serialized metadata blocks."""
    
    serialized_data: str
    format: str
    version: ProtocolSemVer
    file_metadata: ProtocolFileMetadata

@runtime_checkable
class ProtocolResultData(Protocol):
    """Protocol for operation result data."""
    
    output_path: Optional[Path]
    processed_files: list[Path]
    metrics: dict[str, float]
    warnings: list[str]

@runtime_checkable
class ProtocolOnexResult(Protocol):
    """Protocol for ONEX operation results."""
    
    success: bool
    message: str
    result_data: Optional[ProtocolResultData]
    error_code: Optional[str]
    timestamp: ProtocolDateTime
```

### Behavioral Protocols

```python
@runtime_checkable
class ProtocolFileMetadataOperations(Protocol):
    """Protocol for file metadata operations."""
    
    def validate_metadata(self, metadata: ProtocolFileMetadata) -> bool:
        """Validate metadata object integrity."""
        ...
    
    def serialize_metadata(self, metadata: ProtocolFileMetadata) -> str:
        """Serialize metadata to string format."""
        ...
    
    def compare_metadata(
        self, meta1: ProtocolFileMetadata, meta2: ProtocolFileMetadata
    ) -> bool:
        """Compare two metadata objects for equality."""
        ...

@runtime_checkable
class ProtocolResultOperations(Protocol):
    """Protocol for result operations."""
    
    def format_result(self, result: ProtocolOnexResult) -> str:
        """Format result for human-readable output."""
        ...
    
    def merge_results(
        self, results: list[ProtocolOnexResult]
    ) -> ProtocolOnexResult:
        """Merge multiple results into single result."""
        ...
    
    def validate_result(self, result: ProtocolOnexResult) -> bool:
        """Validate result object integrity."""
        ...
```

## Usage Patterns

### Basic File Handler Implementation

```python
from omnibase_spi.protocols.file_handling import ProtocolFileTypeHandler
from pathlib import Path
import re

class PythonFileHandler:
    """Example Python file handler implementation."""
    
    def __init__(self):
        self._metadata = ProtocolNodeMetadata(
            name="Python File Handler",
            version=ProtocolSemVer(1, 0, 0),
            author="ONEX Team",
            description="Handles Python source files with metadata extraction"
        )
    
    @property
    def metadata(self) -> ProtocolNodeMetadata:
        return self._metadata
    
    @property
    def node_name(self) -> str:
        return "python_handler"
    
    @property
    def node_version(self) -> ProtocolSemVer:
        return self._metadata.version
    
    @property
    def node_author(self) -> str:
        return self._metadata.author
    
    @property
    def node_description(self) -> str:
        return self._metadata.description
    
    @property
    def supported_extensions(self) -> list[str]:
        return [".py", ".pyi", ".pyx"]
    
    @property
    def supported_filenames(self) -> list[str]:
        return ["setup.py", "conftest.py"]
    
    @property
    def node_priority(self) -> int:
        return 10  # High priority for Python files
    
    @property
    def requires_content_analysis(self) -> bool:
        return True  # Need content to detect Python syntax
    
    def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult:
        """Determine if file can be handled."""
        
        # Check extension first
        extension_match = path.suffix in self.supported_extensions
        filename_match = path.name in self.supported_filenames
        
        if extension_match or filename_match:
            confidence = 0.9
            reason = f"Extension {path.suffix} or filename {path.name} matches"
        else:
            # Content-based detection
            python_indicators = [
                r'^\s*import\s+\w+',
                r'^\s*from\s+\w+\s+import',
                r'^\s*def\s+\w+\s*\(',
                r'^\s*class\s+\w+',
                r'^\s*#!.*python'
            ]
            
            matches = sum(1 for pattern in python_indicators 
                         if re.search(pattern, content, re.MULTILINE))
            
            if matches >= 2:
                confidence = 0.7
                reason = f"Content analysis detected {matches} Python patterns"
            else:
                confidence = 0.1
                reason = "No strong Python indicators found"
        
        file_metadata = ProtocolFileMetadata(
            size=len(content.encode()),
            mime_type="text/x-python",
            encoding="utf-8",
            created_at=path.stat().st_ctime if path.exists() else 0,
            modified_at=path.stat().st_mtime if path.exists() else 0
        )
        
        return ProtocolCanHandleResult(
            can_handle=confidence > 0.5,
            confidence=confidence,
            reason=reason,
            file_metadata=file_metadata
        )
    
    def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock:
        """Extract metadata block from Python file."""
        
        # Look for metadata block at top of file
        metadata_pattern = r'^# === OmniNode:Metadata ===\n(.*?)\n# === /OmniNode:Metadata ===\n'
        
        match = re.search(metadata_pattern, content, re.DOTALL | re.MULTILINE)
        
        if match:
            metadata_content = match.group(1)
            start_line = content[:match.start()].count('\n')
            end_line = content[:match.end()].count('\n')
        else:
            # No existing metadata block
            metadata_content = ""
            start_line = None
            end_line = None
        
        file_metadata = ProtocolFileMetadata(
            size=len(content.encode()),
            mime_type="text/x-python",
            encoding="utf-8",
            created_at=path.stat().st_ctime if path.exists() else 0,
            modified_at=path.stat().st_mtime if path.exists() else 0
        )
        
        return ProtocolExtractedBlock(
            content=metadata_content,
            file_metadata=file_metadata,
            block_type="omninode_metadata",
            start_line=start_line,
            end_line=end_line,
            path=path
        )
    
    def serialize_block(
        self, meta: ProtocolExtractedBlock
    ) -> ProtocolSerializedBlock:
        """Serialize metadata block for stamping."""
        
        # Create YAML-formatted metadata
        metadata_lines = [
            f"# author: {self.node_author}",
            f"# version: {self.node_version}",
            f"# description: {self.node_description}",
            f"# created_at: {datetime.utcnow().isoformat()}",
            f"# file_size: {meta.file_metadata.size}",
            f"# file_path: {meta.path}",
        ]
        
        serialized_data = "# === OmniNode:Metadata ===\n"
        serialized_data += "\n".join(metadata_lines) + "\n"
        serialized_data += "# === /OmniNode:Metadata ===\n"
        
        return ProtocolSerializedBlock(
            serialized_data=serialized_data,
            format="omninode_yaml",
            version=ProtocolSemVer(1, 0, 0),
            file_metadata=meta.file_metadata
        )
    
    def normalize_rest(self, rest: str) -> str:
        """Normalize remaining content."""
        # Remove extra blank lines, ensure single newline at end
        normalized = re.sub(r'\n{3,}', '\n\n', rest)
        return normalized.rstrip() + '\n'
    
    def stamp(
        self, path: Path, content: str, options: ProtocolStampOptions
    ) -> ProtocolOnexResult:
        """Stamp Python file with metadata."""
        
        try:
            # Extract existing block
            extracted_block = self.extract_block(path, content)
            
            # Check if already stamped and not forcing
            if extracted_block.content and not options.force:
                return ProtocolOnexResult(
                    success=False,
                    message="File already contains metadata block",
                    result_data=None,
                    error_code="ALREADY_STAMPED",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Serialize new metadata block
            serialized_block = self.serialize_block(extracted_block)
            
            # Create backup if requested
            if options.backup and not options.dry_run:
                backup_path = path.with_suffix(path.suffix + '.bak')
                backup_path.write_text(content)
            
            # Combine metadata with remaining content
            if extracted_block.start_line is not None:
                # Replace existing block
                lines = content.split('\n')
                before = '\n'.join(lines[:extracted_block.start_line])
                after = '\n'.join(lines[extracted_block.end_line + 1:])
                new_content = before + serialized_block.serialized_data + after
            else:
                # Add new block at beginning
                new_content = serialized_block.serialized_data + content
            
            # Normalize content
            new_content = self.normalize_rest(new_content)
            
            # Write file if not dry run
            if not options.dry_run:
                path.write_text(new_content)
            
            result_data = ProtocolResultData(
                output_path=path,
                processed_files=[path],
                metrics={"content_size": len(new_content)},
                warnings=[]
            )
            
            return ProtocolOnexResult(
                success=True,
                message=f"Successfully stamped {path.name}",
                result_data=result_data,
                error_code=None,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            return ProtocolOnexResult(
                success=False,
                message=f"Stamping failed: {str(e)}",
                result_data=None,
                error_code="STAMPING_ERROR",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult:
        """Validate Python file."""
        
        try:
            warnings = []
            
            # Check for metadata block
            extracted_block = self.extract_block(path, content)
            if not extracted_block.content:
                if options.strict:
                    return ProtocolOnexResult(
                        success=False,
                        message="No metadata block found (strict mode)",
                        result_data=None,
                        error_code="MISSING_METADATA",
                        timestamp=datetime.utcnow().isoformat()
                    )
                else:
                    warnings.append("No metadata block found")
            
            # Syntax validation if requested
            if options.check_syntax:
                try:
                    compile(content, str(path), 'exec')
                except SyntaxError as e:
                    return ProtocolOnexResult(
                        success=False,
                        message=f"Python syntax error: {e}",
                        result_data=None,
                        error_code="SYNTAX_ERROR",
                        timestamp=datetime.utcnow().isoformat()
                    )
            
            result_data = ProtocolResultData(
                output_path=path,
                processed_files=[path],
                metrics={"validation_time": 0.1},
                warnings=warnings
            )
            
            return ProtocolOnexResult(
                success=True,
                message="Validation passed",
                result_data=result_data,
                error_code=None,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            return ProtocolOnexResult(
                success=False,
                message=f"Validation failed: {str(e)}",
                result_data=None,
                error_code="VALIDATION_ERROR",
                timestamp=datetime.utcnow().isoformat()
            )

# Usage
async def use_python_file_handler():
    """Example of using Python file handler."""
    
    handler: ProtocolFileTypeHandler = PythonFileHandler()
    
    # Test file handling capability
    test_path = Path("example.py")
    test_content = '''
import os
import sys

def hello_world():
    print("Hello, world!")

if __name__ == "__main__":
    hello_world()
'''
    
    # Check if handler can process file
    can_handle_result = handler.can_handle(test_path, test_content)
    print(f"Can handle: {can_handle_result.can_handle} (confidence: {can_handle_result.confidence:.2f})")
    print(f"Reason: {can_handle_result.reason}")
    
    if can_handle_result.can_handle:
        # Stamp the file
        stamp_options = ProtocolStampOptions(
            force=False,
            backup=True,
            dry_run=False
        )
        
        stamp_result = handler.stamp(test_path, test_content, stamp_options)
        print(f"Stamping result: {stamp_result.success}")
        print(f"Message: {stamp_result.message}")
        
        # Validate the file
        validation_options = ProtocolValidationOptions(
            strict=False,
            verbose=True,
            check_syntax=True
        )
        
        validation_result = handler.validate(test_path, test_content, validation_options)
        print(f"Validation result: {validation_result.success}")
        print(f"Message: {validation_result.message}")
```

### Multi-Handler File Processing

```python
class FileHandlerRegistry:
    """Registry for managing multiple file handlers."""
    
    def __init__(self):
        self.handlers: list[ProtocolFileTypeHandler] = []
    
    def register_handler(self, handler: ProtocolFileTypeHandler) -> None:
        """Register a file handler."""
        self.handlers.append(handler)
        # Sort by priority (higher priority first)
        self.handlers.sort(key=lambda h: h.node_priority, reverse=True)
    
    def find_best_handler(
        self, path: Path, content: str
    ) -> Optional[ProtocolFileTypeHandler]:
        """Find the best handler for a file."""
        
        best_handler = None
        best_confidence = 0.0
        
        for handler in self.handlers:
            try:
                result = handler.can_handle(path, content)
                if result.can_handle and result.confidence > best_confidence:
                    best_handler = handler
                    best_confidence = result.confidence
            except Exception as e:
                logger.warning(f"Handler {handler.node_name} failed: {e}")
                continue
        
        return best_handler
    
    def get_handlers_for_extension(
        self, extension: str
    ) -> list[ProtocolFileTypeHandler]:
        """Get all handlers that support an extension."""
        return [
            handler for handler in self.handlers
            if extension in handler.supported_extensions
        ]

# Usage
async def setup_file_handler_registry():
    """Set up file handler registry with multiple handlers."""
    
    registry = FileHandlerRegistry()
    
    # Register different file handlers
    handlers = [
        PythonFileHandler(),
        JavaScriptFileHandler(),
        MarkdownFileHandler(),
        YamlFileHandler(),
        JsonFileHandler(),
    ]
    
    for handler in handlers:
        registry.register_handler(handler)
    
    # Process a file
    file_path = Path("example.py")
    file_content = file_path.read_text()
    
    # Find best handler
    best_handler = registry.find_best_handler(file_path, file_content)
    
    if best_handler:
        print(f"Best handler: {best_handler.node_name}")
        
        # Process with best handler
        stamp_options = ProtocolStampOptions(force=False, backup=True, dry_run=False)
        result = best_handler.stamp(file_path, file_content, stamp_options)
        
        print(f"Processing result: {result.success}")
        print(f"Message: {result.message}")
    else:
        print("No suitable handler found")
    
    # Get handlers for specific extension
    python_handlers = registry.get_handlers_for_extension(".py")
    print(f"Python handlers available: {len(python_handlers)}")
    for handler in python_handlers:
        print(f"  - {handler.node_name} (priority: {handler.node_priority})")
```

### Batch File Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class BatchFileProcessor:
    """Batch processor for multiple files."""
    
    def __init__(self, registry: FileHandlerRegistry, max_workers: int = 4):
        self.registry = registry
        self.max_workers = max_workers
    
    async def process_files(
        self,
        file_paths: list[Path],
        operation: str = "stamp",
        options: dict = None
    ) -> list[ProtocolOnexResult]:
        """Process multiple files in parallel."""
        
        options = options or {}
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._process_single_file, path, operation, options)
                for path in file_paths
            ]
            
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = ProtocolOnexResult(
                        success=False,
                        message=f"Processing failed: {str(e)}",
                        result_data=None,
                        error_code="PROCESSING_ERROR",
                        timestamp=datetime.utcnow().isoformat()
                    )
                    results.append(error_result)
        
        return results
    
    def _process_single_file(
        self, path: Path, operation: str, options: dict
    ) -> ProtocolOnexResult:
        """Process a single file."""
        
        try:
            # Read file content
            content = path.read_text()
            
            # Find appropriate handler
            handler = self.registry.find_best_handler(path, content)
            
            if not handler:
                return ProtocolOnexResult(
                    success=False,
                    message=f"No suitable handler found for {path}",
                    result_data=None,
                    error_code="NO_HANDLER",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Perform requested operation
            if operation == "stamp":
                stamp_options = ProtocolStampOptions(**options)
                return handler.stamp(path, content, stamp_options)
            elif operation == "validate":
                validation_options = ProtocolValidationOptions(**options)
                return handler.validate(path, content, validation_options)
            else:
                return ProtocolOnexResult(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    result_data=None,
                    error_code="UNKNOWN_OPERATION",
                    timestamp=datetime.utcnow().isoformat()
                )
                
        except Exception as e:
            return ProtocolOnexResult(
                success=False,
                message=f"Error processing {path}: {str(e)}",
                result_data=None,
                error_code="PROCESSING_ERROR",
                timestamp=datetime.utcnow().isoformat()
            )

# Usage
async def batch_process_project_files():
    """Batch process all files in a project."""
    
    # Set up registry
    registry = FileHandlerRegistry()
    registry.register_handler(PythonFileHandler())
    registry.register_handler(JavaScriptFileHandler())
    registry.register_handler(MarkdownFileHandler())
    
    # Create batch processor
    processor = BatchFileProcessor(registry, max_workers=6)
    
    # Find all supported files
    project_root = Path(".")
    all_files = []
    
    for handler in registry.handlers:
        for extension in handler.supported_extensions:
            files = project_root.rglob(f"*{extension}")
            all_files.extend(files)
    
    # Remove duplicates
    unique_files = list(set(all_files))
    print(f"Found {len(unique_files)} files to process")
    
    # Process all files (stamp operation)
    stamp_options = {
        "force": False,
        "backup": True,
        "dry_run": False
    }
    
    start_time = time.time()
    results = await processor.process_files(
        unique_files,
        operation="stamp",
        options=stamp_options
    )
    processing_time = time.time() - start_time
    
    # Analyze results
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    print(f"Batch processing completed in {processing_time:.2f}s")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    # Report failures
    if failed > 0:
        print("\nFailures:")
        for result in results:
            if not result.success:
                print(f"  - {result.message}")
```

## Advanced Features

### Custom Handler with Hooks

```python
class AdvancedPythonHandler(PythonFileHandler):
    """Advanced Python handler with custom hooks."""
    
    def __init__(self, custom_validators: list = None):
        super().__init__()
        self.custom_validators = custom_validators or []
    
    def pre_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]:
        """Custom pre-validation logic."""
        
        # Check for specific patterns
        if "# TODO:" in content and options.strict:
            return ProtocolOnexResult(
                success=False,
                message="TODO comments found in strict mode",
                result_data=None,
                error_code="TODO_FOUND",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Check import organization
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import ')]
        if len(import_lines) > 10:
            warning_result = ProtocolOnexResult(
                success=True,
                message="Many imports found, consider reorganization",
                result_data=ProtocolResultData(
                    output_path=path,
                    processed_files=[path],
                    metrics={"import_count": len(import_lines)},
                    warnings=["Consider using import reorganization"]
                ),
                error_code=None,
                timestamp=datetime.utcnow().isoformat()
            )
            return warning_result
        
        # Continue with normal validation
        return None
    
    def post_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]:
        """Custom post-validation logic."""
        
        warnings = []
        
        # Run custom validators
        for validator in self.custom_validators:
            try:
                validator_result = validator(path, content)
                if validator_result:
                    warnings.extend(validator_result)
            except Exception as e:
                warnings.append(f"Custom validator failed: {e}")
        
        if warnings:
            return ProtocolOnexResult(
                success=True,
                message="Post-validation completed with warnings",
                result_data=ProtocolResultData(
                    output_path=path,
                    processed_files=[path],
                    metrics={"custom_validator_warnings": len(warnings)},
                    warnings=warnings
                ),
                error_code=None,
                timestamp=datetime.utcnow().isoformat()
            )
        
        return None

# Custom validators
def check_function_complexity(path: Path, content: str) -> list[str]:
    """Check for overly complex functions."""
    warnings = []
    
    lines = content.split('\n')
    current_function = None
    function_line_count = 0
    
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('def '):
            if current_function and function_line_count > 50:
                warnings.append(
                    f"Function {current_function} is {function_line_count} lines (consider breaking up)"
                )
            
            current_function = line.strip().split('(')[0].replace('def ', '')
            function_line_count = 0
        elif current_function and line.strip():
            function_line_count += 1
    
    return warnings

def check_docstring_coverage(path: Path, content: str) -> list[str]:
    """Check for missing docstrings."""
    warnings = []
    
    # Simple regex to find functions without docstrings
    function_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n(?!\s*"""|\s*\'\'\')'
    
    matches = re.finditer(function_pattern, content)
    missing_docstrings = [match.group(1) for match in matches]
    
    if missing_docstrings:
        warnings.append(
            f"Functions without docstrings: {', '.join(missing_docstrings)}"
        )
    
    return warnings

# Usage
async def use_advanced_handler():
    """Use advanced handler with custom validation."""
    
    # Create handler with custom validators
    custom_validators = [
        check_function_complexity,
        check_docstring_coverage
    ]
    
    handler = AdvancedPythonHandler(custom_validators)
    
    # Test with file
    test_path = Path("complex_example.py")
    test_content = '''
def simple_function():
    pass

def complex_function():
    # 60 lines of code here...
    pass

def undocumented_function(param1, param2):
    return param1 + param2
'''
    
    # Validate with custom logic
    validation_options = ProtocolValidationOptions(
        strict=False,
        verbose=True,
        check_syntax=True
    )
    
    result = handler.validate(test_path, test_content, validation_options)
    
    print(f"Validation result: {result.success}")
    print(f"Message: {result.message}")
    
    if result.result_data and result.result_data.warnings:
        print("Warnings:")
        for warning in result.result_data.warnings:
            print(f"  - {warning}")
```

### File Processing Pipeline

```python
from typing import Callable
from dataclasses import dataclass

@dataclass
class PipelineStage:
    """Pipeline stage configuration."""
    name: str
    processor: Callable[[Path, str], ProtocolOnexResult]
    skip_on_failure: bool = False
    required: bool = True

class FileProcessingPipeline:
    """Pipeline for multi-stage file processing."""
    
    def __init__(self):
        self.stages: list[PipelineStage] = []
        self.results_history: list[dict] = []
    
    def add_stage(
        self,
        name: str,
        processor: Callable[[Path, str], ProtocolOnexResult],
        skip_on_failure: bool = False,
        required: bool = True
    ) -> None:
        """Add a processing stage to the pipeline."""
        
        stage = PipelineStage(
            name=name,
            processor=processor,
            skip_on_failure=skip_on_failure,
            required=required
        )
        self.stages.append(stage)
    
    async def process_file(self, path: Path, content: str) -> dict:
        """Process file through all pipeline stages."""
        
        results = {
            "file_path": path,
            "total_stages": len(self.stages),
            "completed_stages": 0,
            "failed_stages": 0,
            "stage_results": [],
            "overall_success": True,
            "processing_time": 0
        }
        
        start_time = time.time()
        current_content = content
        
        for stage in self.stages:
            stage_start = time.time()
            
            try:
                # Run stage processor
                stage_result = stage.processor(path, current_content)
                stage_time = time.time() - stage_start
                
                # Record stage result
                stage_info = {
                    "stage_name": stage.name,
                    "success": stage_result.success,
                    "message": stage_result.message,
                    "processing_time": stage_time,
                    "error_code": stage_result.error_code,
                    "warnings": stage_result.result_data.warnings if stage_result.result_data else []
                }
                results["stage_results"].append(stage_info)
                
                if stage_result.success:
                    results["completed_stages"] += 1
                    
                    # Update content if stage modified it
                    if (stage_result.result_data and 
                        stage_result.result_data.output_path):
                        current_content = stage_result.result_data.output_path.read_text()
                        
                else:
                    results["failed_stages"] += 1
                    
                    # Handle failure
                    if stage.required and not stage.skip_on_failure:
                        results["overall_success"] = False
                        break
                    elif stage.skip_on_failure:
                        continue
                        
            except Exception as e:
                stage_time = time.time() - stage_start
                results["failed_stages"] += 1
                
                stage_info = {
                    "stage_name": stage.name,
                    "success": False,
                    "message": f"Stage failed with exception: {str(e)}",
                    "processing_time": stage_time,
                    "error_code": "STAGE_EXCEPTION",
                    "warnings": []
                }
                results["stage_results"].append(stage_info)
                
                if stage.required:
                    results["overall_success"] = False
                    break
        
        results["processing_time"] = time.time() - start_time
        self.results_history.append(results)
        
        return results
    
    def get_pipeline_summary(self) -> dict:
        """Get summary of pipeline performance."""
        
        if not self.results_history:
            return {"message": "No files processed yet"}
        
        total_files = len(self.results_history)
        successful_files = sum(1 for r in self.results_history if r["overall_success"])
        failed_files = total_files - successful_files
        
        avg_processing_time = sum(r["processing_time"] for r in self.results_history) / total_files
        
        # Stage performance analysis
        stage_stats = {}
        for stage in self.stages:
            stage_successes = sum(
                1 for r in self.results_history 
                for stage_result in r["stage_results"]
                if stage_result["stage_name"] == stage.name and stage_result["success"]
            )
            stage_stats[stage.name] = {
                "success_rate": stage_successes / total_files,
                "total_runs": total_files
            }
        
        return {
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "success_rate": successful_files / total_files,
            "average_processing_time": avg_processing_time,
            "stage_performance": stage_stats
        }

# Usage
async def setup_processing_pipeline():
    """Set up comprehensive file processing pipeline."""
    
    # Create pipeline
    pipeline = FileProcessingPipeline()
    
    # Set up handlers
    python_handler = PythonFileHandler()
    
    # Add pipeline stages
    pipeline.add_stage(
        name="validation",
        processor=lambda path, content: python_handler.validate(
            path, content, 
            ProtocolValidationOptions(strict=False, verbose=True, check_syntax=True)
        ),
        skip_on_failure=False,
        required=False
    )
    
    pipeline.add_stage(
        name="metadata_extraction",
        processor=lambda path, content: ProtocolOnexResult(
            success=True,
            message="Metadata extracted",
            result_data=ProtocolResultData(
                output_path=path,
                processed_files=[path],
                metrics={"metadata_blocks": 1},
                warnings=[]
            ),
            error_code=None,
            timestamp=datetime.utcnow().isoformat()
        ),
        skip_on_failure=True,
        required=False
    )
    
    pipeline.add_stage(
        name="stamping",
        processor=lambda path, content: python_handler.stamp(
            path, content,
            ProtocolStampOptions(force=False, backup=True, dry_run=False)
        ),
        skip_on_failure=False,
        required=True
    )
    
    # Process files
    test_files = [
        Path("example1.py"),
        Path("example2.py"),
        Path("example3.py")
    ]
    
    for file_path in test_files:
        if file_path.exists():
            content = file_path.read_text()
            result = await pipeline.process_file(file_path, content)
            
            print(f"\nProcessed {file_path}:")
            print(f"  Overall success: {result['overall_success']}")
            print(f"  Completed stages: {result['completed_stages']}/{result['total_stages']}")
            print(f"  Processing time: {result['processing_time']:.2f}s")
            
            # Show stage details
            for stage_result in result["stage_results"]:
                status = "✓" if stage_result["success"] else "✗"
                print(f"  {status} {stage_result['stage_name']}: {stage_result['message']}")
    
    # Show pipeline summary
    summary = pipeline.get_pipeline_summary()
    print(f"\nPipeline Summary:")
    print(f"  Files processed: {summary['total_files']}")
    print(f"  Success rate: {summary['success_rate']:.2%}")
    print(f"  Average time: {summary['average_processing_time']:.2f}s")
```

## Integration with Other Domains

### Discovery Integration

```python
from omnibase_spi.protocols.discovery import ProtocolNodeDiscoveryRegistry

async def integrate_file_handling_with_discovery(
    discovery_registry: ProtocolNodeDiscoveryRegistry
) -> FileHandlerRegistry:
    """Integrate file handling with discovery system."""
    
    # Set up discovery for file handlers
    discovery_registry.discover_and_register_nodes()
    
    # Create file handler registry
    file_registry = FileHandlerRegistry()
    
    # Register discovered handlers
    discovered_handlers = []  # Get from discovery registry
    
    for handler_info in discovered_handlers:
        # Create handler instance
        handler_instance = handler_info.node_class()
        
        # Register with file handler registry
        file_registry.register_handler(handler_instance)
    
    return file_registry
```

### Event Bus Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

class EventDrivenFileProcessor:
    """File processor that publishes events."""
    
    def __init__(self, registry: FileHandlerRegistry, event_bus: ProtocolEventBus):
        self.registry = registry
        self.event_bus = event_bus
    
    async def process_file_with_events(
        self, path: Path, content: str, operation: str
    ) -> ProtocolOnexResult:
        """Process file and publish events."""
        
        # Publish processing started event
        await self.event_bus.publish_event(
            EventMessage(
                event_id=str(uuid4()),
                event_type="file.processing.started",
                payload={
                    "file_path": str(path),
                    "operation": operation,
                    "file_size": len(content)
                },
                metadata=EventMetadata(
                    source="file_processor",
                    correlation_id=str(uuid4())
                ),
                timestamp=datetime.utcnow().isoformat()
            )
        )
        
        try:
            # Find handler
            handler = self.registry.find_best_handler(path, content)
            
            if not handler:
                # Publish no handler event
                await self.event_bus.publish_event(
                    EventMessage(
                        event_id=str(uuid4()),
                        event_type="file.processing.no_handler",
                        payload={"file_path": str(path)},
                        metadata=EventMetadata(source="file_processor"),
                        timestamp=datetime.utcnow().isoformat()
                    )
                )
                
                return ProtocolOnexResult(
                    success=False,
                    message="No handler found",
                    result_data=None,
                    error_code="NO_HANDLER",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Process file
            if operation == "stamp":
                result = handler.stamp(path, content, ProtocolStampOptions())
            elif operation == "validate":
                result = handler.validate(path, content, ProtocolValidationOptions())
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Publish completion event
            await self.event_bus.publish_event(
                EventMessage(
                    event_id=str(uuid4()),
                    event_type="file.processing.completed",
                    payload={
                        "file_path": str(path),
                        "operation": operation,
                        "success": result.success,
                        "handler_used": handler.node_name
                    },
                    metadata=EventMetadata(source="file_processor"),
                    timestamp=datetime.utcnow().isoformat()
                )
            )
            
            return result
            
        except Exception as e:
            # Publish error event
            await self.event_bus.publish_event(
                EventMessage(
                    event_id=str(uuid4()),
                    event_type="file.processing.error",
                    payload={
                        "file_path": str(path),
                        "operation": operation,
                        "error": str(e)
                    },
                    metadata=EventMetadata(source="file_processor"),
                    timestamp=datetime.utcnow().isoformat()
                )
            )
            
            raise
```

## Testing Strategies

### Handler Protocol Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestFileHandlerProtocol:
    """Test suite for file handler protocol compliance."""
    
    @pytest.fixture
    def python_handler(self):
        """Create Python handler for testing."""
        return PythonFileHandler()
    
    @pytest.fixture
    def sample_python_content(self):
        """Sample Python content for testing."""
        return '''
import os
import sys

def example_function():
    """Example function for testing."""
    return "Hello, World!"

if __name__ == "__main__":
    print(example_function())
'''
    
    def test_handler_metadata(self, python_handler):
        """Test handler metadata properties."""
        assert python_handler.node_name == "python_handler"
        assert python_handler.node_author == "ONEX Team"
        assert isinstance(python_handler.node_version, ProtocolSemVer)
        assert len(python_handler.supported_extensions) > 0
        assert python_handler.node_priority > 0
    
    def test_can_handle_python_file(self, python_handler, sample_python_content):
        """Test Python file detection."""
        test_path = Path("test.py")
        
        result = python_handler.can_handle(test_path, sample_python_content)
        
        assert isinstance(result, ProtocolCanHandleResult)
        assert result.can_handle is True
        assert result.confidence > 0.5
        assert "python" in result.reason.lower() or ".py" in result.reason
    
    def test_can_handle_non_python_file(self, python_handler):
        """Test non-Python file rejection."""
        test_path = Path("test.txt")
        test_content = "This is just plain text content."
        
        result = python_handler.can_handle(test_path, test_content)
        
        assert result.can_handle is False
        assert result.confidence < 0.5
    
    def test_extract_block(self, python_handler, sample_python_content):
        """Test metadata block extraction."""
        test_path = Path("test.py")
        
        result = python_handler.extract_block(test_path, sample_python_content)
        
        assert isinstance(result, ProtocolExtractedBlock)
        assert result.path == test_path
        assert result.block_type == "omninode_metadata"
    
    def test_serialize_block(self, python_handler):
        """Test metadata block serialization."""
        # Create extracted block
        extracted_block = Mock()
        extracted_block.content = "test content"
        extracted_block.file_metadata = Mock()
        extracted_block.file_metadata.size = 100
        extracted_block.path = Path("test.py")
        
        result = python_handler.serialize_block(extracted_block)
        
        assert isinstance(result, ProtocolSerializedBlock)
        assert "OmniNode:Metadata" in result.serialized_data
        assert result.format == "omninode_yaml"
    
    def test_stamp_operation(self, python_handler, sample_python_content, tmp_path):
        """Test file stamping operation."""
        test_file = tmp_path / "test.py"
        test_file.write_text(sample_python_content)
        
        options = ProtocolStampOptions(force=False, backup=True, dry_run=True)
        
        result = python_handler.stamp(test_file, sample_python_content, options)
        
        assert isinstance(result, ProtocolOnexResult)
        assert result.success is True
        assert "stamped" in result.message.lower()
    
    def test_validation_operation(self, python_handler, sample_python_content):
        """Test file validation."""
        test_path = Path("test.py")
        options = ProtocolValidationOptions(strict=False, verbose=True, check_syntax=True)
        
        result = python_handler.validate(test_path, sample_python_content, options)
        
        assert isinstance(result, ProtocolOnexResult)
        assert result.success is True

class TestFileHandlerRegistry:
    """Test file handler registry functionality."""
    
    @pytest.fixture
    def registry(self):
        """Create handler registry for testing."""
        return FileHandlerRegistry()
    
    @pytest.fixture
    def mock_handlers(self):
        """Create mock handlers for testing."""
        
        handler1 = Mock()
        handler1.node_name = "handler1"
        handler1.node_priority = 10
        handler1.supported_extensions = [".py"]
        handler1.can_handle.return_value = Mock(can_handle=True, confidence=0.8)
        
        handler2 = Mock()
        handler2.node_name = "handler2"
        handler2.node_priority = 20
        handler2.supported_extensions = [".py", ".pyi"]
        handler2.can_handle.return_value = Mock(can_handle=True, confidence=0.9)
        
        return [handler1, handler2]
    
    def test_register_handlers(self, registry, mock_handlers):
        """Test handler registration and priority ordering."""
        
        # Register handlers
        for handler in mock_handlers:
            registry.register_handler(handler)
        
        assert len(registry.handlers) == 2
        # Should be sorted by priority (higher first)
        assert registry.handlers[0].node_priority == 20
        assert registry.handlers[1].node_priority == 10
    
    def test_find_best_handler(self, registry, mock_handlers):
        """Test best handler selection."""
        
        for handler in mock_handlers:
            registry.register_handler(handler)
        
        test_path = Path("test.py")
        test_content = "print('hello')"
        
        best_handler = registry.find_best_handler(test_path, test_content)
        
        assert best_handler is not None
        assert best_handler.node_name == "handler2"  # Higher confidence
    
    def test_get_handlers_for_extension(self, registry, mock_handlers):
        """Test extension-based handler lookup."""
        
        for handler in mock_handlers:
            registry.register_handler(handler)
        
        py_handlers = registry.get_handlers_for_extension(".py")
        pyi_handlers = registry.get_handlers_for_extension(".pyi")
        js_handlers = registry.get_handlers_for_extension(".js")
        
        assert len(py_handlers) == 2
        assert len(pyi_handlers) == 1
        assert len(js_handlers) == 0

class TestBatchProcessing:
    """Test batch file processing functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create batch processor for testing."""
        registry = FileHandlerRegistry()
        return BatchFileProcessor(registry, max_workers=2)
    
    async def test_batch_processing(self, processor, tmp_path):
        """Test batch processing of multiple files."""
        
        # Create test files
        test_files = []
        for i in range(3):
            test_file = tmp_path / f"test_{i}.py"
            test_file.write_text(f"print('test {i}')")
            test_files.append(test_file)
        
        # Mock registry to return a working handler
        mock_handler = Mock()
        mock_handler.stamp.return_value = Mock(
            success=True,
            message="Stamped successfully"
        )
        processor.registry.find_best_handler = Mock(return_value=mock_handler)
        
        # Process files
        results = await processor.process_files(
            test_files,
            operation="stamp",
            options={"force": False, "backup": True, "dry_run": True}
        )
        
        assert len(results) == 3
        assert all(result.success for result in results)
```

## Performance Optimization

### Caching and Memoization

```python
from functools import lru_cache
import hashlib

class CachedFileHandler:
    """File handler with result caching."""
    
    def __init__(self, base_handler: ProtocolFileTypeHandler):
        self.base_handler = base_handler
        self._can_handle_cache = {}
        self._extraction_cache = {}
    
    def _get_content_hash(self, content: str) -> str:
        """Generate hash for content caching."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult:
        """Cached can_handle check."""
        
        # Create cache key
        cache_key = (str(path), self._get_content_hash(content))
        
        if cache_key in self._can_handle_cache:
            return self._can_handle_cache[cache_key]
        
        # Compute result
        result = self.base_handler.can_handle(path, content)
        
        # Cache result
        self._can_handle_cache[cache_key] = result
        
        return result
    
    def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock:
        """Cached block extraction."""
        
        cache_key = (str(path), self._get_content_hash(content))
        
        if cache_key in self._extraction_cache:
            return self._extraction_cache[cache_key]
        
        result = self.base_handler.extract_block(path, content)
        self._extraction_cache[cache_key] = result
        
        return result
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._can_handle_cache.clear()
        self._extraction_cache.clear()

# Usage
async def use_cached_handler():
    """Use cached file handler for performance."""
    
    base_handler = PythonFileHandler()
    cached_handler = CachedFileHandler(base_handler)
    
    test_path = Path("test.py")
    test_content = "print('hello')"
    
    # First call (slow)
    start_time = time.time()
    result1 = cached_handler.can_handle(test_path, test_content)
    first_time = time.time() - start_time
    
    # Second call (fast - cached)
    start_time = time.time()
    result2 = cached_handler.can_handle(test_path, test_content)
    second_time = time.time() - start_time
    
    print(f"First call: {first_time:.4f}s")
    print(f"Second call: {second_time:.4f}s (cached)")
    
    assert result1.can_handle == result2.can_handle
    assert second_time < first_time
```

### Streaming Processing

```python
import asyncio
from typing import AsyncGenerator

class StreamingFileProcessor:
    """Process files in streaming fashion for large datasets."""
    
    def __init__(self, registry: FileHandlerRegistry, chunk_size: int = 100):
        self.registry = registry
        self.chunk_size = chunk_size
    
    async def process_files_streaming(
        self,
        file_paths: AsyncGenerator[Path, None],
        operation: str = "validate"
    ) -> AsyncGenerator[ProtocolOnexResult, None]:
        """Process files in streaming chunks."""
        
        chunk = []
        async for file_path in file_paths:
            chunk.append(file_path)
            
            if len(chunk) >= self.chunk_size:
                # Process chunk
                async for result in self._process_chunk(chunk, operation):
                    yield result
                chunk = []
        
        # Process remaining files
        if chunk:
            async for result in self._process_chunk(chunk, operation):
                yield result
    
    async def _process_chunk(
        self,
        file_paths: list[Path],
        operation: str
    ) -> AsyncGenerator[ProtocolOnexResult, None]:
        """Process a chunk of files."""
        
        tasks = []
        for file_path in file_paths:
            task = asyncio.create_task(self._process_single_file(file_path, operation))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                # Convert exception to error result
                error_result = ProtocolOnexResult(
                    success=False,
                    message=f"Processing failed: {str(result)}",
                    result_data=None,
                    error_code="PROCESSING_EXCEPTION",
                    timestamp=datetime.utcnow().isoformat()
                )
                yield error_result
            else:
                yield result
    
    async def _process_single_file(
        self,
        file_path: Path,
        operation: str
    ) -> ProtocolOnexResult:
        """Process single file asynchronously."""
        
        try:
            # Read file content
            content = file_path.read_text()
            
            # Find handler
            handler = self.registry.find_best_handler(file_path, content)
            
            if not handler:
                return ProtocolOnexResult(
                    success=False,
                    message=f"No handler for {file_path}",
                    result_data=None,
                    error_code="NO_HANDLER",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Process based on operation
            if operation == "validate":
                return handler.validate(
                    file_path, content,
                    ProtocolValidationOptions(strict=False, verbose=False, check_syntax=True)
                )
            elif operation == "stamp":
                return handler.stamp(
                    file_path, content,
                    ProtocolStampOptions(force=False, backup=False, dry_run=True)
                )
            else:
                return ProtocolOnexResult(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    result_data=None,
                    error_code="UNKNOWN_OPERATION",
                    timestamp=datetime.utcnow().isoformat()
                )
                
        except Exception as e:
            return ProtocolOnexResult(
                success=False,
                message=f"Error processing {file_path}: {str(e)}",
                result_data=None,
                error_code="FILE_ERROR",
                timestamp=datetime.utcnow().isoformat()
            )

# Usage
async def process_large_project_streaming():
    """Process large project using streaming approach."""
    
    # Set up processor
    registry = FileHandlerRegistry()
    registry.register_handler(PythonFileHandler())
    
    processor = StreamingFileProcessor(registry, chunk_size=50)
    
    # Create async generator for file paths
    async def get_project_files() -> AsyncGenerator[Path, None]:
        project_root = Path("large_project")
        
        # Walk directory tree
        for file_path in project_root.rglob("*.py"):
            if file_path.is_file():
                yield file_path
                # Small delay to simulate I/O bound work
                await asyncio.sleep(0.001)
    
    # Process files in streaming fashion
    successful = 0
    failed = 0
    
    start_time = time.time()
    
    async for result in processor.process_files_streaming(
        get_project_files(),
        operation="validate"
    ):
        if result.success:
            successful += 1
        else:
            failed += 1
        
        # Progress reporting
        if (successful + failed) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (successful + failed) / elapsed
            print(f"Processed {successful + failed} files ({rate:.1f} files/sec)")
    
    total_time = time.time() - start_time
    total_files = successful + failed
    
    print(f"\nStreaming processing completed:")
    print(f"  Total files: {total_files}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Rate: {total_files / total_time:.1f} files/sec")
```

## Best Practices

### File Handler Design Guidelines

1. **Single Responsibility**: Each handler should focus on one file type or closely related types
2. **Robust Detection**: Implement both extension-based and content-based file type detection
3. **Error Handling**: Provide detailed error messages and graceful failure handling
4. **Performance**: Use caching for expensive operations like content analysis
5. **Extensibility**: Support hooks for custom validation and processing logic
6. **Metadata Rich**: Include comprehensive metadata for debugging and monitoring
7. **Atomic Operations**: Ensure file operations are atomic with proper backup strategies

### Error Handling Best Practices

1. **Specific Error Codes**: Use meaningful error codes for different failure types
2. **Detailed Messages**: Provide actionable error messages for users
3. **Graceful Degradation**: Continue processing other files when one fails
4. **Resource Cleanup**: Ensure proper cleanup of temporary files and resources

The file handling protocols provide comprehensive file processing capabilities that form the core of the ONEX stamper engine and enable sophisticated file operations with full lifecycle management and validation workflows.