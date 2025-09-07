# Discovery Protocols API Reference

## Overview

The ONEX discovery protocols provide comprehensive service and handler discovery capabilities for distributed systems. These protocols enable dynamic node registration, plugin discovery, handler resolution, and distributed service coordination with sophisticated filtering, monitoring, and lifecycle management.

## Protocol Architecture

The discovery domain consists of specialized protocols that provide complete service and handler discovery:

### Handler Discovery Protocol

```python
from omnibase.protocols.discovery import ProtocolHandlerDiscovery
from omnibase.protocols.types.discovery_types import ProtocolHandlerInfo

@runtime_checkable
class ProtocolHandlerDiscovery(Protocol):
    """
    Protocol for discovering file type handlers from various sources.
    
    Supports plugin-based architecture where handlers can be discovered 
    dynamically from entry points, configuration files, environment variables,
    and other sources without requiring hardcoded imports.
    
    Features:
        - Multi-source discovery (entry points, config files, environment)
        - Dynamic handler loading and registration
        - Plugin architecture support
        - Error resilience with graceful fallback
        - Source identification for troubleshooting
        - Metadata extraction for handler capabilities
    """
    
    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
        """
        Discover available handler nodes from this source.
        
        Implementations scan their specific source (entry points, config files, etc.)
        and return handler information for all discovered handlers.
        
        Returns:
            List of ProtocolHandlerInfo objects for discovered handlers
            
        Raises:
            DiscoveryError: If discovery process encounters unrecoverable errors
        """
        ...
    
    def get_source_name(self) -> str:
        """
        Get human-readable name of this discovery source.
        
        Used for logging, debugging, and user interface display.
        Should include enough detail to identify the source uniquely.
        
        Returns:
            Human-readable name (e.g., "EntryPoint[myapp.handlers]", 
                                        "ConfigFile[/etc/handlers.yaml]")
        """
        ...
```

### Handler Information Protocol

```python
from omnibase.protocols.discovery import ProtocolHandlerInfo
from omnibase.protocols.file_handling import ProtocolFileTypeHandler

@runtime_checkable
class ProtocolHandlerInfo(Protocol):
    """
    Protocol for handler information objects.
    
    Contains all metadata needed to register and use a file type handler,
    including capabilities, priority, and source information.
    
    Features:
        - Complete handler metadata
        - Source tracking for provenance
        - Priority-based ordering
        - Extension and filename support mapping
        - Diagnostic metadata for troubleshooting
    """
    
    node_class: Type[ProtocolFileTypeHandler]
    name: str
    source: str  # "core", "runtime", "node-local", "plugin"
    priority: int
    extensions: list[str]
    special_files: list[str]
    metadata: dict[str, Any]
```

### Node Discovery Registry Protocol

```python
from omnibase.protocols.discovery import ProtocolNodeDiscoveryRegistry

@runtime_checkable
class ProtocolNodeDiscoveryRegistry(Protocol):
    """
    Protocol for registries that support dynamic discovery.
    
    Extends basic node registries with discovery capabilities, enabling
    nodes to be registered from multiple sources without hardcoded imports.
    Supports plugin architectures and runtime node registration.
    
    Features:
        - Multiple discovery source registration
        - Batch discovery and registration
        - Source prioritization and ordering
        - Error handling and recovery
        - Dynamic node lifecycle management
    """
    
    def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None:
        """
        Register a handler discovery source with the registry.
        
        Discovery sources are consulted in registration order during discovery.
        Multiple sources can be registered to support different discovery methods.
        
        Args:
            discovery: Handler discovery implementation to register
            
        Raises:
            RegistrationError: If source cannot be registered
        """
        ...
    
    def discover_and_register_nodes(self) -> None:
        """
        Discover handlers from all registered sources and register them.
        
        Iterates through all registered discovery sources, discovers available
        handlers, and registers them with the node registry. Handles conflicts
        and prioritization automatically.
        
        Raises:
            DiscoveryError: If discovery process fails critically
            RegistrationError: If handler registration fails
        """
        ...
    
    def register_node_info(self, node_info: ProtocolHandlerInfo) -> None:
        """
        Register a handler from ProtocolHandlerInfo.
        
        Direct registration method for handlers discovered from external sources.
        Validates handler info and integrates with existing node registry.
        
        Args:
            node_info: Complete handler information for registration
            
        Raises:
            ValidationError: If handler info is invalid
            RegistrationError: If registration fails
        """
        ...
```

## Type Definitions

### Core Discovery Types

```python
from omnibase.protocols.types.discovery_types import (
    DiscoveryStatus,
    HandlerStatus,
    CapabilityValue,
    ProtocolHandlerCapability,
    ProtocolDiscoveryQuery,
    ProtocolDiscoveryResult,
    ProtocolHandlerRegistration
)

# Discovery result status
DiscoveryStatus = Literal["found", "not_found", "error", "timeout"]

# Handler availability status  
HandlerStatus = Literal["available", "busy", "offline", "error"]

# Generic capability value type
CapabilityValue = str | int | float | bool | list[str]

@runtime_checkable
class ProtocolHandlerCapability(Protocol):
    """Protocol for handler capability objects."""
    
    capability_name: str
    capability_value: CapabilityValue
    is_required: bool
    version: ProtocolSemVer

@runtime_checkable
class ProtocolHandlerInfo(Protocol):
    """Protocol for comprehensive handler information."""
    
    node_id: UUID
    node_name: str
    node_type: str
    status: HandlerStatus
    capabilities: list[str]
    metadata: dict[str, CapabilityValue]

@runtime_checkable
class ProtocolDiscoveryQuery(Protocol):
    """Protocol for discovery query objects."""
    
    query_id: UUID
    target_type: str
    required_capabilities: list[str]
    filters: dict[str, str]
    timeout_seconds: float

@runtime_checkable
class ProtocolDiscoveryResult(Protocol):
    """Protocol for discovery operation results."""
    
    query_id: UUID
    status: DiscoveryStatus
    nodes_found: int
    discovery_time: float
    error_message: str | None

@runtime_checkable
class ProtocolHandlerRegistration(Protocol):
    """Protocol for handler registration objects."""
    
    node_id: UUID
    registration_data: dict[str, CapabilityValue]
    registration_time: float
    expires_at: float | None
    is_active: bool
```

