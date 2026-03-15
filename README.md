# omnibase_spi

Service provider interface protocols for the ONEX platform.

[![CI](https://github.com/OmniNode-ai/omnibase_spi/actions/workflows/ci.yml/badge.svg)](https://github.com/OmniNode-ai/omnibase_spi/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Install

```bash
uv add omnibase-spi
```

## Minimal Example

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusProducer

class MyProducer(ProtocolEventBusProducer):
    """Implement the event bus producer protocol."""

    async def publish(self, topic: str, payload: bytes) -> None:
        # Your implementation here
        ...
```

## Key Features

- **176+ protocol interfaces**: Runtime-checkable protocols for all ONEX service boundaries
- **22 domains**: Event bus, handlers, nodes, registry, storage, and more
- **Zero implementations**: Protocols only -- concrete implementations live in omnibase_infra
- **Structural typing**: All protocols use `@runtime_checkable` for duck typing
- **Contract-first**: Protocols define the contract, implementations fulfill it

## Documentation

- [Protocol registry](docs/api-reference/REGISTRY.md)
- [Architecture](docs/architecture/)
- [CLAUDE.md](CLAUDE.md) -- developer context and conventions
- [AGENT.md](AGENT.md) -- LLM navigation guide

## License

[MIT](LICENSE)
