# Agent registry

Coordinator: **BlackBot**. These are logical roles, not newly launched processes.

| Agent | Role | Start | State |
|---|---|---|---|
| BlackBot | Coordinator, primary assistant and specialist result aggregator; not trading-only. | [[Agents/BlackBot/START]] | Architecture and knowledge registry only; no orchestrator process installed by this task. |
| First Agent | Developer/assistant collaborator; Hermes profile robo. Coordinates with BlackBot without becoming its parent. | [[Agents/First Agent/START]] | Existing assistant profile; vault folder documents it and does not relocate its runtime. |
| TradingAI | BlackBot trading research, guarded paper-trading and journal specialist. | [[Agents/TradingAI/START]] | Preserved strategy/research and rollout plans; live market/paper pipeline not activated. |
| BudgetAI | BlackBot private finance specialist; deterministic calculations, review approvals and bank boundaries. | [[Agents/BudgetAI/START]] | Existing repository remains external while running; no financial operations authorized by this migration. |
| Research | Cited source verification and reusable research; no automatic access to private finances. | [[Agents/Research/START]] | SOUL.md + README.md fully written 2026-11-13; no dedicated runtime profile yet. |
| Project and Goals | Projects, milestones, priorities, dependencies and next actions. | [[Agents/Project and Goals/START]] | SOUL.md + README.md fully written 2026-11-13; no dedicated runtime profile yet. |
| School and Career | Assignments, study, calendars and career planning. | [[Agents/School and Career/START]] | SOUL.md + README.md fully written 2026-11-13; no dedicated runtime profile yet. |
| Car and Build | Vehicle evidence, repairs, parts and build planning. | [[Agents/Car and Build/START]] | SOUL.md + README.md fully written 2026-11-13; no dedicated runtime profile yet. |
| Content | Content ideas, scripts, scheduling and analytics. | [[Agents/Content/START]] | SOUL.md + README.md fully written 2026-11-13; no dedicated runtime profile yet. |

"Developer" (from the 2026-11-13 six-agent design brief) is merged into **First Agent** rather than a separate folder — same running agent, same role, documented once; user confirmed the merge 2026-11-13. See [[Agents/First Agent/README]] and [[Agents/First Agent/SOUL]].

Shared rules common to every specialist: [[System/SHARED AGENT STANDARDS]]. Machine-readable routing: `System/agent-registry.json`. See [[System/ARCHITECTURE]] and [[System/RETRIEVAL]].