## Usage Patterns

### Entry Point Discovery

```python
from omnibase.protocols.discovery import (
    ProtocolHandlerDiscovery, 
    ProtocolNodeDiscoveryRegistry
)

class EntryPointHandlerDiscovery:
    """Discover handlers from Python setuptools entry points."""
    
    def __init__(self, group_name: str):
        """
        Initialize entry point discovery.
        
        Args:
            group_name: Entry point group to scan (e.g., "myapp.file_handlers")
        """
        self.group_name = group_name
        self.discovered_nodes = []
    
    @property
    def group_name(self) -> str:
        return self._group_name
    
    @property
    def discovered_nodes(self) -> list[Any]:
        return self._discovered_nodes
    
    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
        """Discover handlers from entry points."""
        nodes = []
        
        try:
            import pkg_resources
            for entry_point in pkg_resources.iter_entry_points(self.group_name):
                try:
                    # Load handler class
                    handler_class = entry_point.load()
                    
                    # Create temporary instance for metadata extraction
                    temp_instance = handler_class()
                    
                    # Create handler info
                    handler_info = HandlerInfo(
                        node_class=handler_class,
                        name=entry_point.name,
                        source="entry_point",
                        priority=getattr(temp_instance, 'node_priority', 50),
                        extensions=getattr(temp_instance, 'supported_extensions', []),
                        special_files=getattr(temp_instance, 'supported_filenames', []),
                        metadata={
                            "entry_point": entry_point.name,
                            "module": entry_point.module_name,
                            "distribution": entry_point.dist.project_name,
                            "version": str(entry_point.dist.version),
                            "author": getattr(temp_instance, 'node_author', 'Unknown'),
                            "description": getattr(temp_instance, 'node_description', '')
                        }
                    )
                    nodes.append(handler_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to load handler {entry_point.name}: {e}")
                    continue
                    
        except ImportError:
            logger.warning("pkg_resources not available for entry point discovery")
        
        return nodes
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return f"EntryPoint[{self.group_name}]"

# Usage example
async def setup_entry_point_discovery():
    """Set up entry point-based handler discovery."""
    
    # Create discovery registry
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Register entry point discovery
    entry_point_discovery = EntryPointHandlerDiscovery("myapp.file_handlers")
    registry.register_discovery_source(entry_point_discovery)
    
    # Discover and register all handlers
    registry.discover_and_register_nodes()
    
    # Report discovered handlers
    handlers = entry_point_discovery.discover_nodes()
    print(f"Discovered {len(handlers)} handlers from entry points:")
    for handler_info in handlers:
        print(f"  - {handler_info.name}: {handler_info.extensions}")
```

### Configuration File Discovery

```python
import yaml
from pathlib import Path

class ConfigFileHandlerDiscovery:
    """Discover handlers from YAML configuration files."""
    
    def __init__(self, config_path: Path):
        """
        Initialize config file discovery.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
    
    @property
    def config_path(self) -> Path:
        return self._config_path
    
    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
        """Discover handlers from configuration file."""
        nodes = []
        
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return nodes
        
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            for handler_config in config.get("handlers", []):
                if not handler_config.get("enabled", True):
                    continue
                
                try:
                    # Dynamic import of handler class
                    module_path = handler_config["module"]
                    class_name = handler_config["class"]
                    
                    module = importlib.import_module(module_path)
                    handler_class = getattr(module, class_name)
                    
                    # Create handler info
                    handler_info = HandlerInfo(
                        node_class=handler_class,
                        name=handler_config["name"],
                        source="config_file",
                        priority=handler_config.get("priority", 50),
                        extensions=handler_config.get("extensions", []),
                        special_files=handler_config.get("special_files", []),
                        metadata={
                            "config_file": str(self.config_path),
                            "module": module_path,
                            "class": class_name,
                            "enabled": True,
                            "description": handler_config.get("description", ""),
                            "version": handler_config.get("version", "1.0.0")
                        }
                    )
                    
                    nodes.append(handler_info)
                    
                except Exception as e:
                    logger.error(f"Failed to load handler {handler_config.get('name', 'unknown')}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to load handlers from config: {e}")
        
        return nodes
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return f"ConfigFile[{self.config_path}]"

# Example configuration file format (handlers.yaml):
"""
handlers:
  - name: "python_handler"
    module: "myapp.handlers.python"
    class: "PythonFileHandler"
    enabled: true
    priority: 10
    extensions: [".py", ".pyi"]
    special_files: ["setup.py", "pyproject.toml"]
    description: "Python source file handler"
    version: "1.2.0"
    
  - name: "markdown_handler"
    module: "myapp.handlers.markdown"
    class: "MarkdownFileHandler"
    enabled: true
    priority: 20
    extensions: [".md", ".markdown"]
    special_files: ["README.md"]
    description: "Markdown document handler"
    version: "1.0.0"
"""

# Usage
async def setup_config_file_discovery():
    """Set up configuration file-based discovery."""
    
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Register config file discovery
    config_discovery = ConfigFileHandlerDiscovery(Path("config/handlers.yaml"))
    registry.register_discovery_source(config_discovery)
    
    # Discover and register
    registry.discover_and_register_nodes()
    
    # Report results
    handlers = config_discovery.discover_nodes()
    print(f"Loaded {len(handlers)} handlers from configuration:")
    for handler_info in handlers:
        print(f"  - {handler_info.name} (priority: {handler_info.priority})")
```

