# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.169382'
# description: Stamped by ToolPython
# entrypoint: python://protocol_file_type_node
# hash: f865199088b42907bcfd03147a6071a4ec1c21659e83436e8b30537c67f30d6c
# last_modified_at: '2025-05-29T14:14:00.255085+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_file_type_node.py
# namespace: python://omnibase.protocol.protocol_file_type_node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4e1063a3-c759-42a8-8a3f-2d05489e0ea4
# version: 1.0.0
# === /OmniNode:Metadata ===


from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import ProtocolNodeMetadata, ProtocolSemVer
from omnibase.protocols.types.file_handling_types import (
    ProtocolCanHandleResult,
    ProtocolExtractedBlock,
    ProtocolOnexResult,
    ProtocolSerializedBlock,
)


@runtime_checkable
class ProtocolStampOptions(Protocol):
    """Protocol for stamping operation options."""

    force: bool
    backup: bool
    dry_run: bool


@runtime_checkable
class ProtocolValidationOptions(Protocol):
    """Protocol for validation operation options."""

    strict: bool
    verbose: bool
    check_syntax: bool


class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type nodes in the ONEX stamper engine.
    All methods and metadata must use canonical result models per typing_and_protocols rule.

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class NodePythonFileProcessor:
            def __init__(self):
                self._metadata = ModelNodeMetadata(
                    node_name="python",
                    version=ModelSemVer(1, 0, 0),
                    author="ONEX Team",
                    description="Python file processing node with AST-based metadata extraction",
                    supported_extensions=[".py", ".pyw"],
                    supported_filenames=["__init__.py", "setup.py"],
                    priority=100,
                    requires_content_analysis=True
                )

            @property
            def metadata(self) -> ProtocolNodeMetadata:
                return self._metadata

            @property
            def node_name(self) -> str:
                return "python"

            def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult:
                # Check file extension
                if path.suffix.lower() in ['.py', '.pyw']:
                    return ModelCanHandleResult(
                        can_handle=True,
                        confidence=0.9,
                        reason="Python file extension detected"
                    )

                # Check for Python shebang
                if content.startswith('#!/usr/bin/env python') or content.startswith('#!/usr/bin/python'):
                    return ModelCanHandleResult(
                        can_handle=True,
                        confidence=0.8,
                        reason="Python shebang detected"
                    )

                # Check for Python-specific imports
                if any(line.strip().startswith(('import ', 'from ')) for line in content.split('\n')[:10]):
                    return ModelCanHandleResult(
                        can_handle=True,
                        confidence=0.7,
                        reason="Python import statements detected"
                    )

                return ModelCanHandleResult(
                    can_handle=False,
                    confidence=0.0,
                    reason="No Python indicators found"
                )

            def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock:
                # Extract metadata using AST parsing
                try:
                    tree = ast.parse(content)

                    # Extract docstring
                    docstring = ast.get_docstring(tree) or "Python module"

                    # Extract imports, classes, functions
                    imports = [node.names[0].name for node in ast.walk(tree)
                              if isinstance(node, ast.Import)]
                    classes = [node.name for node in ast.walk(tree)
                              if isinstance(node, ast.ClassDef)]
                    functions = [node.name for node in ast.walk(tree)
                                if isinstance(node, ast.FunctionDef)]

                    metadata = {
                        "description": docstring,
                        "entrypoint": f"python://{path.stem}",
                        "imports": imports,
                        "classes": classes,
                        "functions": functions,
                        "runtime_language_hint": f"python>={sys.version_info.major}.{sys.version_info.minor}"
                    }

                    return ModelExtractedBlock(
                        success=True,
                        metadata=metadata,
                        raw_content=content,
                        normalized_content=self.normalize_rest(content)
                    )

                except SyntaxError as e:
                    return ModelExtractedBlock(
                        success=False,
                        error=f"Python syntax error: {e}",
                        raw_content=content
                    )

            def stamp(self, path: Path, content: str, options: ProtocolStampOptions) -> ProtocolOnexResult:
                # Create ONEX metadata stamp for Python file
                if options.dry_run:
                    return ModelOnexResult(
                        success=True,
                        message=f"Would stamp {path.name} with Python metadata"
                    )

                extracted = self.extract_block(path, content)
                if not extracted.success:
                    return ModelOnexResult(
                        success=False,
                        message=f"Failed to extract metadata: {extracted.error}"
                    )

                # Generate metadata block
                metadata_lines = [
                    "# === OmniNode:Metadata ===",
                    f"# author: {extracted.metadata.get('author', 'Unknown')}",
                    f"# description: {extracted.metadata.get('description', 'Python module')}",
                    f"# entrypoint: {extracted.metadata.get('entrypoint')}",
                    f"# runtime_language_hint: {extracted.metadata.get('runtime_language_hint')}",
                    f"# version: 1.0.0",
                    "# === /OmniNode:Metadata ===",
                    ""
                ]

                stamped_content = '\n'.join(metadata_lines) + content

                if not options.force and self._has_existing_stamp(content):
                    return ModelOnexResult(
                        success=False,
                        message="File already has metadata stamp. Use force=True to overwrite."
                    )

                return ModelOnexResult(
                    success=True,
                    message=f"Successfully stamped {path.name}",
                    result_content=stamped_content
                )

            def validate(self, path: Path, content: str, options: ProtocolValidationOptions) -> ProtocolOnexResult:
                # Validate Python file and its metadata
                errors = []
                warnings = []

                # Check syntax
                if options.check_syntax:
                    try:
                        ast.parse(content)
                    except SyntaxError as e:
                        errors.append(f"Python syntax error: {e}")

                # Validate metadata block if present
                if self._has_existing_stamp(content):
                    metadata_validation = self._validate_metadata_block(content)
                    errors.extend(metadata_validation.get('errors', []))
                    warnings.extend(metadata_validation.get('warnings', []))
                else:
                    warnings.append("No ONEX metadata stamp found")

                # Check for required elements
                if options.strict:
                    # Skip docstring check for now due to quote parsing issues
                    pass

                return ModelOnexResult(
                    success=len(errors) == 0,
                    message=f"Validation {'passed' if len(errors) == 0 else 'failed'}",
                    errors=errors,
                    warnings=warnings
                )

        # Usage in application
        node: ProtocolFileTypeHandler = NodePythonFileProcessor()

        # Check if node can process a file
        python_file = Path("example.py")
        with open(python_file) as f:
            content = f.read()

        can_handle = node.can_handle(python_file, content)
        if can_handle.can_handle:
            print(f"Node can process file with {can_handle.confidence} confidence: {can_handle.reason}")

            # Extract metadata
            extracted = node.extract_block(python_file, content)
            if extracted.success:
                print(f"Extracted metadata: {extracted.metadata}")

                # Stamp the file
                stamp_options = ModelStampOptions(
                    force=False,
                    backup=True,
                    dry_run=False
                )

                result = node.stamp(python_file, content, stamp_options)
                if result.success:
                    print(f"File stamped successfully: {result.message}")
                    # Write stamped content back to file
                    with open(python_file, 'w') as f:
                        f.write(result.result_content)

                # Validate the stamped file
                validation_options = ModelValidationOptions(
                    strict=True,
                    verbose=True,
                    check_syntax=True
                )

                validation = node.validate(python_file, result.result_content, validation_options)
                if validation.success:
                    print("File validation passed")
                else:
                    print(f"Validation errors: {validation.errors}")
                    print(f"Validation warnings: {validation.warnings}")
        ```

    Node Implementation Patterns:
        - File type detection: Extension-based, content-based, and heuristic analysis
        - Metadata extraction: Language-specific parsing (AST, regex, etc.)
        - Stamping workflow: Extract → Serialize → Inject → Validate
        - Validation modes: Syntax checking, metadata compliance, strict requirements
        - Error handling: Graceful degradation with detailed error messages
    """

    @property
    def metadata(self) -> ProtocolNodeMetadata: ...

    @property
    def node_name(self) -> str: ...

    @property
    def node_version(self) -> ProtocolSemVer: ...

    @property
    def node_author(self) -> str: ...

    @property
    def node_description(self) -> str: ...

    @property
    def supported_extensions(self) -> list[str]: ...

    @property
    def supported_filenames(self) -> list[str]: ...

    @property
    def node_priority(self) -> int: ...

    @property
    def requires_content_analysis(self) -> bool: ...

    def can_handle(self, path: Path, content: str) -> ProtocolCanHandleResult: ...

    def extract_block(self, path: Path, content: str) -> ProtocolExtractedBlock: ...

    def serialize_block(
        self, meta: ProtocolExtractedBlock
    ) -> ProtocolSerializedBlock: ...

    def normalize_rest(self, rest: str) -> str: ...

    def stamp(
        self, path: Path, content: str, options: ProtocolStampOptions
    ) -> ProtocolOnexResult: ...

    def pre_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]: ...

    def post_validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> Optional[ProtocolOnexResult]: ...

    def validate(
        self, path: Path, content: str, options: ProtocolValidationOptions
    ) -> ProtocolOnexResult: ...
