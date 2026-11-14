# Discord runtime — verified chat connections

## Scope and approval
The user approved configuring Blackbot, TradingAI and BudgetAI to work in **BlackBot Prototype Server**. This setup enables owner-authorized assistant chat; it does not activate trading, banking, scheduled routines or automatic cross-agent orchestration.

## Active mapping
| Discord bot | Hermes profile | Mention-free channels |
|---|---|---|
| Blackbot | `blackbot` (new profile) | `#general`, `#alerts`, `#research`, `#morning-digest`, `#evening-review` |
| TradingAI | `tradingai` (existing profile) | `#trading-tasks`, `#tradingai-private` |
| BudgetAI | `budgetai` (existing profile) | `#budget-tasks`, `#budgetai-private` |

First Agent remains the separate `robo` profile, unchanged in identity. Specialists also accept owner @mentions in `#general` and `#alerts`. Guild channel allowlists exclude other specialist rooms. Owner DMs are supported by the adapter but were not exercised in this test.

## Configuration
- The three applications have separate bot tokens stored using Hermes's supported `.env` writer in their respective profiles; no tokens are included here.
- `DISCORD_ALLOWED_USERS` is restricted to the verified shared application owner, `487739819427102720`.
- Mentions remain required outside each bot's free-response rooms. Responses are inline; automatic threading is disabled.
- Bot-authored input is ignored, avoiding accidental reply loops. No bot-to-bot handoff automation has been enabled.
- History backfill and missed-message replay are disabled; setup did not replay old requests.
- Local model stays **Qwen `qwen3.5:9b`**, served by Ollama at `http://localhost:11434/v1`.
- TradingAI/BudgetAI initially failed because their configured `HERMES_CUSTOM_QWEN_API_KEY` slot was absent in their own profile scope. The existing local-model setting was copied using the supported writer; a routed-profile resolution check failed before and passed after the repair.
- Role-specific SOUL files identify each agent and reference its bounded vault context. Relevant specialist skills were added to the existing specialist profiles. These are behavior/context settings, not OS isolation.

## Verification — 2026-11-13
The user sent real messages through their logged-in Discord client and confirmed normal responses after the local-model fix. Gateway logs show an actual model API call for each successful response. Replies were independently fetched from Discord, not inferred from send success:

- [Blackbot reply](https://discord.com/channels/1570641308337442968/1570641308828041238/1570846544792657962): successful greeting; gateway duration **18.1 s**, **1 model call**.
- [TradingAI reply](https://discord.com/channels/1570641308337442968/1570646381775953980/1570847542441287703): "Pong!" and specialist introduction; **11.7 s**, **1 model call**.
- [BudgetAI reply](https://discord.com/channels/1570641308337442968/1570646483420581969/1570847592856690811): "Pong!" and finance-assistant introduction; **10.9 s**, **1 model call**.

The shared gateway state reported all **3/3** profile Discord adapters connected, with no attention/error flag. Detailed credential-free evidence: `C:/Users/Kyle Adolphe/AppData/Local/hermes/profiles/robo/reports/discord-live-verification.json`.

## Runtime requirements and limits
The PC, Ollama and the shared Hermes gateway must remain running and network-connected. No new boot/autostart policy was installed or tested. No server role/channel permissions were changed. Existing Discord permission: Blackbot can read `#tradingai-private`; the new BlackBot conversational allowlist does not include that room, but this is not removal of Discord-level access. No live-bank, broker, paper-order, market-data or backtest integration was exercised by this setup. Private channels' reply flows, DMs and tool-heavy tasks remain untested.

## Recovery and backups
Before changes, `config.yaml`, `.env` where present, and SOUL files were copied to each target profile's `backups/before-discord-20261113-115737/`. Keep backups private because `.env` can contain credentials.

For future failures: check the shared `gateway_state.json` and each profile's `logs/gateway.log`/`logs/errors.log`; a connected Discord transport can still have a broken model credential scope. Do not publish logs without redaction. A successful webhook or REST identity request is not proof of a working model response.