### Environment Variable Discovery

```python
import os
import importlib

class EnvironmentHandlerDiscovery:
    """Discover handlers from environment variables."""
    
    def __init__(self, env_prefix: str = "HANDLER_"):
        """
        Initialize environment variable discovery.
        
        Args:
            env_prefix: Prefix for environment variables to scan
        """
        self.env_prefix = env_prefix
    
    @property
    def env_prefix(self) -> str:
        return self._env_prefix
    
    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
        """Discover handlers from environment variables."""
        nodes = []
        
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(self.env_prefix):
                continue
            
            try:
                # Environment format: HANDLER_PYTHON=myapp.handlers.python:PythonHandler
                handler_name = env_key[len(self.env_prefix):].lower()
                module_path, class_name = env_value.split(":")
                
                # Import handler class
                module = importlib.import_module(module_path)
                handler_class = getattr(module, class_name)
                
                # Extract metadata from temporary instance
                temp_instance = handler_class()
                
                handler_info = HandlerInfo(
                    node_class=handler_class,
                    name=handler_name,
                    source="environment",
                    priority=getattr(temp_instance, 'node_priority', 50),
                    extensions=getattr(temp_instance, 'supported_extensions', []),
                    special_files=getattr(temp_instance, 'supported_filenames', []),
                    metadata={
                        "env_var": env_key,
                        "module": module_path,
                        "class": class_name,
                        "source": "environment_variable"
                    }
                )
                
                nodes.append(handler_info)
                
            except Exception as e:
                logger.warning(f"Failed to load handler from {env_key}: {e}")
                continue
        
        return nodes
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return f"Environment[{self.env_prefix}*]"

# Usage with environment variables:
# export HANDLER_PYTHON="myapp.handlers.python:PythonHandler"
# export HANDLER_YAML="myapp.handlers.yaml:YamlHandler"
# export HANDLER_JSON="myapp.handlers.json:JsonHandler"

async def setup_environment_discovery():
    """Set up environment variable-based discovery."""
    
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Register environment discovery
    env_discovery = EnvironmentHandlerDiscovery("MYAPP_HANDLER_")
    registry.register_discovery_source(env_discovery)
    
    # Discover and register
    registry.discover_and_register_nodes()
    
    # Report results
    handlers = env_discovery.discover_nodes()
    print(f"Loaded {len(handlers)} handlers from environment:")
    for handler_info in handlers:
        print(f"  - {handler_info.name} from {handler_info.metadata['env_var']}")
```

### Multi-Source Discovery Setup

```python
async def setup_comprehensive_discovery():
    """Set up comprehensive multi-source handler discovery."""
    
    # Create registry
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Register multiple discovery sources
    discovery_sources = [
        # Entry points (highest priority - installed packages)
        EntryPointHandlerDiscovery("myapp.file_handlers"),
        
        # System configuration (medium priority - system admin)
        ConfigFileHandlerDiscovery(Path("/etc/myapp/handlers.yaml")),
        
        # User configuration (medium priority - user customization)  
        ConfigFileHandlerDiscovery(Path.home() / ".config/myapp/handlers.yaml"),
        
        # Environment variables (lower priority - runtime config)
        EnvironmentHandlerDiscovery("MYAPP_HANDLER_"),
        
        # Local project configuration (lowest priority - project-specific)
        ConfigFileHandlerDiscovery(Path("./handlers.yaml")),
    ]
    
    # Register all sources
    for discovery_source in discovery_sources:
        registry.register_discovery_source(discovery_source)
    
    # Perform discovery
    print("Discovering handlers from all sources...")
    registry.discover_and_register_nodes()
    
    # Report discovery results
    print("\nDiscovery Summary:")
    total_handlers = 0
    
    for source in discovery_sources:
        handlers = source.discover_nodes()
        total_handlers += len(handlers)
        
        print(f"\n{source.get_source_name()}: {len(handlers)} handlers")
        for handler_info in handlers:
            print(f"  - {handler_info.name} (priority: {handler_info.priority})")
            print(f"    Extensions: {handler_info.extensions}")
            print(f"    Source: {handler_info.source}")
    
    print(f"\nTotal: {total_handlers} handlers discovered")
    return registry
```

## Advanced Features

### Discovery Result Caching

