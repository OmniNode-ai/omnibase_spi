# Protocol Composition Patterns

## Overview

Advanced protocol design patterns for composing complex behaviors from simpler protocol components.

## Composition Patterns

### Protocol Aggregation

Combine multiple protocols into a single interface:

```python
@runtime_checkable
class ProtocolCompositeService(Protocol):
    """Composite service combining multiple protocol capabilities."""

    # Health monitoring capability
    health_monitor: ProtocolHealthMonitor

    # Logging capability
    logger: ProtocolLogger

    # Performance metrics capability
    metrics: ProtocolPerformanceMetrics

    async def perform_operation(self, data: ContextValue) -> ContextValue:
        """Perform operation with full observability."""
        # Use health monitoring
        health_status = await self.health_monitor.get_current_health_status()
        if health_status != "healthy":
            raise ServiceUnavailableError("Service unhealthy")

        # Log operation start
        await self.logger.log("INFO", f"Starting operation with data: {data}")

        # Record metrics
        start_time = time.time()
        try:
            result = await self._execute_operation(data)
            await self.metrics.record_timing("operation", time.time() - start_time)
            return result
        except Exception as e:
            await self.logger.log("ERROR", f"Operation failed: {e}")
            raise
```

### Protocol Delegation

Delegate specific responsibilities to specialized protocols:

```python
@runtime_checkable
class ProtocolWorkflowManager(Protocol):
    """Workflow manager with delegated responsibilities."""

    # Delegate workflow orchestration
    orchestrator: ProtocolWorkflowOrchestrator

    # Delegate event handling
    event_bus: ProtocolWorkflowEventBus

    # Delegate persistence
    persistence: ProtocolWorkflowPersistence

    async def start_workflow(
        self,
        workflow_type: str,
        instance_id: UUID,
        initial_data: dict[str, ContextValue]
    ) -> ProtocolWorkflowInstance:
        """Start workflow with full coordination."""
        # Delegate to orchestrator
        workflow = await self.orchestrator.start_workflow(
            workflow_type, instance_id, initial_data
        )

        # Delegate event publishing
        await self.event_bus.publish_workflow_event(
            ProtocolWorkflowEvent(
                workflow_type=workflow_type,
                instance_id=instance_id,
                event_type="started",
                sequence_number=1,
                data=initial_data
            )
        )

        # Delegate persistence
        await self.persistence.save_workflow_state(
            workflow_type, instance_id, workflow.state
        )

        return workflow
```

### Protocol Facade

Provide simplified interface to complex protocol subsystems:

```python
@runtime_checkable
class ProtocolServiceFacade(Protocol):
    """Facade for complex service operations."""

    # Internal protocols
    service_registry: ProtocolServiceRegistry
    health_monitor: ProtocolHealthMonitor
    metrics: ProtocolPerformanceMetrics
    logger: ProtocolLogger

    async def execute_service_operation(
        self,
        service_type: Type[T],
        operation: str,
        parameters: dict[str, ContextValue]
    ) -> ContextValue:
        """Execute service operation with full observability."""
        # Get service
        service = await self.service_registry.resolve_service(service_type)

        # Check health
        health = await self.health_monitor.get_current_health_status()
        if health != "healthy":
            raise ServiceUnavailableError("Service unhealthy")

        # Execute with monitoring
        start_time = time.time()
        try:
            result = await getattr(service, operation)(**parameters)
            await self.metrics.record_timing(f"{service_type.__name__}.{operation}", time.time() - start_time)
            await self.logger.log("INFO", f"Operation {operation} completed successfully")
            return result
        except Exception as e:
            await self.logger.log("ERROR", f"Operation {operation} failed: {e}")
            raise
```

## Advanced Patterns

### Protocol Chain

Chain protocols for sequential processing:

```python
@runtime_checkable
class ProtocolProcessingChain(Protocol):
    """Chain of processing protocols."""

    processors: list[ProtocolDataProcessor]

    async def process_data(
        self,
        data: ContextValue,
        context: dict[str, ContextValue]
    ) -> ContextValue:
        """Process data through chain of processors."""
        current_data = data

        for processor in self.processors:
            # Validate processor health
            if hasattr(processor, 'health_monitor'):
                health = await processor.health_monitor.get_current_health_status()
                if health != "healthy":
                    raise ProcessingError(f"Processor {processor.__class__.__name__} unhealthy")

            # Process data
            current_data = await processor.process(current_data, context)

        return current_data
```

### Protocol Pipeline

Pipeline protocols for parallel processing:

```python
@runtime_checkable
class ProtocolProcessingPipeline(Protocol):
    """Pipeline of parallel processing protocols."""

    processors: dict[str, ProtocolDataProcessor]

    async def process_data_parallel(
        self,
        data: ContextValue,
        context: dict[str, ContextValue]
    ) -> dict[str, ContextValue]:
        """Process data through parallel pipeline."""
        # Execute all processors in parallel
        tasks = []
        for name, processor in self.processors.items():
            task = asyncio.create_task(
                processor.process(data, context),
                name=name
            )
            tasks.append((name, task))

        # Collect results
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                results[name] = ProcessingError(f"Processor {name} failed: {e}")

        return results
```

## Best Practices

### Protocol Design

- **Single Responsibility**: Each protocol should have a clear, focused purpose
- **Composition over Inheritance**: Prefer composition for complex behaviors
- **Interface Segregation**: Keep interfaces focused and cohesive
- **Dependency Inversion**: Depend on abstractions, not concretions

### Performance Considerations

- **Async/Await**: Use async patterns for I/O operations
- **Connection Pooling**: Reuse connections where possible
- **Caching**: Cache frequently accessed data
- **Monitoring**: Include performance monitoring in compositions

### Error Handling

- **Specific Exceptions**: Define specific exception types
- **Error Context**: Include context information in errors
- **Recovery Strategies**: Implement appropriate recovery mechanisms
- **Logging**: Log errors with appropriate detail levels

## API Reference

- **[Container Protocols](api-reference/container.md)** - Dependency injection patterns
- **[Workflow Orchestration](api-reference/workflow-orchestration.md)** - Event-driven FSM
- **[MCP Integration](api-reference/mcp.md)** - Multi-subsystem coordination
- **[Event Bus](api-reference/event-bus.md)** - Distributed messaging

---

*For detailed protocol documentation, see the [API Reference](api-reference/README.md).*
