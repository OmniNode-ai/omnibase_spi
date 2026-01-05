"""
Protocol for loading projectors from YAML contracts.

This module defines the interface for projector loaders that instantiate
projectors from declarative contract definitions. The loader handles:
- Contract parsing and validation
- Schema initialization (tables, indexes)
- Projector configuration and instantiation

Architecture Context:
    The projector loader enables declarative projector configuration:

    ```
    projectors/
      orders.yaml      # Contract defining OrderProjector
      users.yaml       # Contract defining UserProjector
      inventory.yaml   # Contract defining InventoryProjector
    ```

    Each contract specifies:
    - Target table and schema
    - Column definitions and types
    - Index requirements
    - Ordering configuration

    The loader discovers contracts, validates them, and produces
    configured ProtocolEventProjector instances ready for use.

Example Contract:
    ```yaml
    projector:
      name: orders
      domain: ecommerce
      table: order_projections

    schema:
      columns:
        - name: order_id
          type: varchar(36)
          primary_key: true
        - name: status
          type: varchar(50)
        - name: total_amount
          type: decimal(10,2)
        - name: updated_at
          type: timestamp

      indexes:
        - columns: [status]
        - columns: [updated_at]

    ordering:
      entity_id_column: order_id
      sequence_column: sequence_number
    ```

Related tickets:
    - OMN-1167: Define ProtocolProjectorLoader in omnibase_spi
    - OMN-940: Define ProtocolProjector
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.projectors.protocol_event_projector import (
        ProtocolEventProjector,
    )


@runtime_checkable
class ProtocolProjectorLoader(Protocol):
    """Interface for loading projectors from declarative contracts.

    Enables declarative projector definitions via YAML contracts,
    separating projector configuration from implementation. The loader
    handles contract validation, schema creation, and projector instantiation.

    Design Principles:
        - Contract-driven: Projectors defined in YAML, not code
        - Schema-aware: Loader ensures tables and indexes exist
        - Discovery-friendly: Supports glob patterns for contract finding
        - Fail-fast: Invalid contracts raise clear validation errors

    Lifecycle:
        1. Discover contracts (via path, directory, or patterns)
        2. Parse and validate contract structure
        3. Ensure database schema matches contract (create/migrate)
        4. Instantiate and configure projector
        5. Return ready-to-use ProtocolEventProjector instance

    Error Handling:
        - ContractValidationError: Contract syntax or semantic errors
        - SchemaError: Database schema creation/migration failures
        - FileNotFoundError: Contract file does not exist

    Thread Safety:
        Loaders should be thread-safe. Multiple callers can load
        projectors concurrently. Schema creation should use
        appropriate locking to prevent race conditions.

    Example Usage:
        ```python
        loader = ProjectorLoader(connection_pool)

        # Load single projector
        orders_projector = await loader.load_from_contract(
            Path("contracts/orders.yaml")
        )

        # Load all projectors in directory
        projectors = await loader.load_from_directory(
            Path("contracts/projectors/")
        )

        # Discover and load using patterns
        projectors = await loader.discover_and_load(
            patterns=["**/projectors/*.yaml", "**/projections/*.yml"]
        )
        ```
    """

    async def load_from_contract(
        self,
        contract_path: Path,
    ) -> ProtocolEventProjector:
        """Load a projector from a YAML contract file.

        Parses the contract, validates its structure and semantics,
        ensures the database schema exists (creating if needed),
        and returns a fully configured projector instance.

        Args:
            contract_path: Path to the YAML contract file. Must exist
                and be readable. Supports both .yaml and .yml extensions.

        Returns:
            A configured ProtocolEventProjector instance ready for use.
            The projector is connected to the appropriate database
            and configured according to the contract.

        Raises:
            ContractValidationError: If the contract file contains
                invalid YAML syntax, missing required fields, or
                semantic errors (e.g., invalid column types).
            SchemaError: If the database schema cannot be created
                or migrated to match the contract specification.
            FileNotFoundError: If contract_path does not exist.
            PermissionError: If contract_path is not readable.

        Contract Structure:
            The contract must include:
            - projector: name, domain, table
            - schema: columns with names and types
            - ordering: entity_id_column, sequence_column

            Optional sections:
            - schema.indexes: column indexes to create
            - projector.description: human-readable description

        Schema Handling:
            - If table doesn't exist: creates it with all columns
            - If table exists: validates columns match (no auto-migration)
            - Creates indexes if they don't exist

        Example:
            ```python
            projector = await loader.load_from_contract(
                Path("/app/contracts/orders.yaml")
            )

            # Projector is ready to use
            await projector.persist(
                projection=order_data,
                entity_id=order_id,
                domain="orders",
                sequence_info=seq,
            )
            ```
        """
        ...

    async def load_from_directory(
        self,
        directory: Path,
    ) -> list[ProtocolEventProjector]:
        """Load all projectors from contracts in a directory.

        Discovers all .yaml and .yml files in the specified directory
        (non-recursive) and loads each as a projector contract.

        Args:
            directory: Directory containing contract files. Must exist
                and be a directory. Only top-level files are processed;
                subdirectories are not traversed.

        Returns:
            List of configured ProtocolEventProjector instances, one for
            each valid contract file found. The list order matches
            the lexicographic order of filenames.

        Raises:
            FileNotFoundError: If directory does not exist.
            NotADirectoryError: If directory is not a directory.
            ContractValidationError: If any contract file is invalid.
                Processing stops at the first error.
            SchemaError: If schema creation fails for any projector.

        Discovery Rules:
            - Includes: *.yaml, *.yml files
            - Excludes: Hidden files (starting with .)
            - Excludes: Subdirectories (non-recursive)

        Error Behavior:
            By default, loading stops at the first error. Implementations
            may offer a continue_on_error option for partial loading.

        Example:
            ```python
            projectors = await loader.load_from_directory(
                Path("/app/contracts/projectors/")
            )

            print(f"Loaded {len(projectors)} projectors")
            for projector in projectors:
                print(f"  - Ready: {projector}")
            ```
        """
        ...

    async def discover_and_load(
        self,
        patterns: list[str],
    ) -> list[ProtocolEventProjector]:
        """Discover contracts matching glob patterns and load projectors.

        Supports flexible contract discovery using glob patterns,
        enabling contracts to be organized in various directory structures.

        Args:
            patterns: List of glob patterns to match contract files.
                Patterns are relative to the current working directory
                unless absolute. Supports recursive patterns (**).

                Examples:
                - "contracts/*.yaml" - all YAML in contracts/
                - "**/projectors/*.yaml" - recursive projector discovery
                - "modules/*/projections.yml" - per-module contracts

        Returns:
            List of configured ProtocolEventProjector instances for all
            contracts matching any of the patterns. Duplicates (same
            file matched by multiple patterns) are deduplicated.

        Raises:
            ContractValidationError: If any matched contract is invalid.
            SchemaError: If schema creation fails for any projector.

        Pattern Matching:
            - Uses Python's pathlib.Path.glob() semantics
            - ** matches any number of directories
            - * matches any characters except /
            - Patterns are processed in order
            - Results are deduplicated by absolute path

        Ordering:
            Results are returned in discovery order (first pattern match
            wins for ordering, subsequent matches are deduplicated).

        Example:
            ```python
            # Load all projector contracts from multiple locations
            projectors = await loader.discover_and_load(
                patterns=[
                    "core/projectors/*.yaml",
                    "plugins/*/projectors/*.yaml",
                    "custom/**/*.projector.yml",
                ]
            )

            print(f"Discovered and loaded {len(projectors)} projectors")
            ```
        """
        ...
