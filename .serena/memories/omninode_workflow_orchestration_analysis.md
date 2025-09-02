# OmniNode Workflow Orchestration System Analysis

## Document Overview
Analysis of 4 key documents describing an event-sourced workflow orchestration system:

1. **OmniNode Reducer Pattern** - Multi-workflow execution with instance isolation
2. **Reducer Subcontracts & Orchestration** - RSS as single source of truth, derived orchestration
3. **Persistence & Recovery Pattern** - Event sourcing with snapshots and projectors
4. **Repository Split Strategy** - SPI/Core/Infrastructure separation

## Core Concepts

### Event-Sourced FSM Architecture
- **State Shape**: `workflows[workflowType][instanceId]` with FSM state, data, sequence tracking
- **Event Shape**: Typed events with workflowType, instanceId, seq, causationId, correlationId
- **Reducer Pattern**: Top-level router → workflow subreducers → FSM transitions → effects/computes

### RSS (Reducer State Subcontracts)
- YAML-defined state machines with dispatch annotations
- Single source of truth for both reducer logic AND orchestration behavior
- Hierarchical states, guards, transitions with effects[] and computes[]
- Automatic code generation potential for reducers, validators, diagrams

### Orchestration Flow
```
Event → Reducer (RSS) → {newState, effects[], computes[]} → Orchestrator
→ Route to compute/effect nodes → Result events → Loop continues
```

### Persistence Strategy
- **Event Store**: Append-only with (workflowType, instanceId, seq) ordering
- **Snapshots**: Periodic state checkpoints to reduce replay cost  
- **Projectors**: Event-driven read models and analytics
- **Transactional Outbox**: Atomic event publishing + persistence

### Repository Architecture
- **SPI**: Pure contracts, interfaces, schemas, constants
- **Core**: Domain logic, reducers, RSS specs, dev adapters (in-memory)
- **Infrastructure**: Production adapters (Kafka, Postgres, observability)

## Key Technical Patterns
- Instance isolation via correlation IDs
- Idempotent event processing with sequence numbers
- Hierarchical/parallel substates in FSMs
- Deterministic replay from event logs
- Fire-and-forget vs await semantics for effects
- Retry policies and timeout handling

## Repository Mapping to Current Architecture
Given existing repos: omnibase-core, omnibase-spi, omniagent, omnimcp
- omnibase-spi: Add workflow contracts, RSS schemas, orchestration ports
- omnibase-core: Add reducer implementations, orchestration engine, dev adapters
- New omnibase-infrastructure: Production persistence, event bus, observability
- Consider omniagent integration for distributed compute nodes

## Strategic Value
Prepares for distributed system execution with:
- Workflow coordination across services
- Fault-tolerant state management
- Replay-based debugging and recovery
- Scalable event-driven architecture
- Contract-first orchestration design