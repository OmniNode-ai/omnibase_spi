# Protocol Selection Guide

## Decision Framework

A comprehensive guide for choosing the right protocols for your use case.

## Core System Protocols

### When to Use Core Protocols

**Use Core Protocols when you need:**
- System-level observability and monitoring
- Error handling and recovery
- Performance metrics and monitoring
- Service discovery and registration

**Key Protocols:**
- `ProtocolLogger` - Structured logging across services
- `ProtocolHealthMonitor` - Health monitoring and status tracking
- `ProtocolErrorHandler` - Centralized error handling
- `ProtocolPerformanceMetrics` - Performance monitoring

## Container Management Protocols

### When to Use Container Protocols

**Use Container Protocols when you need:**
- Dependency injection and service lifecycle management
- Circular dependency detection
- Service health monitoring
- Factory patterns and injection contexts

**Key Protocols:**
- `ProtocolServiceRegistry` - Service registration and resolution
- `ProtocolServiceFactory` - Service instance creation
- `ProtocolDependencyGraph` - Dependency analysis
- `ProtocolInjectionContext` - Injection context management

## Workflow Orchestration Protocols

### When to Use Workflow Protocols

**Use Workflow Protocols when you need:**
- Event-driven workflow orchestration
- Event sourcing with sequence numbers
- Workflow state management and projections
- Distributed task scheduling

**Key Protocols:**
- `ProtocolWorkflowOrchestrator` - Workflow lifecycle management
- `ProtocolWorkflowEventBus` - Event-driven coordination
- `ProtocolWorkflowPersistence` - State persistence
- `ProtocolWorkQueue` - Task scheduling

## MCP Integration Protocols

### When to Use MCP Protocols

**Use MCP Protocols when you need:**
- Multi-subsystem tool coordination
- Dynamic tool discovery and routing
- Load balancing across implementations
- Tool execution tracking and monitoring

**Key Protocols:**
- `ProtocolMCPRegistry` - Tool registration and discovery
- `ProtocolMCPToolProxy` - Tool execution coordination
- `ProtocolMCPMonitor` - Health monitoring
- `ProtocolMCPSubsystemClient` - Subsystem communication

## Event Bus Protocols

### When to Use Event Bus Protocols

**Use Event Bus Protocols when you need:**
- Distributed messaging infrastructure
- Event publishing and subscription
- Message serialization and routing
- Dead letter queue handling

**Key Protocols:**
- `ProtocolEventBus` - Core event messaging
- `ProtocolKafkaAdapter` - Kafka integration
- `ProtocolEventPublisher` - Event publishing
- `ProtocolDLQHandler` - Dead letter queue handling

## Memory Management Protocols

### When to Use Memory Protocols

**Use Memory Protocols when you need:**
- Key-value storage operations
- Workflow state persistence
- Memory security and streaming
- Agent coordination and management

**Key Protocols:**
- `ProtocolMemoryBase` - Basic memory operations
- `ProtocolMemoryOperations` - Advanced memory operations
- `ProtocolMemorySecurity` - Security and encryption
- `ProtocolAgentManager` - Agent coordination

## Networking Protocols

### When to Use Networking Protocols

**Use Networking Protocols when you need:**
- HTTP client operations
- Kafka integration
- Circuit breaker patterns
- Communication bridges

**Key Protocols:**
- `ProtocolHttpClient` - HTTP operations
- `ProtocolKafkaClient` - Kafka integration
- `ProtocolCircuitBreaker` - Circuit breaker patterns
- `ProtocolCommunicationBridge` - Protocol bridging

## File Handling Protocols

### When to Use File Handling Protocols

**Use File Handling Protocols when you need:**
- File reading and writing operations
- File type detection and processing
- Directory traversal and discovery
- File I/O optimization

**Key Protocols:**
- `ProtocolFileReader` - File reading operations
- `ProtocolFileWriter` - File writing operations
- `ProtocolFileTypeHandler` - Type detection
- `ProtocolDirectoryTraverser` - Directory traversal

## Validation Protocols

### When to Use Validation Protocols

**Use Validation Protocols when you need:**
- Input validation and sanitization
- Schema validation and compliance
- Quality assurance and testing
- Pre-commit validation

**Key Protocols:**
- `ProtocolValidation` - Core validation
- `ProtocolComplianceValidator` - Compliance checking
- `ProtocolInputValidationTool` - Input validation
- `ProtocolPrecommitChecker` - Pre-commit validation

## Selection Decision Tree

### 1. What is your primary use case?

**System Operations** → Core Protocols
**Service Management** → Container Protocols
**Workflow Processing** → Workflow Orchestration Protocols
**Tool Coordination** → MCP Integration Protocols
**Event Processing** → Event Bus Protocols
**Data Storage** → Memory Management Protocols
**Communication** → Networking Protocols
**File Operations** → File Handling Protocols
**Data Validation** → Validation Protocols

### 2. Do you need multiple capabilities?

**Yes** → Use Protocol Composition Patterns
**No** → Use individual protocols

### 3. What is your performance requirement?

**High Performance** → Use async protocols with optimization
**Standard Performance** → Use standard protocol implementations
**Development/Testing** → Use in-memory or lightweight protocols

### 4. What is your deployment environment?

**Distributed** → Use protocols with clustering support
**Single Node** → Use protocols with local optimization
**Cloud** → Use protocols with cloud integration

## Best Practices

### Protocol Selection

1. **Start Simple** - Begin with core protocols and add complexity as needed
2. **Compose Gradually** - Build complex behaviors from simpler protocols
3. **Consider Performance** - Choose protocols that match your performance requirements
4. **Plan for Scale** - Select protocols that can scale with your needs

### Integration Patterns

1. **Dependency Injection** - Use container protocols for service management
2. **Event-Driven** - Use event bus protocols for loose coupling
3. **Health Monitoring** - Include health monitoring in all critical services
4. **Error Handling** - Implement comprehensive error handling

## API Reference

- **[Core Protocols](../api-reference/CORE.md)** - System fundamentals
- **[Container Protocols](../api-reference/CONTAINER.md)** - Dependency injection
- **[Workflow Orchestration](../api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM
- **[MCP Integration](../api-reference/MCP.md)** - Multi-subsystem coordination
- **[Event Bus](../api-reference/EVENT-BUS.md)** - Distributed messaging
- **[Memory Management](../api-reference/MEMORY.md)** - Memory operations
- **[Networking](../api-reference/NETWORKING.md)** - Communication protocols
- **[File Handling](../api-reference/FILE-HANDLING.md)** - File operations
- **[Validation](../api-reference/VALIDATION.md)** - Input validation

---

*For detailed protocol documentation, see the [API Reference](../api-reference/README.md).*
