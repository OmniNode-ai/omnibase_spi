# Analytics Protocols

## Overview

Analytics protocols provide data collection and reporting capabilities for system monitoring and insights.

## Protocol Categories

### Analytics Provider
- **ProtocolAnalyticsProvider** - Analytics data collection and reporting

## Usage Examples

```python
from omnibase_spi.protocols.analytics import ProtocolAnalyticsProvider

# Initialize analytics provider
analytics: ProtocolAnalyticsProvider = get_analytics_provider()

# Collect analytics data
await analytics.collect_metrics(
    event_type="user_action",
    data={"user_id": "12345", "action": "login"}
)
```

## API Reference

- **[Core Protocols](core.md)** - System fundamentals
- **[Container Protocols](container.md)** - Dependency injection

---

*For detailed protocol documentation, see the [API Reference](README.md).*
