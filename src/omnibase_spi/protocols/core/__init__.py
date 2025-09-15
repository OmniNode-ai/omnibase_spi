"""
Core Protocol Interfaces

System-level contracts for serialization, schema loading, workflow processing,
logging, node registry, and other core functionality supporting the ONEX 
Messaging Design v0.3.
"""

from omnibase_spi.protocols.core.protocol_cache_service import (
    ProtocolCacheService,
    ProtocolCacheServiceProvider,
)
from omnibase_spi.protocols.core.protocol_client_config import (
    ProtocolClientConfigProvider,
    ProtocolHttpAuthConfig,
    ProtocolHttpClientConfig,
    ProtocolKafkaClientConfig,
    ProtocolKafkaConsumerConfig,
    ProtocolKafkaProducerConfig,
)
from omnibase_spi.protocols.core.protocol_http_client import (
    ProtocolHttpClient,
    ProtocolHttpClientProvider,
    ProtocolHttpResponse,
)
from omnibase_spi.protocols.core.protocol_http_extended import (
    ProtocolHttpExtendedClient,
    ProtocolHttpRequestBuilder,
    ProtocolHttpStreamingResponse,
)
from omnibase_spi.protocols.core.protocol_kafka_client import (
    ProtocolKafkaClient,
    ProtocolKafkaClientProvider,
)
from omnibase_spi.protocols.core.protocol_kafka_extended import (
    ProtocolKafkaBatchProducer,
    ProtocolKafkaConsumer,
    ProtocolKafkaExtendedClient,
    ProtocolKafkaMessage,
    ProtocolKafkaTransactionalProducer,
)
from omnibase_spi.protocols.core.protocol_logger import ProtocolLogger
from omnibase_spi.protocols.core.protocol_node_configuration import (
    ProtocolConfigurationError,
    ProtocolNodeConfiguration,
    ProtocolNodeConfigurationProvider,
)
from omnibase_spi.protocols.core.protocol_node_configuration_utils import (
    ProtocolUtilsNodeConfiguration,
)
from omnibase_spi.protocols.core.protocol_node_registry import (
    ProtocolNodeInfo,
    ProtocolNodeRegistry,
)
from omnibase_spi.protocols.core.protocol_workflow_reducer import (
    ProtocolWorkflowReducer,
)

__all__ = [
    # Advanced workflow protocols
    "ProtocolWorkflowReducer",
    # Node discovery and registry
    "ProtocolNodeInfo",
    "ProtocolNodeRegistry",
    # Configuration protocols
    "ProtocolNodeConfiguration",
    "ProtocolNodeConfigurationProvider",
    "ProtocolUtilsNodeConfiguration",
    "ProtocolConfigurationError",
    # Cache service protocols
    "ProtocolCacheService",
    "ProtocolCacheServiceProvider",
    # Client configuration protocols
    "ProtocolClientConfigProvider",
    "ProtocolHttpClientConfig",
    "ProtocolHttpAuthConfig",
    "ProtocolKafkaClientConfig",
    "ProtocolKafkaProducerConfig",
    "ProtocolKafkaConsumerConfig",
    # HTTP client protocols
    "ProtocolHttpResponse",
    "ProtocolHttpClient",
    "ProtocolHttpClientProvider",
    # Extended HTTP protocols
    "ProtocolHttpRequestBuilder",
    "ProtocolHttpStreamingResponse",
    "ProtocolHttpExtendedClient",
    # Kafka client protocols
    "ProtocolKafkaClient",
    "ProtocolKafkaClientProvider",
    # Extended Kafka protocols
    "ProtocolKafkaMessage",
    "ProtocolKafkaConsumer",
    "ProtocolKafkaBatchProducer",
    "ProtocolKafkaTransactionalProducer",
    "ProtocolKafkaExtendedClient",
    # Logging protocols
    "ProtocolLogger",
]
