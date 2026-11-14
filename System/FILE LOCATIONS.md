# Canonical file locations and relocation exceptions

Updated 2026-11-12. Originals are moved only after exact manifest verification; backups are not competing working copies.

| Collection | Canonical location | Old location/status |
|---|---|---|
| Project summaries (8) | `HermesVault/Projects/` | Restored from incorrect TradingAI nesting |
| Trading research originals | `HermesVault/Agents/TradingAI/Files/Research/` | `Documents/Trading Strategy Research/` is now a compatibility junction to this same tree |
| Trading source packages | `HermesVault/Agents/TradingAI/Files/Source Packages/` | Moved exact reviewed archives/Markdown from Documents and Downloads |
| Trading journal | `HermesVault/Agents/TradingAI/Files/Private/Trading Journal.pdf` | Original relocated; private, excluded from default packets |
| BlackBot WebUI original ZIP | `HermesVault/Agents/BlackBot/Files/Source Packages/BlackBot_WebUI_v0.2_Agent_Kanban.zip` | Moved from Downloads; active modified frontend remains inside BudgetAI repo |
| ChatGPT export/import originals (120 files) | `HermesVault/Sources/Files/ChatGPT Export Original/` | Former `Downloads/Memory/` is a compatibility junction to these same originals; raw content excluded from packets |
| BudgetAI live repository | `C:/Users/Kyle Adolphe/Projects/budget-ai/` | **Deferred explicitly by user while running** |
| Budget workbooks | Existing Documents/OneDrive/repository locations | **Open workbooks deferred explicitly by user**; no master choice or financial edits |
| Hermes runtime/profile/secrets | `C:/Users/Kyle Adolphe/AppData/Local/hermes/profiles/robo/` | Intentionally outside vault; not relocated |
| OpenClaw runtime | Existing external runtime | Separate learning environment; not blindly moved into BlackBot |

Both `OneDrive/Documents/BlackBot` and `OneDrive/Documents/Blackbot Files` were independently checked and are empty: zero files to migrate. No OneDrive cloud deletion was performed.

Unclassified personal artifacts and finance records outside the approved inactive source sets remain in place. Personal medical/tax records, unrelated downloads, installers, games, operational bank ledgers and credentials are not part of a blanket project migration. Budget workbook copies/financial intake need a separately verified master/privacy/active-use plan; do not infer they were all moved.

## Preservation
Pre-migration backup: `C:/Users/Kyle Adolphe/AppData/Local/hermes/profiles/robo/backups/vault-migration-20261112-212738/`.
Contains verified vault ZIP/manifest, BudgetAI authored-source/Git snapshot, Qwen original configuration and migration logs. The previous duplicate TradingAI bulk copy was moved into that backup, not recursively deleted.

## Retrieval and privacy
The original research keeps its dependencies and raw evidence for reproducibility. Default context packets exclude Files/, Private/, dependency trees and raw browser data. Do not publish/sync the vault blindly: raw browser captures include token/signed-link fields and the journal is personal. Read source-specific material only within an explicit task.

[[System/RETRIEVAL]]; [[Sessions/2026-11-12 - Vault Retrieval Setup]].
