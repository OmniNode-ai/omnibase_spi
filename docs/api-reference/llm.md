# LLM Protocols

## Overview

LLM protocols provide Large Language Model integration capabilities for AI-powered operations.

## Protocol Categories

### LLM Integration
- **ProtocolLLMProvider** - LLM provider interface
- **ProtocolLLMToolProvider** - LLM tool integration
- **ProtocolOllamaClient** - Ollama client integration

## Usage Examples

```python
from omnibase_spi.protocols.llm import ProtocolLLMProvider

# Initialize LLM provider
llm: ProtocolLLMProvider = get_llm_provider()

# Generate text
response = await llm.generate_text(
    prompt="Explain the ONEX framework",
    model="gpt-4",
    max_tokens=1000
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*
