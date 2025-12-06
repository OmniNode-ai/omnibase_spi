"""
Protocol interfaces for file processing operations in ONEX ecosystem.

This protocol defines interfaces for unified file processing, tree analysis, caching,
rate limiting, and metrics collection operations. Provides type-safe contracts
for comprehensive file processing pipelines across ONEX service components.

Domain: File Processing and Analysis
Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


# === PROTOCOLS ===


@runtime_checkable
class ProtocolFileProcessingResult(Protocol):
    """
    Protocol for file processing operation results.

    Defines the contract for file processing results with comprehensive
    metadata, performance tracking, and error reporting capabilities.

    Key Features:
        - Processing success/failure status
        - Performance timing metrics
        - Cache hit/miss tracking
        - Detailed metadata storage
        - Error message reporting
        - File path identification

    Usage Example:
        ```python
        result: ProtocolFileProcessingResult = processor.process_file(str('data.yaml'))

        if result.success:
            print(f"Processed {result.file_path} in {result.processing_time_ms}ms")
            if result.cached:
                print("Result served from cache")
        else:
            print(f"Processing failed: {result.error_message}")
        ```
    """

    file_path: str
    success: bool
    processing_time_ms: float
    cached: bool
    metadata: dict[str, "ContextValue"]
    error_message: str | None


@runtime_checkable
class ProtocolProjectAnalysis(Protocol):
    """
    Protocol for complete project analysis results.

    Defines the contract for project-wide analysis with comprehensive
    statistics, file tracking, and tree structure information.

    Key Features:
        - Project scope analysis
        - File processing statistics
        - Tree structure representation
        - Ignore pattern tracking
        - Performance metrics
        - Comprehensive file tracking

    Usage Example:
        ```python
        analysis: ProtocolProjectAnalysis = processor.process_project(str('/project'))

        print(f"Processed {analysis.processed_files}/{analysis.total_files} files")
        print(f"Ignored {analysis.ignored_files} files based on patterns")
        print(f"Failed files: {analysis.failed_files}")
        ```
    """

    project_root: str
    total_files: int
    processed_files: int
    ignored_files: int
    failed_files: int
    processing_time_ms: float
    file_results: list["ProtocolFileProcessingResult"]
    tree_structure: dict[str, "ContextValue"]
    ignore_patterns: list[str]


@runtime_checkable
class ProtocolASTNode(Protocol):
    """
    Protocol for AST node representation.

    Defines the contract for AST nodes with comprehensive structural
    information, location tracking, and metadata support.

    Key Features:
        - Node type identification
        - Named entity support
        - Precise location tracking
        - Hierarchical structure
        - Metadata storage
        - Child node relationships

    Usage Example:
        ```python
        node: ProtocolASTNode = ast_result.root_node

        print(f"Found {node.node_type} at line {node.start_line}")
        if node.name:
            print(f"Entity name: {node.name}")

        # Process children recursively
        for child in node.children:
            process_ast_node(child)
        ```
    """

    node_type: str
    name: str | None
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    children: list["ProtocolASTNode"]
    metadata: dict[str, "ContextValue"]


@runtime_checkable
class ProtocolASTResult(Protocol):
    """
    Protocol for AST parsing results.

    Defines the contract for AST parsing results with performance
    metrics, error tracking, and comprehensive node information.

    Key Features:
        - File and language identification
        - Root node access
        - Performance timing
        - Node count tracking
        - Error and warning reporting
        - Parsing quality metrics

    Usage Example:
        ```python
        ast_result: ProtocolASTResult = analyzer.parse_file(str('source.py'))

        print(f"Parsed {ast_result.file_path} in {ast_result.parsing_time_ms}ms")
        print(f"Found {ast_result.node_count} nodes")
        if ast_result.error_count > 0:
            print(f"Found {ast_result.error_count} parsing errors")
        ```
    """

    file_path: str
    language: str
    root_node: "ProtocolASTNode"
    parsing_time_ms: float
    node_count: int
    error_count: int
    warnings: list[str]


@runtime_checkable
class ProtocolFileProcessor(Protocol):
    """
    Protocol for file processing operations in ONEX ecosystem.

    Defines the contract for file processing operations with support for
    single files, directories, and entire project analysis. Provides
    comprehensive performance tracking and error reporting.

    Key Features:
        - Single file processing
        - Directory batch processing
        - Complete project analysis
        - Performance metrics collection
        - Cache integration support
        - Error handling and reporting

    Processing Capabilities:
        - File content analysis
        - Structure parsing
        - Metadata extraction
        - Dependency analysis
        - Quality assessment
        - Performance profiling

    Usage Example:
        ```python
        processor: ProtocolFileProcessor = SomeFileProcessor()

        # Process single file
        result = await processor.process_file(str('config.yaml'))

        # Process directory
        results = await processor.process_directory(str('src/'))

        # Process entire project
        analysis = await processor.process_project(str('/project'))
        ```

    Integration Patterns:
        - Works with ONEX file handling protocols
        - Integrates with caching systems
        - Supports parallel processing
        - Provides detailed analytics
        - Compatible with async workflows
    """

    async def process_file(self, file_path: str) -> "ProtocolFileProcessingResult":
        """
        Process a single file.

        Performs comprehensive analysis and processing of a single file
        with detailed metadata collection and performance tracking.

        Args:
            file_path: str to file to process

        Returns:
            Processing result with metadata and performance metrics
        """
        ...

    async def process_directory(
        self,
        directory: str,
    ) -> list["ProtocolFileProcessingResult"]:
        """
        Process all files in a directory.

        Performs batch processing of all files in the specified directory
        with individual result tracking and aggregate statistics.

        Args:
            directory: Directory path to process

        Returns:
            List of processing results for all files
        """
        ...

    async def process_project(self, project_root: str) -> "ProtocolProjectAnalysis":
        """
        Process entire project with tree structure analysis.

        Performs comprehensive project-wide analysis including file processing,
        tree structure generation, and pattern-based filtering.

        Args:
            project_root: Root directory of project

        Returns:
            Complete project analysis with comprehensive statistics
        """
        ...


@runtime_checkable
class ProtocolTreeAnalyzer(Protocol):
    """
    Protocol for AST tree analysis operations.

    Defines the contract for AST parsing and analysis operations with
    support for multiple programming languages and symbol extraction.

    Key Features:
        - Multi-language AST parsing
        - Symbol extraction and analysis
        - Language auto-detection
        - Performance optimization
        - Error handling and reporting
        - Comprehensive symbol tracking

    Supported Languages:
        - Python, JavaScript, TypeScript
        - YAML, JSON, XML
        - Configuration file formats
        - Custom language extensions

    Usage Example:
        ```python
        analyzer: ProtocolTreeAnalyzer = SomeTreeAnalyzer()

        # Parse file with auto-detection
        ast_result = await analyzer.parse_file(str('source.py'))

        # Parse with specific language hint
        ast_result = await analyzer.parse_file(
            str('unknown.ext'),
            language='python'
        )

        # Extract symbols
        symbols = await analyzer.extract_symbols(ast_result)
        print(f"Found functions: {symbols.get('functions', [])}")
        ```
    """

    async def parse_file(
        self,
        file_path: str,
        language: str | None = None,
    ) -> "ProtocolASTResult":
        """
        Parse file and return AST.

        Performs AST parsing with optional language specification and
        comprehensive error reporting.

        Args:
            file_path: str to file to parse
            language: Optional language hint (auto-detected if not provided)

        Returns:
            Parsed AST result with comprehensive metadata
        """
        ...

    async def get_supported_languages(self) -> list[str]:
        """
            ...
        Return list of supported languages.

        Provides information about all supported programming languages
        and file formats for AST parsing.

        Returns:
            List of language identifiers (e.g., ["python", "typescript"])
        """
        ...

    async def extract_symbols(
        self, ast_result: "ProtocolASTResult"
    ) -> dict[str, list[str]]:
        """
        Extract symbols from AST (functions, classes, etc).

        Performs comprehensive symbol extraction from AST structures
        with categorization and organization.

        Args:
            ast_result: Parsed AST result

        Returns:
            Dictionary of symbol types to symbol names
        """
        ...


@runtime_checkable
class ProtocolCacheManager(Protocol):
    """
    Protocol for caching operations in ONEX ecosystem.

    Defines the contract for caching operations with TTL support,
    pattern-based invalidation, and comprehensive statistics.

    Key Features:
        - Key-value caching with TTL
        - Pattern-based invalidation
        - Performance statistics
        - Cache management operations
        - Memory optimization
        - Hit/miss tracking

    Usage Example:
        ```python
        cache: ProtocolCacheManager = SomeCacheManager()

        # Set cached value
        await cache.set('file_analysis:result:123', analysis_data, ttl_seconds=3600)

        # Get cached value
        result = await cache.get('file_analysis:result:123')
        if result is None:
            # Cache miss, compute and cache
            result = compute_analysis()
            await cache.set('file_analysis:result:123', result, 3600)

        # Invalidate by pattern
        invalidated = await cache.invalidate('file_analysis:*')
        print(f"Invalidated {invalidated} cache entries")
        ```
    """

    async def get(self, key: str) -> "ContextValue | None":
        """
        Get cached value.

        Retrieves a value from cache by key with automatic handling
        of expired entries and cache misses.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        ...

    async def set(self, key: str, value: "ContextValue", ttl_seconds: int) -> None:
        """
        Set cached value with TTL.

        Stores a value in cache with specified time-to-live for
        automatic expiration.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        ...

    async def invalidate(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.

        Removes cache entries that match the specified pattern
        with wildcard support for flexible invalidation.

        Args:
            pattern: Pattern to match (supports wildcards)

        Returns:
            Number of entries invalidated
        """
        ...

    async def clear(self) -> None:
        """Clear all cache entries"""
        ...

    async def get_stats(self) -> dict[str, int]:
        """
        Get cache statistics.

        Provides comprehensive cache performance metrics including
        hit rates, memory usage, and operation counts.

        Returns:
            Dictionary with stats (hits, misses, size, etc)
        """
        ...


