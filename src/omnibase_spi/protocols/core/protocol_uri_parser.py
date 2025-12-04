"""
Protocol for ONEX URI parser utilities.

Provides a clean interface for URI parsing operations without exposing
implementation-specific details. This protocol enables testing and
cross-component URI parsing while maintaining proper architectural boundaries.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolUriParser(Protocol):
    """Protocol for URI parsing and component extraction.

    Provides standardized URI parsing functionality across the ONEX ecosystem,
    enabling consistent URI handling, validation, and component extraction for
    service discovery, resource addressing, and protocol negotiation.

    The URI parser follows RFC 3986 URI specification, supporting hierarchical
    URIs with scheme, authority, path, query, and fragment components. It provides
    structured access to URI components through a dictionary interface compatible
    with ONEX ContextValue types.

    Example:
        ```python
        from omnibase_spi.protocols.core import ProtocolUriParser

        parser: ProtocolUriParser = get_uri_parser()

        # Parse HTTP URL
        http_uri = parser.parse("https://api.example.com:8443/v1/users?active=true#results")
        assert http_uri["scheme"] == "https"
        assert http_uri["host"] == "api.example.com"
        assert http_uri["port"] == 8443
        assert http_uri["path"] == "/v1/users"
        assert http_uri["query"] == "active=true"
        assert http_uri["fragment"] == "results"

        # Parse service discovery URI
        service_uri = parser.parse("consul://prod/workflow-orchestrator:5000")
        assert service_uri["scheme"] == "consul"
        assert service_uri["host"] == "prod"
        assert service_uri["path"] == "/workflow-orchestrator"
        assert service_uri["port"] == 5000

        # Parse file path URI
        file_uri = parser.parse("file:///etc/onex/config.yaml")
        assert file_uri["scheme"] == "file"
        assert file_uri["path"] == "/etc/onex/config.yaml"

        # Parse database connection URI
        db_uri = parser.parse("postgresql://user:pass@localhost:5432/dbname?ssl=true")
        assert db_uri["scheme"] == "postgresql"
        assert db_uri["userinfo"] == "user:pass"
        assert db_uri["host"] == "localhost"
        assert db_uri["port"] == 5432
        assert db_uri["path"] == "/dbname"
        assert db_uri["query"] == "ssl=true"
        ```

    Key Features:
        - RFC 3986 compliant URI parsing
        - Component extraction (scheme, authority, path, query, fragment)
        - Port number parsing and defaults
        - Query string preservation
        - Fragment identifier support
        - User info extraction (username:password)
        - Hierarchical and non-hierarchical URI support
        - ContextValue-compatible return types

    URI Components Returned:
        - scheme: URI scheme (http, https, consul, file, etc.)
        - host: Hostname or IP address
        - port: Port number (int) or None if not specified
        - path: URI path component
        - query: Query string (unparsed)
        - fragment: Fragment identifier
        - userinfo: User information (username:password)
        - authority: Complete authority component (userinfo@host:port)

    Supported URI Schemes:
        - HTTP/HTTPS: Web service endpoints
        - Consul/Etcd: Service discovery URIs
        - File: Local file system paths
        - PostgreSQL/MySQL: Database connection strings
        - AMQP/Kafka: Message broker connections
        - Redis: Cache service connections
        - Custom schemes: Application-specific protocols

    See Also:
        - ProtocolServiceDiscovery: Uses URI parser for service addressing
        - ProtocolEventBus: Uses URI parser for broker connections
        - ProtocolLogger: URI sanitization in logs
    """

    def parse(self, uri_string: str) -> dict[str, "ContextValue"]:
        """Parse a URI string into structured components.

        Performs RFC 3986 compliant URI parsing, extracting all components
        into a structured dictionary with ContextValue-compatible types.

        Args:
            uri_string: Complete URI string to parse (e.g., "https://host:port/path?query#fragment")

        Returns:
            Dictionary containing URI components as ContextValue types:
            - scheme: str - URI scheme (required)
            - host: str | None - Hostname or IP address
            - port: int | None - Port number
            - path: str - Path component
            - query: str | None - Query string
            - fragment: str | None - Fragment identifier
            - userinfo: str | None - User credentials
            - authority: str | None - Complete authority

        Raises:
            ValueError: If URI string is malformed or invalid
            TypeError: If uri_string is not a string

        Example:
            ```python
            # Parse complete URI with all components
            uri_components = parser.parse("https://user:pass@api.example.com:8443/v1/resource?key=value#section")

            # Access individual components
            print(f"Connecting to {uri_components['scheme']}://{uri_components['host']}:{uri_components['port']}")
            print(f"Path: {uri_components['path']}")
            print(f"Query: {uri_components['query']}")

            # Parse minimal URI
            simple_uri = parser.parse("file:///var/log/onex.log")
            assert simple_uri["scheme"] == "file"
            assert simple_uri["path"] == "/var/log/onex.log"
            assert simple_uri["host"] is None
            assert simple_uri["port"] is None
            ```
        """
        ...
