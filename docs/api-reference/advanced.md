# Advanced Protocols

## Overview

Advanced protocols provide sophisticated system capabilities for complex operations and specialized functionality.

## Protocol Categories

### Adaptive Processing
- **ProtocolAdaptiveChunker** - Dynamic content chunking
- **ProtocolASTBuilder** - Abstract syntax tree construction
- **ProtocolContractAnalyzer** - Contract analysis and validation

### Coverage & Testing
- **ProtocolCoverageProvider** - Code coverage analysis
- **ProtocolFixtureLoader** - Test fixture management

### Knowledge Management
- **ProtocolDirectKnowledgePipeline** - Direct knowledge processing
- **ProtocolMultiVectorIndexer** - Multi-vector indexing

### Orchestration & Output
- **ProtocolOrchestrator** - Advanced orchestration
- **ProtocolOutputFieldTool** - Output field processing
- **ProtocolOutputFormatter** - Output formatting

### Logging & Stamping
- **ProtocolLogFormatHandler** - Log format processing
- **ProtocolStamperEngine** - Document stamping engine
- **ProtocolStamper** - Document stamping

## Usage Examples

```python
from omnibase_spi.protocols.advanced import ProtocolAdaptiveChunker

# Initialize adaptive chunker
chunker: ProtocolAdaptiveChunker = get_adaptive_chunker()

# Process content with adaptive chunking
chunks = await chunker.chunk_content(
    content="Large document content...",
    max_chunk_size=1000,
    overlap=100
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection
- **[Workflow Orchestration](../api-reference/workflow-orchestration.md)** - Event-driven FSM

---

*For detailed protocol documentation, see the [API Reference](README.md).*
