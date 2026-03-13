# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""
LLM Protocol Interfaces

Integration protocols for Large Language Model providers and tools,
enabling consistent interfaces across different LLM implementations.

Key Protocols:
    - ProtocolLLMProvider: Base interface for LLM service providers
    - ProtocolModelRouter: Interface for model routing and selection
    - ProtocolLLMToolProvider: Interface for LLM-based tool providers

Usage Example:
    from omnibase_spi.protocols.llm import ProtocolLLMProvider

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

__all__ = [
    "ProtocolLLMProvider",
    "ProtocolLLMToolProvider",
    "ProtocolModelRouter",
]