```python
import asyncio
import time
from typing import Dict, Tuple

class CachedDiscoverySource:
    """Wrapper that adds caching to discovery sources."""
    
    def __init__(self, 
                 base_discovery: ProtocolHandlerDiscovery, 
                 cache_ttl_seconds: int = 300):
        """
        Initialize cached discovery wrapper.
        
        Args:
            base_discovery: Base discovery source to wrap
            cache_ttl_seconds: Cache time-to-live in seconds
        """
        self.base_discovery = base_discovery
        self.cache_ttl = cache_ttl_seconds
        self._cached_results: Dict[str, Tuple[list[ProtocolHandlerInfo], float]] = {}
    
    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
        """Discover nodes with caching."""
        source_name = self.base_discovery.get_source_name()
        current_time = time.time()
        
        # Check cache
        if source_name in self._cached_results:
            cached_nodes, cache_time = self._cached_results[source_name]
            if current_time - cache_time < self.cache_ttl:
                logger.debug(f"Using cached results for {source_name}")
                return cached_nodes
        
        # Discover fresh results
        logger.debug(f"Discovering fresh results for {source_name}")
        nodes = self.base_discovery.discover_nodes()
        
        # Cache results
        self._cached_results[source_name] = (nodes, current_time)
        
        return nodes
    
    def get_source_name(self) -> str:
        """Get source name from base discovery."""
        return f"Cached[{self.base_discovery.get_source_name()}]"
    
    def invalidate_cache(self) -> None:
        """Invalidate cached results."""
        source_name = self.base_discovery.get_source_name()
        if source_name in self._cached_results:
            del self._cached_results[source_name]
            logger.debug(f"Cache invalidated for {source_name}")

# Usage
async def setup_cached_discovery():
    """Set up discovery with caching for performance."""
    
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Wrap discovery sources with caching
    cached_sources = [
        CachedDiscoverySource(
            EntryPointHandlerDiscovery("myapp.handlers"),
            cache_ttl_seconds=600  # Cache for 10 minutes
        ),
        CachedDiscoverySource(
            ConfigFileHandlerDiscovery(Path("handlers.yaml")),
            cache_ttl_seconds=60   # Cache for 1 minute (more dynamic)
        ),
    ]
    
    # Register cached sources
    for source in cached_sources:
        registry.register_discovery_source(source)
    
    # First discovery (slow - no cache)
    start_time = time.time()
    registry.discover_and_register_nodes()
    first_time = time.time() - start_time
    
    # Second discovery (fast - cached)
    start_time = time.time()
    registry.discover_and_register_nodes()
    second_time = time.time() - start_time
    
    print(f"First discovery: {first_time:.2f}s")
    print(f"Second discovery: {second_time:.2f}s (cached)")
```

### Watch-Based Discovery

```python
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatchDiscovery(FileSystemEventHandler):
    """Discovery source that watches file system for changes."""
    
    def __init__(self, 
                 watch_path: Path, 
                 callback: Callable[[], None]):
        """
        Initialize file watch discovery.
        
        Args:
            watch_path: Directory or file to watch
            callback: Function to call when changes detected
        """
        super().__init__()
        self.watch_path = Path(watch_path)
        self.callback = callback
        self.observer = Observer()
        self.is_watching = False
    
    def start_watching(self) -> None:
        """Start watching for file system changes."""
        if not self.is_watching:
            self.observer.schedule(self, str(self.watch_path), recursive=False)
            self.observer.start()
            self.is_watching = True
            logger.info(f"Started watching {self.watch_path}")
    
    def stop_watching(self) -> None:
        """Stop watching for changes."""
        if self.is_watching:
            self.observer.stop()
            self.observer.join()
            self.is_watching = False
            logger.info(f"Stopped watching {self.watch_path}")
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            logger.info(f"Configuration file modified: {event.src_path}")
            # Trigger re-discovery
            self.callback()

class WatchableConfigDiscovery(ConfigFileHandlerDiscovery):
    """Config discovery that supports file system watching."""
    
    def __init__(self, config_path: Path, registry: ProtocolNodeDiscoveryRegistry):
        super().__init__(config_path)
        self.registry = registry
        self.file_watcher = None
    
    def start_watching(self) -> None:
        """Start watching config file for changes."""
        def on_config_changed():
            logger.info("Config file changed, re-discovering handlers...")
            self.registry.discover_and_register_nodes()
        
        self.file_watcher = FileWatchDiscovery(self.config_path, on_config_changed)
        self.file_watcher.start_watching()
    
    def stop_watching(self) -> None:
        """Stop watching config file."""
        if self.file_watcher:
            self.file_watcher.stop_watching()

# Usage
async def setup_watch_based_discovery():
    """Set up discovery with file system watching."""
    
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Create watchable config discovery
    config_path = Path("handlers.yaml")
    watchable_discovery = WatchableConfigDiscovery(config_path, registry)
    
    # Register discovery source
    registry.register_discovery_source(watchable_discovery)
    
    # Initial discovery
    registry.discover_and_register_nodes()
    
    # Start watching for changes
    watchable_discovery.start_watching()
    
    print("Discovery set up with file system watching")
    print("Modify handlers.yaml to see automatic re-discovery")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    finally:
        # Clean up watcher
        watchable_discovery.stop_watching()
```

### Plugin Discovery with Validation

