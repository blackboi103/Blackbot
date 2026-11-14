# Qwen context — measured configuration

Verified 2026-11-12. Local endpoint `http://localhost:11434/v1`, model `qwen3.5:9b` (Q4_K_M).

- Persisted model parameter: `num_ctx 262144`.
- Unload/reload without a per-request num_ctx override: `/api/ps` returned **262,144**, with size and size_vram both **14,326,295,428 bytes**.
- Real request through the same OpenAI-compatible endpoint used by Hermes: **77,149 prompt tokens**, **268 completion tokens**, all three exact start/middle/end codes recovered, `finish_reason=stop`; about **79.94 seconds** uncached.
- This proves the larger allocation and one >64K retrieval case. It is not a reliable-reasoning guarantee for all 262K tokens or a full Hermes compaction/tool-loop certification.
- Hermes context was **not lowered**. Its existing cached advertised size was already 262,144.
- Rollback model tag: `qwen3.5:9b-before-262k-20261112`. No weights were redownloaded. Original model configuration is also in the durable migration backup.

Evidence files: `C:/Users/Kyle Adolphe/AppData/Local/hermes/profiles/robo/reports/qwen-262k/persisted-and-over64k-test.json` and `Qwen-262k.Modelfile`.

For a new local-Qwen conversation, select that model and keep a short sourced project packet. Longer windows increase memory demand and uncached prompt latency. Keep room for reasoning and output; model capacity is not permanent memory. [[System/RETRIEVAL]].

Native `/api/chat` honored `think:false` in a short probe, but the OpenAI-compatible endpoint did not honor earlier ad-hoc thinking-off hints. No default thinking/template change was made.

Source: [[Sessions/2026-11-12 - Vault Retrieval Setup]].
