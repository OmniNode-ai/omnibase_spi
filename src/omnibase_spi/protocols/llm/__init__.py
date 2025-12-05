"""
LLM Protocol Interfaces

Integration protocols for Large Language Model providers and tools,
enabling consistent interfaces across different LLM implementations.

Key Protocols:
    - ProtocolLLMProvider: Base interface for LLM service providers
    - ProtocolOllamaClient: Specific protocol for Ollama model service
    - ProtocolModelRouter: Interface for model routing and selection
    - ProtocolLLMToolProvider: Interface for LLM-based tool providers

Usage Example:
    from omnibase_spi.protocols.llm import ProtocolLLMProvider, ProtocolOllamaClient

    # Create implementations
    class MyLLMProvider(ProtocolLLMProvider):
        async def generate_text(self, prompt: str) -> str:
            # Implementation here
            ...
"""

from omnibase_spi.protocols.llm.protocol_llm_provider import ProtocolLLMProvider
from omnibase_spi.protocols.llm.protocol_llm_tool_provider import (
    ProtocolLLMToolProvider,
    ProtocolModelRouter,
)
from omnibase_spi.protocols.llm.protocol_ollama_client import ProtocolOllamaClient

__all__ = [
    "ProtocolLLMProvider",
    "ProtocolLLMToolProvider",
    "ProtocolModelRouter",
    "ProtocolOllamaClient",
]