```python
class ValidatedPluginDiscovery:
    """Plugin discovery with comprehensive validation."""
    
    def __init__(self, plugin_dir: Path, required_interfaces: list[type] = None):
        """
        Initialize validated plugin discovery.
        
        Args:
            plugin_dir: Directory containing plugin files
            required_interfaces: Required interfaces for plugins
        """
        self.plugin_dir = Path(plugin_dir)
        self.required_interfaces = required_interfaces or []
        self.validation_errors: Dict[str, list[str]] = {}
    
    def discover_nodes(self) -> list[ProtocolHandlerInfo]:
        """Discover and validate plugins."""
        nodes = []
        self.validation_errors.clear()
        
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            return nodes
        
        # Scan Python files in plugin directory
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue  # Skip __init__.py, __pycache__, etc.
            
            try:
                plugin_info = self._load_and_validate_plugin(plugin_file)
                if plugin_info:
                    nodes.append(plugin_info)
                    
            except Exception as e:
                error_msg = f"Failed to load plugin {plugin_file.name}: {e}"
                self.validation_errors[plugin_file.name] = [error_msg]
                logger.error(error_msg)
        
        return nodes
    
    def _load_and_validate_plugin(self, plugin_file: Path) -> ProtocolHandlerInfo | None:
        """Load and validate a single plugin file."""
        
        # Import plugin module
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem, plugin_file
        )
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Find handler classes in module
        handler_classes = []
        for attr_name in dir(plugin_module):
            attr = getattr(plugin_module, attr_name)
            if (inspect.isclass(attr) and 
                hasattr(attr, 'supported_extensions') and
                attr_name != 'ProtocolFileTypeHandler'):
                handler_classes.append(attr)
        
        if not handler_classes:
            raise ValueError("No handler classes found in plugin")
        
        if len(handler_classes) > 1:
            logger.warning(f"Multiple handler classes in {plugin_file.name}, using first")
        
        handler_class = handler_classes[0]
        
        # Validate handler class
        validation_errors = self._validate_handler_class(handler_class, plugin_file.name)
        if validation_errors:
            self.validation_errors[plugin_file.name] = validation_errors
            return None
        
        # Create temporary instance for metadata
        temp_instance = handler_class()
        
        # Create handler info
        return HandlerInfo(
            node_class=handler_class,
            name=plugin_file.stem,
            source="plugin",
            priority=getattr(temp_instance, 'node_priority', 50),
            extensions=getattr(temp_instance, 'supported_extensions', []),
            special_files=getattr(temp_instance, 'supported_filenames', []),
            metadata={
                "plugin_file": str(plugin_file),
                "module_name": plugin_file.stem,
                "class_name": handler_class.__name__,
                "validation_passed": True,
                "author": getattr(temp_instance, 'node_author', 'Unknown'),
                "version": getattr(temp_instance, 'node_version', '1.0.0'),
                "description": getattr(temp_instance, 'node_description', '')
            }
        )
    
    def _validate_handler_class(self, handler_class: type, plugin_name: str) -> list[str]:
        """Validate handler class meets requirements."""
        errors = []
        
        # Check required interfaces
        for required_interface in self.required_interfaces:
            if not issubclass(handler_class, required_interface):
                errors.append(f"Does not implement required interface: {required_interface.__name__}")
        
        # Check required methods
        required_methods = [
            'can_handle', 'extract_block', 'stamp', 'validate'
        ]
        
        for method_name in required_methods:
            if not hasattr(handler_class, method_name):
                errors.append(f"Missing required method: {method_name}")
            elif not callable(getattr(handler_class, method_name)):
                errors.append(f"Required method is not callable: {method_name}")
        
        # Check required properties
        required_properties = [
            'supported_extensions', 'node_priority', 'node_name'
        ]
        
        # Create temporary instance for property checking
        try:
            temp_instance = handler_class()
            for prop_name in required_properties:
                if not hasattr(temp_instance, prop_name):
                    errors.append(f"Missing required property: {prop_name}")
                    
        except Exception as e:
            errors.append(f"Cannot instantiate class: {e}")
        
        return errors
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return f"ValidatedPlugins[{self.plugin_dir}]"
    
    def get_validation_report(self) -> str:
        """Get comprehensive validation report."""
        if not self.validation_errors:
            return "All plugins validated successfully"
        
        report = "Plugin Validation Errors:\n"
        for plugin_name, errors in self.validation_errors.items():
            report += f"\n{plugin_name}:\n"
            for error in errors:
                report += f"  - {error}\n"
        
        return report

# Usage
async def setup_validated_plugin_discovery():
    """Set up plugin discovery with validation."""
    
    from omnibase.protocols.file_handling import ProtocolFileTypeHandler
    
    registry: ProtocolNodeDiscoveryRegistry = NodeDiscoveryRegistryImpl()
    
    # Create validated plugin discovery
    plugin_discovery = ValidatedPluginDiscovery(
        plugin_dir=Path("plugins/"),
        required_interfaces=[ProtocolFileTypeHandler]
    )
    
    # Register discovery source
    registry.register_discovery_source(plugin_discovery)
    
    # Discover and register plugins
    registry.discover_and_register_nodes()
    
    # Report validation results
    validation_report = plugin_discovery.get_validation_report()
    print("Plugin Discovery Results:")
    print(validation_report)
    
    # List discovered plugins
    discovered_plugins = plugin_discovery.discover_nodes()
    print(f"\nSuccessfully loaded {len(discovered_plugins)} plugins:")
    for plugin_info in discovered_plugins:
        print(f"  - {plugin_info.name} (priority: {plugin_info.priority})")
        print(f"    Extensions: {plugin_info.extensions}")
```

## Integration with Other Domains

### File Handling Integration

