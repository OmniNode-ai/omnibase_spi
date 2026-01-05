"""Factory implementations for omnibase_spi.

This module provides factory classes and functions for creating
default handler contracts and other SPI objects.
"""

from omnibase_spi.factories.handler_contract_factory import (
    HandlerContractFactory,
    get_default_handler_contract,
)

__all__ = [
    "HandlerContractFactory",
    "get_default_handler_contract",
]
