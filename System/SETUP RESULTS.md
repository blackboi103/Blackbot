# Setup results — Qwen and BlackBot vault

Completed 2026-11-12 for Hermes profile `robo`, subject to the explicit active-file deferrals below.

## Qwen
- Persisted `num_ctx 262144` on the existing `qwen3.5:9b` model.
- Unloaded/reloaded and verified actual 262,144 allocation without a request-level context override.
- A real 77,149-input-token fixture recovered all three beginning/middle/end values and finished normally. The uncached request took about 80 seconds.
- Hermes configuration was not lowered or otherwise changed; its pre/post configuration hashes match.
- Original local model retained as `qwen3.5:9b-before-262k-20261112`; original configuration also saved in the backup.
- This is not a full-262K reasoning-quality certification. [[System/QWEN CONTEXT]].

## Knowledge foundation
- BlackBot is the coordinator; specialists own their records independently.
- Nine logical roles are registered with short entry notes: BlackBot, First Agent, TradingAI, BudgetAI, Research, Project and Goals, School and Career, Car and Build, Content.
- These files document a basic architecture. They do not install an autonomous orchestrator or deploy nine running agents.
- Read-only `Tools/vault_context.py` builds bounded, cited packets from curated notes only. Five regression tests passed, including source privacy/path checks and the character-budget boundary.
- Qwen answered the five relationship/deferral questions correctly from an 839-token typed-schema prompt. An earlier generic-JSON probe returned wrong field types; explicit string/boolean definitions plus schema resolved the interface issue. No failed probe was relabeled as success.
- First Agent notes no longer claim the invalid old context test passed; timezone, memory and cron assertions were corrected.

## Originals and preservation
- **1,997 original files relocated from outside the vault**, across eight source sets, with per-file SHA-256 verification:
  - Trading research: 1,871 files.
  - Original ChatGPT export/import collection: 120 files.
  - Six reviewed source-package/Markdown/journal files.
- Eight original project summaries restored to global `Projects/` with their contents unchanged.
- All 192 preexisting ChatGPT Archive files remain SHA-256-identical.
- The redundant old 1,871-file research copy is in the private durable backup, not another active vault copy and not deleted.
- Former Documents research and Downloads/Memory paths are Windows junctions to the same originals now physically in the vault.
- Both named OneDrive BlackBot folders were empty; zero OneDrive files moved or deleted.

## Explicitly deferred / outside migration scope
- Running `C:/Users/Kyle Adolphe/Projects/budget-ai` and open Excel workbooks remain where they were, as requested. Git status/diff fingerprints and all 117 classified nonfinancial source/doc/asset hashes matched the preflight check.
- Financial intake/master selection, operational bank ledgers, credentials, live Hermes/OpenClaw runtime state and unrelated/ambiguous personal files were not swept into the vault.
- Raw export/browser evidence and private journal files are excluded from default packets. Folder exclusion is not OS isolation or safe-publication clearance; do not publish/sync raw private material blindly.

## Where to start
[[System/AGENT REGISTRY]] · [[System/RETRIEVAL]] · [[System/FILE LOCATIONS]] · [[Agents/BlackBot/START]]

Example:
```bash
python "C:/Users/Kyle Adolphe/HermesVault/Tools/vault_context.py" tradingai --max-chars 8000 --json
```

Backup: `C:/Users/Kyle Adolphe/AppData/Local/hermes/profiles/robo/backups/vault-migration-20261112-212738/`.
Verification outputs: `robo/reports/vault-setup-verification-typed.json`, `vault-migration-final-checks.json`, and `qwen-262k/persisted-and-over64k-test.json` under the actual profile home.

Source/approval trail: [[Sessions/2026-11-12 - Vault Retrieval Setup]] and [[Sources/2026-11-12 - Vault Setup User Authorization]].