```python
from omnibase.protocols.file_handling import ProtocolFileTypeHandler

async def integrate_discovery_with_file_handling(
    registry: ProtocolNodeDiscoveryRegistry
) -> None:
    """Integrate discovery with file handling system."""
    
    # Set up discovery for file handlers
    discovery_sources = [
        EntryPointHandlerDiscovery("myapp.file_handlers"),
        ConfigFileHandlerDiscovery(Path("file_handlers.yaml")),
        ValidatedPluginDiscovery(Path("file_plugins/"))
    ]
    
    for source in discovery_sources:
        registry.register_discovery_source(source)
    
    # Discover all file handlers
    registry.discover_and_register_nodes()
    
    # Create handler lookup by extension
    extension_handlers: Dict[str, list[ProtocolFileTypeHandler]] = {}
    
    for source in discovery_sources:
        handlers = source.discover_nodes()
        for handler_info in handlers:
            # Create handler instances
            handler_instance = handler_info.node_class()
            
            # Index by supported extensions
            for ext in handler_info.extensions:
                if ext not in extension_handlers:
                    extension_handlers[ext] = []
                extension_handlers[ext].append(handler_instance)
    
    # Sort handlers by priority
    for ext, handlers in extension_handlers.items():
        handlers.sort(key=lambda h: getattr(h, 'node_priority', 50))
    
    print("Handler Discovery Complete:")
    for ext, handlers in extension_handlers.items():
        print(f"  {ext}: {len(handlers)} handlers")
        for handler in handlers:
            print(f"    - {handler.node_name} (priority: {handler.node_priority})")
```

### MCP Tool Integration

```python
from omnibase.protocols.mcp import ProtocolMCPRegistry

async def integrate_discovery_with_mcp(
    registry: ProtocolNodeDiscoveryRegistry,
    mcp_registry: ProtocolMCPRegistry
) -> None:
    """Integrate discovery with MCP tool registry."""
    
    # Discover MCP tool providers
    mcp_tool_discovery = EntryPointHandlerDiscovery("myapp.mcp_tools")
    registry.register_discovery_source(mcp_tool_discovery)
    registry.discover_and_register_nodes()
    
    # Register discovered tools with MCP registry
    discovered_tools = mcp_tool_discovery.discover_nodes()
    
    for tool_info in discovered_tools:
        # Create tool instance
        tool_instance = tool_info.node_class()
        
        # Register with MCP registry
        if hasattr(tool_instance, 'get_tool_definitions'):
            tool_definitions = tool_instance.get_tool_definitions()
            
            for tool_def in tool_definitions:
                await mcp_registry.register_tool(
                    tool_definition=tool_def,
                    implementation=tool_instance
                )
    
    print(f"Registered {len(discovered_tools)} MCP tools from discovery")
```

## Testing Strategies

### Discovery Protocol Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestHandlerDiscovery:
    """Test suite for handler discovery protocols."""
    
    @pytest.fixture
    def mock_handler_class(self):
        """Create mock handler class for testing."""
        
        class MockHandler:
            node_name = "test_handler"
            node_priority = 10
            supported_extensions = [".test"]
            supported_filenames = ["test.txt"]
            node_author = "Test Author"
            node_description = "Test handler"
            
            def can_handle(self, path, content):
                return True
        
        return MockHandler
    
    @pytest.fixture
    def entry_point_discovery(self):
        """Create entry point discovery for testing."""
        return EntryPointHandlerDiscovery("test.handlers")
    
    def test_entry_point_discovery_source_name(self, entry_point_discovery):
        """Test source name generation."""
        assert entry_point_discovery.get_source_name() == "EntryPoint[test.handlers]"
    
    @patch('pkg_resources.iter_entry_points')
    def test_entry_point_discovery_success(
        self, 
        mock_iter_entry_points, 
        entry_point_discovery,
        mock_handler_class
    ):
        """Test successful entry point discovery."""
        
        # Mock entry point
        mock_entry_point = Mock()
        mock_entry_point.name = "test_handler"
        mock_entry_point.load.return_value = mock_handler_class
        mock_entry_point.module_name = "test.handlers.test_handler"
        mock_entry_point.dist.project_name = "test-package"
        mock_entry_point.dist.version = "1.0.0"
        
        mock_iter_entry_points.return_value = [mock_entry_point]
        
        # Discover handlers
        handlers = entry_point_discovery.discover_nodes()
        
        # Verify results
        assert len(handlers) == 1
        handler_info = handlers[0]
        
        assert handler_info.name == "test_handler"
        assert handler_info.source == "entry_point"
        assert handler_info.priority == 10
        assert handler_info.extensions == [".test"]
        assert handler_info.node_class == mock_handler_class
    
    @patch('pkg_resources.iter_entry_points')
    def test_entry_point_discovery_error_handling(
        self,
        mock_iter_entry_points,
        entry_point_discovery
    ):
        """Test error handling in entry point discovery."""
        
        # Mock failing entry point
        mock_entry_point = Mock()
        mock_entry_point.name = "failing_handler"
        mock_entry_point.load.side_effect = ImportError("Module not found")
        
        mock_iter_entry_points.return_value = [mock_entry_point]
        
        # Discovery should handle errors gracefully
        handlers = entry_point_discovery.discover_nodes()
        
        # Should return empty list, not raise exception
        assert handlers == []

