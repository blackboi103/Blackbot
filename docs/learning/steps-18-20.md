# OpenClaw Learning Notes: Steps 18-20

Status date: August 17, 2026

These notes describe the implemented learning milestones before Step 21. They
do not authorize a live Gateway connection, pairing request, message send,
commit, or push.

## Step 18: Offline OpenClaw Gateway Client

### Objective

Build a standalone Python adapter for OpenClaw protocol 4 without placing
Gateway credentials or cryptographic identity in browser code.

### Main concepts

1. WebSocket is the transport.
2. OpenClaw uses custom request, response, and event JSON frames.
3. The Gateway sends `connect.challenge` before authentication.
4. The client signs a version-3 payload with an Ed25519 private key.
5. Authentication and authorization are separate checks.
6. Request IDs correlate asynchronous responses.
7. Idempotency keys protect side-effecting requests from duplication.

### Backend modules

- `app/gateway_config.py`: loopback-only configuration and exact protocol/scope policy.
- `app/gateway_identity.py`: Ed25519 identity creation, validation, and atomic storage.
- `app/gateway_credentials.py`: prototype device-token persistence.
- `app/gateway_protocol.py`: frame parsing, challenge validation, signature payloads, and `hello-ok` checks.
- `app/gateway_client.py`: asynchronous connection, request correlation, events, timeouts, and safe shutdown.
- `app/gateway_prototype.py`: deliberately read-only command-line verification surface.

### Supported RPC wrappers

- `sessions.list`
- `chat.history`
- `chat.send`
- `chat.abort`
- `agent.wait`

`chat.send` exists in the adapter but is not exposed by the read-only prototype
command. A live send still requires a separate explicit authorization step.

### Security boundary

- Gateway URL defaults to `ws://127.0.0.1:18789`.
- Remote hosts are rejected unless a future configuration explicitly permits them.
- Required scopes are exactly `operator.read` and `operator.write`.
- The browser never receives a token, private key, or device token.
- Authentication failures do not trigger an automatic retry loop.
- Protocol, role, scope, and required-method mismatches fail closed.
- Stored PEM and device-token files remain prototype storage; DPAPI or Windows
  Credential Manager is still the hardened future design.

### Verification completed

Offline tests simulate challenge, authentication, `hello-ok`, events, requests,
device-token issuance, scope rejection, malformed JSON, and shutdown. No live
Gateway connection or pairing was performed.

### BlackBot lesson

BlackBot should inherit the adapter boundary, not the OpenClaw wire protocol.
Its Hermes/Ollama connection should implement a separate model/runtime adapter.

## Step 19: Mission Control Kanban Workspace

### Objective

Replace the mistaken custom chat interface with an Inky-inspired operational
workspace for tasks, agent visibility, projects, schedules, memory summaries,
documents, and future team views.

### Implemented interface

- Sidebar workspace navigation
- Kanban columns: Backlog, Ready, In Progress, Review, Done
- Demo task cards
- Drag-and-drop status movement
- Search and priority filters
- New-task dialog
- Task metrics
- Agent status and activity panel
- Visible OpenClaw-to-BlackBot privacy boundary

### Current limitation

The browser deliberately still uses temporary demo data. Connecting it to the
FastAPI task API is Step 21 and has not started.

### Security boundary

- No Gateway credentials appear in HTML, CSS, or JavaScript.
- The dashboard is presentation only.
- Planned navigation buttons do not silently perform privileged actions.

### BlackBot lesson

The UI should depend on stable application APIs, not directly on OpenClaw,
Hermes, Ollama, SQLite, or private files. That allows a future BlackBot backend
to replace the OpenClaw learning backend.

## Step 20: SQLite Task and Activity Backend

### Objective

Create a structured local source of truth for Mission Control tasks while
keeping Obsidian for human-readable knowledge rather than transactional data.

### Data flow

```text
Browser (Step 21)
    -> FastAPI validation
    -> TaskStore repository
    -> SQLite tasks and task_events tables
```

### Task fields

- ID
- Title and description
- Kanban status
- Priority
- Owner and tag
- Stable position within a Kanban column
- Archived flag
- Version number
- Created and updated timestamps

### Activity fields

- Event ID
- Task ID and task title
- Event type
- Previous and next status
- Detail
- Timestamp

### API surface

- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `POST /api/tasks`
- `PATCH /api/tasks/{task_id}`
- `DELETE /api/tasks/{task_id}` (soft archive)
- `GET /api/activity`

### Important patterns

- Pydantic validates untrusted request data.
- SQLite constraints provide a second validation layer.
- Parameterized SQL prevents values from becoming SQL instructions.
- Transactions keep task state and activity history consistent.
- Soft archiving preserves history.
- `PRAGMA user_version` establishes a migration boundary.
- Tests use temporary databases and do not create personal project data.

### Prototype limitations

- SQLite is not encrypted.
- Browser/API authentication is not implemented yet.
- There is no backup or migration command.
- Card reordering within one column is not exposed through the API yet.
- Project relationships, due dates, dependencies, and approvals are future schema work.

### BlackBot lesson

BlackBot can reuse validated models, repositories, transactions, migrations,
and append-only audit ideas. It should keep private financial and trading data
in stricter, separate stores that OpenClaw cannot read.

## Step 21 Boundary

Step 21 will replace the browser's demo task array with calls to the task and
activity APIs. Step 21 is not started and requires Kyle's explicit permission.
