# Design: Sync Hermes Display Configuration

## Evidence hierarchy

All corrections in this change are grounded in a five-layer evidence hierarchy. No layer alone is sufficient; the reconciled spec reflects the intersection of all five.

1. **Official documentation** (`/docs/user-guide/configuration`) — canonical key names, accepted values, documented defaults, platform limitations. Keys absent from official docs are flagged as source-recognized.
2. **Installed v0.20.5 source** (`cli-config.yaml.example`, `DEFAULT_CONFIG`, `gateway/display_config.py`, `agent/display.py`, `gateway/runtime_footer.py`) — actual runtime behavior, default values, per-platform built-in tiers, normalization logic, footer field registry.
3. **Raw YAML** (`~/.hermes/config.yaml`) — explicit user-set values.
4. **Resolved config** (`hermes config get display`) — values after DEFAULT_CONFIG merge and normalization.
5. **Effective per-platform resolution** — platform override > global > built-in platform default > global default, applied in order.

## What changed and why

### Requirement: Reasoning-visible display profile

- `interim_assistant_messages`: `false` → `true` — raw YAML line 843, confirmed by resolved config
- `turn_summary`: `false` → `true` — raw YAML line 846, confirmed by resolved config
- `tool_preview_length`: `60` → `0` — raw YAML line 845, confirmed by resolved config; source confirms `0` = unlimited
- Added `show_commentary: true`, `spinner_token_flow: true` — not in old spec but present in raw YAML and resolved config
- Removed `reasoning_style` from this requirement's assertion list — it is inherited (not explicitly set at top level) and belongs in the per-platform requirement

### Requirement: Operational visibility preservation

- `tool_progress`: `all` → `verbose` — raw YAML line 894, confirmed by resolved config
- Added `tool_progress_grouping: separate`, `live_status: full`, `busy_ack_detail: true` — all in raw YAML and resolved config
- Added `runtime_footer.fields` containing `latency` — raw YAML lines 887-891

### Requirement: Unsupported key exclusion

- Removed `display.busy_ack_detail absent` prohibition — `busy_ack_detail: true` is now explicitly set in raw YAML line 898 and confirmed in resolved config
- Preserved `agent.verbose` absence
- Added scenario documenting `busy_ack_detail absent` as legacy-compatibility case
- Added scenario documenting `busy_ack_detail: true` in full-detail profile

### Requirement: Reasoning display is presentation-only

- Strengthened: added messages array, tool schemas to the "SHALL NOT alter" list
- Softened "identical output" to parameter-level assertion (stochastic models cannot guarantee identical output)

### Requirement: Per-platform reasoning override

- Slack: `false` → `true` — raw YAML line 849 shows `slack.show_reasoning: true`
- Preserved original suppression scenario for validator compatibility
- Added enabled scenario reflecting validated profile

### ADDED: Gateway streaming is distinct from CLI streaming

- `display.streaming` (CLI-only) vs top-level `streaming.enabled` (gateway) are separate paths — both are `true` in the live config
- Documented in official docs as distinct; source confirms `display_config.py` skips `streaming` from global resolution

### ADDED: Tool-progress modes and preview length

- `log` mode is gateway-only and exclusive — source confirms `log_mode_enabled` guard in `run.py`
- `tool_preview_length: 0` = unlimited — source confirms in `agent/display.py` `_tool_preview_max_len: 0`

### ADDED: Runtime footer fields

- Exactly four fields: `model`, `context_pct`, `cwd`, `latency` — source confirms `_DEFAULT_FIELDS` and `format_runtime_footer` in `runtime_footer.py`
- Unknown fields silently ignored — source confirms loop with `# Unknown field names are silently ignored`

### ADDED: Deprecated tool_progress_overrides exclusion

- `display.tool_progress_overrides` is deprecated per official docs — migrated to `display.platforms` on first load
- Source confirms backward-compat read in `display_config.py:221-227`

### ADDED: Explicit platform verbosity and provenance

- Telegram/Discord/Slack: explicit overrides in raw YAML lines 848-878
- Feishu/Matrix/WhatsApp: only `streaming: true` set; other 8 keys inherit from global block
- Built-in `_TIER_MEDIUM` defaults (tool_progress: new) are shadowed by global verbose inheritance

### ADDED: reasoning_full is source-recognized

- Absent from official documentation — confirmed by delegate 1 (zero occurrences in full docs aggregate)
- Present in `DEFAULT_CONFIG["display"]` and resolves correctly via `hermes config get`
- `hermes config set display.reasoning_full true` may produce unknown-key notice — this is expected, not an error

## Scope boundary

This change is documentation and specification only. No live config mutation, no Hermes source code modification, no adapter implementation changes. Adapter edit support is validated as evidence, not enforced as a requirement.
