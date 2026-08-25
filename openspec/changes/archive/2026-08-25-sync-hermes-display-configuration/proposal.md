# Proposal: Sync Hermes Display Configuration

## Why

The existing `hermes-display-configuration` spec describes a former low-noise profile that no longer matches reality. Four categories of staleness:

1. **Stale value assertions** — `interim_assistant_messages: false`, `turn_summary: false`, `tool_preview_length: 60`, `tool_progress: all`, `busy_ack_detail: absent`, `Slack reasoning: false` — all contradicted by the validated live config.
2. **Missing coverage** — `tool_progress_grouping`, `spinner_token_flow`, `show_commentary`, `cleanup_progress`, `long_running_notifications`, `live_status`, `runtime_footer.fields` (latency) are not in the spec.
3. **Platform-provenance omission** — Telegram/Discord/Slack have explicit overrides; Feishu/Matrix/WhatsApp inherit from global block. Spec does not distinguish.
4. **Known key behaviors not documented** — `tool_preview_length: 0` means unlimited (not disabled); `reasoning_full` is source-recognized but absent from official docs; `tool_progress: log` is gateway-only and exclusive.

## What Changes

### Modified: `hermes-display-configuration`

Reconciles the canonical spec to match the validated v0.20.5 live configuration. All corrections are based on: official docs (`/docs/user-guide/configuration`), installed source (`cli-config.yaml.example`, `gateway/display_config.py`, `DEFAULT_CONFIG`), and resolved live config (`hermes config get display`).

### Local validation evidence

A validation document capturing the evidence trail is committed alongside the spec change.

## Scope

- Config-only reconciliation — no Hermes source code modifications
- No live config mutation — the live config is already at maximum visibility
- OpenSpec spec + Hermes skill reference only

## Evidence

- Hermes Agent v0.20.5 (2026.8.19), installed via git
- Config version 38, `hermes config check` passes
- Resolved via `hermes config get display` and `hermes config get streaming`
- Source cross-verified against `cli-config.yaml.example`, `gateway/display_config.py`, `agent/display.py`, `gateway/runtime_footer.py`
- Official docs cross-verified at `/docs/user-guide/configuration`