class TestConfigFileDiscovery:
    """Test suite for config file discovery."""
    
    @pytest.fixture
    def config_file_content(self):
        """Sample configuration file content."""
        return """
        handlers:
          - name: "yaml_handler"
            module: "test.handlers.yaml_handler"
            class: "YamlHandler"
            enabled: true
            priority: 15
            extensions: [".yaml", ".yml"]
            description: "YAML file handler"
            
          - name: "disabled_handler"
            module: "test.handlers.disabled"
            class: "DisabledHandler"
            enabled: false
            extensions: [".disabled"]
        """
    
    @pytest.fixture
    def temp_config_file(self, tmp_path, config_file_content):
        """Create temporary config file."""
        config_file = tmp_path / "test_handlers.yaml"
        config_file.write_text(config_file_content)
        return config_file
    
    def test_config_file_discovery_source_name(self, temp_config_file):
        """Test config file source name."""
        discovery = ConfigFileHandlerDiscovery(temp_config_file)
        expected = f"ConfigFile[{temp_config_file}]"
        assert discovery.get_source_name() == expected
    
    @patch('importlib.import_module')
    def test_config_file_discovery_success(
        self,
        mock_import_module,
        temp_config_file,
        mock_handler_class
    ):
        """Test successful config file discovery."""
        
        # Mock module import
        mock_module = Mock()
        mock_module.YamlHandler = mock_handler_class
        mock_import_module.return_value = mock_module
        
        # Create discovery
        discovery = ConfigFileHandlerDiscovery(temp_config_file)
        handlers = discovery.discover_nodes()
        
        # Verify results (only enabled handler)
        assert len(handlers) == 1
        handler_info = handlers[0]
        
        assert handler_info.name == "yaml_handler"
        assert handler_info.source == "config_file"
        assert handler_info.priority == 15
        assert handler_info.extensions == [".yaml", ".yml"]
    
    def test_config_file_discovery_missing_file(self, tmp_path):
        """Test handling of missing config file."""
        
        missing_file = tmp_path / "nonexistent.yaml"
        discovery = ConfigFileHandlerDiscovery(missing_file)
        
        # Should return empty list, not raise exception
        handlers = discovery.discover_nodes()
        assert handlers == []

class TestNodeDiscoveryRegistry:
    """Test node discovery registry integration."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock node discovery registry."""
        
        class MockNodeDiscoveryRegistry:
            def __init__(self):
                self.discovery_sources = []
                self.registered_handlers = []
            
            def register_discovery_source(self, discovery):
                self.discovery_sources.append(discovery)
            
            def discover_and_register_nodes(self):
                for source in self.discovery_sources:
                    handlers = source.discover_nodes()
                    for handler_info in handlers:
                        self.register_node_info(handler_info)
            
            def register_node_info(self, node_info):
                self.registered_handlers.append(node_info)
        
        return MockNodeDiscoveryRegistry()
    
    def test_multi_source_discovery(self, mock_registry, mock_handler_class):
        """Test discovery from multiple sources."""
        
        # Create mock discovery sources
        source1 = Mock()
        source1.discover_nodes.return_value = [
            Mock(name="handler1", source="source1", priority=10)
        ]
        
        source2 = Mock()
        source2.discover_nodes.return_value = [
            Mock(name="handler2", source="source2", priority=20),
            Mock(name="handler3", source="source2", priority=30)
        ]
        
        # Register sources
        mock_registry.register_discovery_source(source1)
        mock_registry.register_discovery_source(source2)
        
        # Perform discovery
        mock_registry.discover_and_register_nodes()
        
        # Verify all handlers registered
        assert len(mock_registry.registered_handlers) == 3
        handler_names = [h.name for h in mock_registry.registered_handlers]
        assert "handler1" in handler_names
        assert "handler2" in handler_names
        assert "handler3" in handler_names
```

### Integration Testing

```python
class TestDiscoveryIntegration:
    """Test discovery integration with other systems."""
    
    async def test_discovery_with_file_handling(self):
        """Test discovery integration with file handling."""
        
        # Create test environment
        registry = MockNodeDiscoveryRegistry()
        file_manager = MockFileHandlingManager()
        
        # Set up discovery
        discovery = EntryPointHandlerDiscovery("test.handlers")
        registry.register_discovery_source(discovery)
        
        # Mock discovered handlers
        with patch.object(discovery, 'discover_nodes') as mock_discover:
            mock_discover.return_value = [
                Mock(
                    name="python_handler",
                    extensions=[".py"],
                    node_class=MockPythonHandler,
                    priority=10
                )
            ]
            
            # Perform discovery
            registry.discover_and_register_nodes()
            
            # Verify integration
            assert len(registry.registered_handlers) == 1
            
            # Test file handling integration
            handler_info = registry.registered_handlers[0]
            handler = handler_info.node_class()
            
            # Verify handler can process files
            result = handler.can_handle(Path("test.py"), "print('hello')")
            assert result.can_handle is True
    
    async def test_discovery_performance(self):
        """Test discovery performance with large numbers of handlers."""
        
        registry = MockNodeDiscoveryRegistry()
        
        # Create discovery source with many handlers
        large_discovery = Mock()
        large_discovery.discover_nodes.return_value = [
            Mock(name=f"handler_{i}", priority=i)
            for i in range(1000)  # 1000 handlers
        ]
        
        registry.register_discovery_source(large_discovery)
        
        # Measure discovery time
        start_time = time.time()
        registry.discover_and_register_nodes()
        discovery_time = time.time() - start_time
        
        # Verify performance (should complete quickly)
        assert discovery_time < 1.0  # Less than 1 second
        assert len(registry.registered_handlers) == 1000
