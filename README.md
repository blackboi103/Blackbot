# OpenClaw Learning Project

Engineering classroom and prototype laboratory for the future BlackBot system.

## Current Stage

Steps 18-20 are code-complete and offline-verified:

- OpenClaw Gateway protocol adapter and read-only prototype
- Mission Control Kanban workspace
- SQLite task and activity backend

Step 21, connecting the browser board to the task API, has not started.

The human-facing interface is a Kanban-style operations workspace inspired by
Tina Huang's Inky Mission Control setup. It is not intended to replace
OpenClaw's chat interfaces. The workspace will eventually surface tasks,
projects, agent activity, schedules, memory summaries, documents, and team
status while keeping Gateway credentials and privileged operations in the
Python backend.

## Current Architecture

- Browser code is presentation only and never receives Gateway secrets.
- The Gateway adapter is isolated in backend Python modules.
- FastAPI exposes local task and activity endpoints under `/api`.
- SQLite stores structured task state and append-only task activity in
  `data/mission_control.db`.
- Archiving hides a task without deleting its activity history.
- The browser still uses demo task data until Step 21 is explicitly started.

## Project Purpose

OpenClaw is a precursor and learning project for BlackBot. Its purpose is to
provide a practical environment for learning how to design, build, secure, and
operate an advanced AI agent.

OpenClaw is not intended to remain the permanent primary assistant. The
knowledge, architecture lessons, integrations, security practices, and
development experience gained from OpenClaw will be documented and eventually
used to build BlackBot.

## Long-Term Goal: BlackBot

BlackBot is the eventual primary local AI agent. It is intended to run locally
using Hermes and Ollama, with privacy, local control, and extensibility as major
design goals.

BlackBot will eventually incorporate capabilities developed and learned through
OpenClaw, including:

- General AI assistance
- Persistent memory
- Obsidian integration
- File management
- Email
- Calendar
- FIU/Canvas integration
- Task and project management
- Budgeting
- Automation
- Tool use
- Appropriate web access
- Agent orchestration

BlackBot will additionally have a specialized trading capability that OpenClaw
does not need to implement.

Trading development will progress through:

1. Research
2. Backtesting
3. Simulation
4. Paper trading
5. Controlled validation
6. Explicitly authorized live trading, if ever enabled

Live trading must never be enabled automatically.

## Knowledge Transfer

OpenClaw will document important development knowledge in Obsidian, including:

- Architecture decisions
- Development and security lessons
- Integration knowledge
- Problems and solutions
- Failed and deprecated approaches
- Future improvements
- Lessons applicable to BlackBot

The intended flow is:

```text
OpenClaw -> approved shared Obsidian knowledge -> BlackBot
```

BlackBot should learn from the documented OpenClaw experience rather than
starting from zero. OpenClaw must not read BlackBot's private workspace,
memory, financial records, trading records, credentials, or other private data.

## Development Philosophy

Development should prioritize understanding over simply completing tasks. For
major components, documentation should explain:

- What is being built
- Why it is needed
- How it works
- Security considerations
- What was learned
- How the concept transfers to BlackBot

## OpenClaw Learning Goals

- Personal AI assistance
- Calendar and email organization
- FIU Canvas integration
- Academic planning
- Personal budgeting and financial tracking
- Mission Control/Kanban project management
- Agent and task visibility
- Reusable integration and security patterns for BlackBot

Trading analysis, backtesting, paper trading, and any later controlled live
execution belong to BlackBot rather than this OpenClaw learning project.

## Learning Notes

- [Steps 18-20](docs/learning/steps-18-20.md)
