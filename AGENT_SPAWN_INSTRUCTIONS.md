# Agent Spawn Instructions - SPI Remediation

**Quick reference for spawning 8 parallel agent-workflow-coordinators**

---

## Track 1: Critical Async Fix

**Agent**: `agent-quick-fix`
**Branch**: `feature/spi-track-1-async-fix`
**Duration**: 15 minutes
**Dependencies**: None

**Task**:
```
Fix 1 SPI005 error in protocol_core_types.py:1549
Change method signature to async def for I/O operations
```

**Files**:
- `src/omnibase_spi/protocols/types/protocol_core_types.py`

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/types/protocol_core_types.py --json-report
grep "SPI005" comprehensive_spi_validation_*.json
```

---

## Track 2: Core Domain Conflicts

**Agent**: `agent-core-domain-fix`
**Branch**: `feature/spi-track-2-core-conflicts`
**Duration**: 45 minutes
**Dependencies**: None

**Task**:
```
Resolve 3 protocol name conflicts:
1. ProtocolDiscoveredTool (CLI domain → ProtocolCliDiscoveredTool)
2. ProtocolRegistryWithBus (EventBus domain → ProtocolEventBusRegistry)
3. ProtocolLogEmitter (EventBus domain → ProtocolEventBusLogEmitter)
```

**Files**:
- `src/omnibase_spi/protocols/cli/protocol_cli_tool_discovery.py`
- `src/omnibase_spi/protocols/event_bus/protocol_event_bus_mixin.py`
- `src/omnibase_spi/protocols/discovery/protocol_discovery_client.py`
- `src/omnibase_spi/protocols/types/protocol_core_types.py`

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/{discovery,cli,event_bus}/ \
  src/omnibase_spi/protocols/types/protocol_core_types.py --json-report
```

---

## Track 3: Agent Protocol Conflicts

**Agent**: `agent-memory-domain-fix-1`
**Branch**: `feature/spi-track-3-agent-conflicts`
**Duration**: 90 minutes
**Dependencies**: None

**Task**:
```
Resolve 9 agent-related protocol conflicts:
- ProtocolAgentConfig (3 conflicts) → Import from canonical
- ProtocolAgentInstance (3 conflicts) → Rename with domain prefixes
- ProtocolAgentHealthStatus (2 conflicts) → Import from canonical
- ProtocolAgentStatus (1+ conflicts) → Rename with domain prefixes
```

**Files**:
- `src/omnibase_spi/protocols/memory/protocol_agent_manager.py` (canonical)
- `src/omnibase_spi/protocols/memory/protocol_agent_pool.py` (update)
- `src/omnibase_spi/protocols/memory/protocol_distributed_agent_orchestrator.py` (update)
- `src/omnibase_spi/protocols/memory/protocol_agent_config_interfaces.py` (canonical)
- `src/omnibase_spi/protocols/mcp/protocol_llm_agent_provider.py` (rename)
- `src/omnibase_spi/protocols/types/protocol_event_bus_types.py` (rename)

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/memory/ \
  src/omnibase_spi/protocols/mcp/protocol_llm_agent_provider.py --json-report
```

---

## Track 4: Memory Conflicts Part 1

**Agent**: `agent-memory-domain-fix-2`
**Branch**: `feature/spi-track-4-memory-conflicts-1`
**Duration**: 90 minutes
**Dependencies**: Track 3 (for context)

**Task**:
```
Resolve 8 memory protocol conflicts:
- ProtocolValidationResult (2 conflicts) → Rename in memory domain
- ProtocolMemoryOperation (1 conflict) → Consolidate
- ProtocolMemoryResponse (2 conflicts) → Import from responses module
- ProtocolMemoryMetadata (2 conflicts) → Import from base module
```

**Files**:
- `src/omnibase_spi/protocols/memory/protocol_agent_pool.py` (update)
- `src/omnibase_spi/protocols/memory/protocol_distributed_agent_orchestrator.py` (update)
- `src/omnibase_spi/protocols/validation/protocol_validation.py` (canonical)
- `src/omnibase_spi/protocols/memory/protocol_memory_responses.py` (canonical)
- `src/omnibase_spi/protocols/memory/protocol_memory_base.py` (canonical)

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/memory/ \
  src/omnibase_spi/protocols/validation/ --json-report
```