@runtime_checkable
class ProtocolRateLimiter(Protocol):
    """
    Protocol for rate limiting operations in ONEX ecosystem.

    Defines the contract for rate limiting with resource tracking,
    permit acquisition/release, and configurable limits.

    Key Features:
        - Resource-based rate limiting
        - Permit acquisition and release
        - Configurable limits
        - Performance optimization
        - Resource protection
        - Load balancing support

    Usage Example:
        ```python
        rate_limiter: ProtocolRateLimiter = SomeRateLimiter()

        try:
            # Acquire permit for resource
            await rate_limiter.acquire('api_calls')

            # Perform rate-limited operation
            result = perform_api_call()

        finally:
            # Release permit
            await rate_limiter.release('api_calls')
        ```
    """

    async def acquire(self, resource: str) -> None:
        """
        Acquire rate limit permit for resource.

        Acquires a permit for the specified resource, blocking or raising
        an exception if the rate limit is exceeded.

        Args:
            resource: Resource identifier

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        ...

    async def release(self, resource: str) -> None:
        """
        Release rate limit permit for resource.

        Releases a previously acquired permit for the specified resource.

        Args:
            resource: Resource identifier
        """
        ...

    async def get_limit(self, resource: str) -> int: ...


@runtime_checkable
class ProtocolFileMetricsCollector(Protocol):
    """
    Protocol for metrics collection in ONEX ecosystem.

    Defines the contract for metrics collection with support for
    counters, gauges, histograms, and comprehensive export capabilities.

    Key Features:
        - Counter metrics (incrementing)
        - Gauge metrics (set values)
        - Histogram metrics (distributions)
        - Tag-based organization
        - Performance tracking
        - Export capabilities

    Metric Types:
        - Counters: Monotonically increasing values
        - Gauges: Values that can go up and down
        - Histograms: Distribution of values

    Usage Example:
        ```python
        metrics: ProtocolFileMetricsCollector = SomeMetricsCollector()

        # Track operation counts
        metrics.increment('files.processed', tags={'type': 'yaml'})

        # Track current resource usage
        metrics.gauge('memory.usage', current_memory_mb)

        # Track operation timing
        metrics.histogram('operation.duration', duration_ms)

        # Export all metrics
        all_metrics = await metrics.export_metrics()
        ```
    """

    def increment(
        self,
        metric: str,
        value: int | None = None,
        tags: dict[str, str] | None = None,
    ) -> None:
        """
        Increment counter metric.

        Increases the value of a counter metric by the specified amount.

        Args:
            metric: Metric name
            value: Increment value
                ...
            tags: Optional metric tags
        """
        ...

    def gauge(
        self,
        metric: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """
        Set gauge metric.

        Sets the absolute value of a gauge metric.

        Args:
            metric: Metric name
                ...
            value: Gauge value
            tags: Optional metric tags
        """
        ...

    def histogram(
        self,
        metric: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """
        Record histogram metric.

        Records a value in a histogram for distribution tracking.

        Args:
            ...
        """
        ...

    async def export_metrics(self) -> dict[str, "ContextValue"]:
        """
        Export all metrics.

        Exports all collected metrics in a structured format
        for external processing and reporting.

        Returns:
            Dictionary of metric data
        """
        ...
