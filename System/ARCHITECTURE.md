# BlackBot architecture — basic file foundation

Updated 2026-11-12. **Implemented here: knowledge structure, registry and read-only bounded retrieval. Not implemented here: autonomous orchestrator, specialist services, tool permissions or scheduler.**

## Goal
BlackBot is the long-term primary assistant coordinating independent specialists, not a trading-only agent. OpenClaw is a separate learning precursor. First Agent is the existing development collaborator (profile `robo`), not BlackBot's parent.

```text
User ↔ BlackBot coordinator
          ├─ First Agent / development collaboration
          ├─ TradingAI
          ├─ BudgetAI
          ├─ Research
          ├─ Project and Goals
          ├─ School and Career
          ├─ Car and Build
          └─ Content

Shared deterministic services (planned): tasks/state, approvals, permissions,
model routing, notifications, audit, structured data and retrieval.
```

Disk folders are siblings so no specialist accidentally owns every project. Coordination is explicit in [[System/agent-registry.json|the JSON registry]]; nesting is not an access-control boundary.

## Four layers
1. **Working context:** bounded task packet and current conversation.
2. **Operational state:** deterministic databases/services in their actual runtime homes. No relocation of bank ledgers or credentials into shared notes.
3. **Knowledge:** human-readable curated notes, original project files, provenance and decisions in this vault.
4. **Retrieval:** allowlisted context bundles now; optional derived indexes later. Raw files are opt-in, not automatically loaded.

## Authority and workflow
User-approved requirement → dated decision → implementation/source → independently exercised result. Proposals remain proposals. Each agent starts at START, then CURRENT_STATE and only task-relevant evidence. Return source paths, known limitations and next blocker to BlackBot. BlackBot aggregates results rather than copying private specialist data into every note.

Permissions, approvals, arithmetic, finance transaction identity and trading hard limits must be enforced in deterministic code. This document does not implement those controls or authorize orders, bank actions, purchases, publishing or unattended execution.

## Sources
[[Projects/BlackBot]]; [[Projects/Budget AI]]; [[Sources/2026-10-30 - BlackBot OpenClaw Project Handoff]]; [[Sessions/2026-11-12 - Vault Retrieval Setup]]. Newer specialist source: [[Agents/TradingAI/Files/Research/BlackBot Trading Agent/NORTH_STAR_AND_ROLLOUT]].
