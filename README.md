# BlackBot Orchestrator

## Overview
This is the **central coordination repository** for the BlackBot multi-agent system. 

**What's in this repo:**
- Core agent registry and routing logic
- Shared permissions and approval frameworks  
- Context retrieval protocol (vault_context.py)
- System architecture documentation
- Agent-to-agent communication patterns
- Health checks and monitoring hooks

## What to Use This For
- Coordinate work across all specialist agents
- Manage task queues and approval workflows
- Handle notifications and alerts
- Audit logging and state tracking
- Model routing for different tasks

## NOT For:
- Individual agent's domain-specific code (each agent has its own repo)
- Private financial data (BudgetAI keeps that separate)
- Trading execution logic (TradingAI handles that)

## Quick Start
```bash
# Initialize your environment
python Tools/vault_context.py blackbot --max-chars 8000

# Check system status
python Tools/system_status.py

# View agent registry
cat System/agent-registry.json
```

## Repository Structure
- `System/` - Core coordination, permissions, registry
- `Tools/` - Context retrieval and utility scripts
- `Tests/` - Integration tests for multi-agent workflows
- `docs/` - Architecture and usage documentation

## Related Repositories
- TradingAI: Trading strategies and paper trading
- BudgetAI: Financial management (separate repo)
- Research-Agent: Market research and analysis
- Project-Goals: Project planning and milestones