---

## Track 5: Memory Conflicts Part 2

**Agent**: `agent-memory-domain-fix-3`
**Branch**: `feature/spi-track-5-memory-conflicts-2`
**Duration**: 90 minutes
**Dependencies**: None (parallel with Track 4)

**Task**:
```
Resolve 8 memory protocol conflicts:
- ProtocolMemoryError (2 conflicts) → Import from errors module
- ProtocolMemoryRequest (2 conflicts) → Import from requests module
- ProtocolMemoryResponseV2 (1 conflict) → Consolidate
- ProtocolMemorySecurityContext (2 conflicts) → Import from security module
```

**Files**:
- `src/omnibase_spi/protocols/memory/protocol_agent_pool.py` (update)
- `src/omnibase_spi/protocols/memory/protocol_distributed_agent_orchestrator.py` (update)
- `src/omnibase_spi/protocols/memory/protocol_memory_errors.py` (canonical)
- `src/omnibase_spi/protocols/memory/protocol_memory_requests.py` (canonical)
- `src/omnibase_spi/protocols/memory/protocol_memory_security.py` (canonical)

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/memory/ --json-report
```

---

## Track 6: Memory Conflicts Part 3

**Agent**: `agent-memory-domain-fix-4`
**Branch**: `feature/spi-track-6-memory-conflicts-3`
**Duration**: 60 minutes
**Dependencies**: None (parallel with Tracks 4-5)

**Task**:
```
Resolve 4 remaining memory protocol conflicts:
- ProtocolMemoryStreamingResponse (1 conflict) → Consolidate
- ProtocolMemoryStreamingRequest (1 conflict) → Consolidate
- ProtocolMemorySecurityPolicy (1 conflict) → Consolidate
- ProtocolMemoryComposable + ProtocolMemoryErrorHandling (2 conflicts) → Consolidate
```

**Files**:
- `src/omnibase_spi/protocols/memory/protocol_agent_pool.py` (canonical for some)
- `src/omnibase_spi/protocols/memory/protocol_distributed_agent_orchestrator.py` (remove duplicates)
- `src/omnibase_spi/protocols/memory/protocol_memory_requests.py` (possibly canonical)
- `src/omnibase_spi/protocols/memory/protocol_memory_responses.py` (possibly canonical)
- `src/omnibase_spi/protocols/memory/protocol_memory_security.py` (possibly canonical)

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/memory/ --json-report
```

---

## Track 7: Semantic Duplicates

**Agent**: `agent-semantic-consolidation`
**Branch**: `feature/spi-track-7-semantic-duplicates`
**Duration**: 120 minutes
**Dependencies**: Tracks 3-6 (verify their completion)

**Task**:
```
Verify and consolidate 25 semantically duplicate protocols:
- Verify Tracks 3-6 resolved most duplicates
- Analyze remaining:
  * ProtocolValidationResult vs ProtocolLegacyConfigValidationResult
  * ProtocolBatchMemoryRetrieveRequest vs ProtocolMemoryRetrieveRequest
  * ProtocolWorkflowInputState vs ProtocolOnexInputState
```

**Files**:
- `src/omnibase_spi/protocols/memory/protocol_memory_requests.py`
- `src/omnibase_spi/protocols/types/protocol_workflow_orchestration_types.py`
- Various files from Tracks 3-6 (verification)

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/omnibase_spi/protocols/ --json-report
grep "SPI010" comprehensive_spi_validation_*.json | wc -l
```

---

## Track 8: Documentation Strategy

**Agent**: `agent-documentation-framework`
**Branch**: `feature/spi-track-8-documentation`
**Duration**: 180 minutes (decision) + ongoing
**Dependencies**: None (parallel with all)

**Task**:
```
Phase 1 (3 hours): Define documentation policy
- Set documentation standards (tiers 1-3)
- Create protocol documentation templates
- Define automation strategy
- Establish quality thresholds

