# Proposal: Configure OmniRoute `sh/*` Models Across Supported Agent CLIs

## Why

OmniRoute currently exposes a live `sh/*` model namespace, while several installed coding-agent CLIs still use older, provider-specific, or unclassified model routes. This creates inconsistent routing, makes the shared `OMNIROUTE_API_KEY` source harder to audit, and can cause a CLI to reject an otherwise valid OmniRoute model before making a request.

The earlier `standardize-zshenv-shared-secrets` change established the shared credential source and wrapper model. Kilo has since been configured and verified as a baseline. Prime Agent is owned by the separate change `add-omniroute-prime-agent-provider` (metadata-only at planning time) and is pending reconciliation; this change does not mutate it. This change extends the work to other CLIs only after each CLI's official provider mechanism and protocol compatibility are confirmed.

## Scope

This change SHALL:

- classify every installed coding-agent CLI as supported, wrapper/profile-only, unconfigured, unsupported, or alias;
- configure only CLIs with an official OmniRoute-compatible mechanism;
- use OmniRoute's `http://localhost:20128/v1` endpoint and `OMNIROUTE_API_KEY` without storing literal credentials;
- use live `sh/*` inference model IDs rather than retired `dlg/*` inference routes;
- preserve existing non-OmniRoute providers and defaults unless separately approved;
- verify every changed CLI with a real isolated read-only sentinel call;
- back up and atomically replace each changed configuration file with rollback evidence.

This change SHALL NOT:

- reconfigure the already-applied Kilo baseline;
- mutate the separate Prime Agent change or its configuration without reconciliation;
- force configuration into unsupported or unconfigured CLIs;
- change a CLI's default model implicitly;
- modify application/framework source code;
- rotate provider credentials (provider-side rotation remains a separate user action).

## Initial role policy

Registration is distinct from default selection. Unless the user approves a per-CLI default change, the initial policy is:

```text
primary coding: sh/codex
small/default:  sh/default
Claude-compatible profile: sh/Claude-Fable
reasoning:      sh/o3
fallback:       sh/codex
```

A CLI may expose additional `sh/*` models only when its native catalog and protocol support are verified. The role policy does not authorize changing existing defaults.

## Support matrix baseline

| CLI | Baseline | Initial classification | Apply policy |
|---|---|---|---|
| Kilo | real default `sh/codex` passes | already configured | verify only; no mutation |
| Prime Agent | separate OmniRoute change/baseline | overlapping separate change | reconcile; no mutation here |
| Codex | installed; explicit real call verified | supported candidate | inspect official `model_providers`/Responses mechanism |
| OpenCode | installed; real call verified | supported candidate | inspect native provider model schema |
| Pi | installed; real call verified | supported candidate | inspect native models/provider schema |
| Droid | real call passes through exact custom model | supported candidate | use official BYOK `${VAR}` mechanism; preserve model IDs |
| Goose | real call verified | provider-dependent candidate | inspect provider configuration and protocol |
| Cline | real call verified | provider/profile candidate | inspect official provider configuration |
| AGY | real call verified | unclassified | classify before mutation |
| Qoder | real call verified | unclassified | classify before mutation |
| Claude Code | works via provider adapter | protocol-dependent | do not assume direct OpenAI-compatible `sh/*` support |
| Copilot | explicit model call works; default catalog issue observed | provider-dependent | classify; do not force arbitrary endpoint |
| Cursor Agent | installed but unconfigured | unconfigured | no mutation; requires user login/key |
| Auggie | installed but unconfigured | unconfigured | no mutation; requires user login/key |
| aliases | several binaries resolve to same executable | alias | deduplicate verification |

## Capabilities

### New Capabilities

- OmniRoute `sh/*` model registration across supported coding-agent CLI configuration surfaces.
- Cross-CLI support classification and evidence contract.

### Modified Capabilities

- `coding-cli-provider-registry`: adds OmniRoute `sh/*` registration requirements for the consumer CLIs this change mutates or verifies (goose, opencode, droid, grok, grok, codex), including retired `dlg/*` removal and credential indirection. The new `omniroute-agent-cli-routing` capability carries the cross-CLI process contract (classification, backup, sentinel, rollback) and surfaces outside the nine-CLI registry.

## Impact

- User-level configuration files may change one at a time during apply.
- `OMNIROUTE_API_KEY` remains the sole shared OmniRoute credential source.
- Existing providers remain available.
- Unsupported/unconfigured CLIs remain unchanged and are documented as such.
- Each changed file receives a mode-600 backup and an atomic rollback path.
- Unrelated OpenSpec work in the store remains untouched.

## Matrix authority

The evidence-backed support matrix in design.md (captured 2026-08-28 from read-only, redacted inspections) supersedes the initial classification table above. Where the two differ, design.md governs the apply set.

## Approval gate

Approved and applied 2026-08-28. The user explicitly requested registration of
`sh/gpt-5.6-sol` and `sh/Claude-Fable` where not yet available; no default-model
changes were approved. Applied set: pi, goose, kimi (omp already registered —
verified only). opencode, droid, cline, prime-agent, grok left unchanged.
Outcome and blockers recorded in tasks.md and EVIDENCE_MANIFEST.md.
