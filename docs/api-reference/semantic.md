# Semantic Protocols

## Overview

Semantic protocols provide advanced text processing and semantic analysis capabilities.

## Protocol Categories

### Semantic Processing
- **ProtocolSemanticAnalyzer** - Semantic analysis
- **ProtocolSemanticIndexer** - Semantic indexing
- **ProtocolSemanticSearch** - Semantic search

## Usage Examples

```python
from omnibase_spi.protocols.semantic import ProtocolSemanticAnalyzer

# Initialize semantic analyzer
analyzer: ProtocolSemanticAnalyzer = get_semantic_analyzer()

# Analyze text semantics
analysis = await analyzer.analyze_text(
    text="The quick brown fox jumps over the lazy dog",
    analysis_type="sentiment"
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*