Phase 2 (Ongoing): Systematic implementation
- Categorize 321 protocols by tier
- Process Tier 1 protocols (high priority)
- Create batch documentation tasks
```

**Files to Create**:
- `docs/SPI_DOCUMENTATION_POLICY.md`
- `scripts/templates/protocol_docstring_generator.py`
- `scripts/analysis/categorize_protocols.py`
- `protocol_documentation_plan.yaml`

**Validation**:
```bash
python scripts/validation/comprehensive_spi_validator.py \
  src/ --json-report
grep "SPI014" comprehensive_spi_validation_*.json | wc -l
```

---

## Execution Order

### Phase 1: Error Elimination (Parallel)
```
START
  ├─ Track 1 (15 min)  ─┐
  ├─ Track 2 (45 min)  ─┤
  ├─ Track 3 (90 min)  ─┤
  ├─ Track 4 (90 min)  ─┼─→ VALIDATION GATE 1 → INTEGRATION
  ├─ Track 5 (90 min)  ─┤
  └─ Track 6 (60 min)  ─┘
```

### Phase 2: Quality Improvements (Parallel)
```
INTEGRATION COMPLETE
  ├─ Track 7 (120 min) ─→ VALIDATION GATE 2 → MERGE
  └─ Track 8 (ongoing) ─→ DOCUMENTATION MILESTONES
```

---

## Integration Commands

### After Phase 1 (Tracks 1-6)
```bash
git checkout -b feature/spi-integration
git merge feature/spi-track-1-async-fix
git merge feature/spi-track-2-core-conflicts
git merge feature/spi-track-3-agent-conflicts
git merge feature/spi-track-4-memory-conflicts-1
git merge feature/spi-track-5-memory-conflicts-2
git merge feature/spi-track-6-memory-conflicts-3

# Validate
python scripts/validation/comprehensive_spi_validator.py src/ --json-report

# Expected: 0 errors, <346 warnings
```

### After Phase 2 (Track 7)
```bash
git merge feature/spi-track-7-semantic-duplicates

# Validate
python scripts/validation/comprehensive_spi_validator.py src/ --json-report

# Expected: 0 errors, <100 warnings (mostly SPI014 docs)
```

---

## Success Criteria Summary

| Track | Metric | Target |
|-------|--------|--------|
| 1 | SPI005 errors | 0 |
| 2 | SPI011 conflicts resolved | 3 |
| 3 | SPI011 conflicts resolved | 9 |
| 4 | SPI011 conflicts resolved | 8 |
| 5 | SPI011 conflicts resolved | 8 |
| 6 | SPI011 conflicts resolved | 4 |
| 7 | SPI010 warnings | 0 |
| 8 | SPI014 warnings | <160 (50% reduction) |

**Overall**:
- Total errors: 0
- Total warnings: <200
- Code quality score: >85%

---

## Quick Commands Reference

```bash
# Create branch
git checkout -b feature/spi-track-{N}-{description}

# Validate single file
python scripts/validation/comprehensive_spi_validator.py {file_path} --json-report

# Validate directory
python scripts/validation/comprehensive_spi_validator.py {dir_path}/ --json-report

# Check specific rule violations
grep "{RULE_ID}" comprehensive_spi_validation_*.json

# Commit and push
git add .
git commit -m "fix(spi): Track {N} - {description}"
git push origin feature/spi-track-{N}-{description}

# Create PR
gh pr create --title "SPI Track {N}: {description}" \
  --body "Part of 8-track SPI remediation. Resolves {X} violations."
```

---

**For detailed instructions, see**: `SPI_REMEDIATION_PLAN.md`