```

## Performance Optimization

### Parallel Discovery

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelDiscoveryRegistry:
    """Registry that performs discovery in parallel."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize parallel discovery registry.
        
        Args:
            max_workers: Maximum number of parallel discovery workers
        """
        self.discovery_sources = []
        self.registered_handlers = []
        self.max_workers = max_workers
    
    def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None:
        """Register discovery source."""
        self.discovery_sources.append(discovery)
    
    async def discover_and_register_nodes(self) -> None:
        """Discover handlers from all sources in parallel."""
        
        # Run discovery in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all discovery tasks
            discovery_futures = [
                executor.submit(source.discover_nodes)
                for source in self.discovery_sources
            ]
            
            # Collect results
            all_handlers = []
            for future in discovery_futures:
                try:
                    handlers = future.result(timeout=30)  # 30 second timeout
                    all_handlers.extend(handlers)
                except Exception as e:
                    logger.error(f"Discovery source failed: {e}")
        
        # Register all discovered handlers
        for handler_info in all_handlers:
            self.register_node_info(handler_info)
    
    def register_node_info(self, node_info: ProtocolHandlerInfo) -> None:
        """Register handler info."""
        self.registered_handlers.append(node_info)

# Usage
async def setup_parallel_discovery():
    """Set up parallel discovery for performance."""
    
    registry = ParallelDiscoveryRegistry(max_workers=6)
    
    # Register multiple discovery sources
    discovery_sources = [
        EntryPointHandlerDiscovery("myapp.handlers"),
        ConfigFileHandlerDiscovery(Path("system_handlers.yaml")),
        ConfigFileHandlerDiscovery(Path("user_handlers.yaml")),
        EnvironmentHandlerDiscovery("MYAPP_HANDLER_"),
        ValidatedPluginDiscovery(Path("plugins/")),
        ValidatedPluginDiscovery(Path("user_plugins/"))
    ]
    
    for source in discovery_sources:
        registry.register_discovery_source(source)
    
    # Parallel discovery
    start_time = time.time()
    await registry.discover_and_register_nodes()
    discovery_time = time.time() - start_time
    
    print(f"Discovered {len(registry.registered_handlers)} handlers in {discovery_time:.2f}s")
```

### Lazy Discovery

```python
class LazyDiscoveryRegistry:
    """Registry that performs discovery on-demand."""
    
    def __init__(self):
        self.discovery_sources = []
        self._handler_cache: Dict[str, list[ProtocolHandlerInfo]] = {}
        self._discovery_performed = False
    
    def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None:
        """Register discovery source."""
        self.discovery_sources.append(discovery)
        self._discovery_performed = False  # Reset discovery flag
    
    def get_handlers_for_extension(self, extension: str) -> list[ProtocolHandlerInfo]:
        """Get handlers for specific extension (lazy discovery)."""
        
        # Perform discovery if not done yet
        if not self._discovery_performed:
            self._perform_lazy_discovery()
        
        # Return cached handlers for extension
        return self._handler_cache.get(extension, [])
    
    def _perform_lazy_discovery(self) -> None:
        """Perform discovery and cache by extension."""
        
        # Discover from all sources
        all_handlers = []
        for source in self.discovery_sources:
            try:
                handlers = source.discover_nodes()
                all_handlers.extend(handlers)
            except Exception as e:
                logger.warning(f"Discovery source {source.get_source_name()} failed: {e}")
        
        # Cache by extension
        for handler_info in all_handlers:
            for extension in handler_info.extensions:
                if extension not in self._handler_cache:
                    self._handler_cache[extension] = []
                self._handler_cache[extension].append(handler_info)
        
        # Sort by priority
        for extension, handlers in self._handler_cache.items():
            handlers.sort(key=lambda h: h.priority)
        
        self._discovery_performed = True
        logger.info(f"Lazy discovery completed: {len(all_handlers)} handlers")

# Usage
async def setup_lazy_discovery():
    """Set up lazy discovery for on-demand performance."""
    
    registry = LazyDiscoveryRegistry()
    
    # Register discovery sources (no discovery performed yet)
    registry.register_discovery_source(EntryPointHandlerDiscovery("myapp.handlers"))
    registry.register_discovery_source(ConfigFileHandlerDiscovery(Path("handlers.yaml")))
    
    print("Discovery sources registered (no discovery performed yet)")
    
    # Discovery happens on first access
    python_handlers = registry.get_handlers_for_extension(".py")
    print(f"Found {len(python_handlers)} Python handlers (discovery performed)")
    
    # Subsequent accesses use cache
    yaml_handlers = registry.get_handlers_for_extension(".yaml")
    print(f"Found {len(yaml_handlers)} YAML handlers (from cache)")
```

## Best Practices

### Discovery Design Guidelines

1. **Source Independence**: Each discovery source should be independent and self-contained
2. **Error Resilience**: Handle discovery failures gracefully without affecting other sources
3. **Source Priority**: Support priority ordering for handler resolution conflicts
4. **Metadata Rich**: Include comprehensive metadata for debugging and troubleshooting
5. **Validation**: Validate discovered handlers before registration
6. **Performance**: Use caching and parallel discovery for large-scale systems
7. **Monitoring**: Log discovery results and performance metrics

### Error Handling

1. **Graceful Degradation**: Continue discovery even if some sources fail
2. **Detailed Logging**: Provide detailed error messages for troubleshooting
3. **Fallback Sources**: Have backup discovery sources for critical handlers
4. **Validation Errors**: Clearly report validation failures with actionable messages

The discovery protocols provide comprehensive handler and service discovery capabilities that enable plugin architectures, dynamic registration, and distributed service coordination in the ONEX framework.