# Design: reconcile-llm-spec-authorities

## Context

See proposal.md — Why. Four spec-text accuracy bugs were identified by cross-reading
the six canonical LLM specs and then validated against live code in `tdt-core` and
`agent-core`. In every case the code is correct and the spec text lags. This change
is spec-text-only; no code changes.

## Goals / Non-Goals

**Goals:**
- Make the four canonical spec texts match the implemented behavior exactly.
- Establish the authority boundary between the two Claude Code provider specs.

**Non-Goals:**
- Changing any code, enum, or runtime behavior.
- Resolving the deeper effort-enum design question (one canonical enum vs
  per-provider projection) — that is a separate contract decision.
- Adding omp/prime-agent/adapter to the CLI boundary spec exclusion list —
  tracked separately.

## Decisions

### D1: Fix spec text, not code

All four findings are documentation bugs. The code enums, validators, and registry
are correct and tested. Rewriting code to match stale spec text would regress
working behavior. Alternative considered: treat the master spec's 2-value protocol
enum as authoritative and remove `openai_chat` from code — rejected because
`openai_chat` is wired and tested in `agent_core/_ai/models.py`.

### D2: Correct the registry claim rather than delete the registry spec

The master spec Purpose claims the registry was "replaced". Validation showed the
registry is still active (18 entries, loaded at import, used by
`credential_entry()`/`resolve_agent_profile()`). The accurate statement is that
`auth_env`+canonical schema replaced the `api_key_env` YAML field, while the
registry persists as the credential-metadata authority. Alternative considered:
delete `register-custom-provider-credentials` spec as obsolete — rejected because
its described subsystem is live.

### D3: Document the two-layer effort design as-is

The canonical schema accepts the union vocabulary; agent-core applies
provider-specific sets at construction. This is the implemented behavior and is
sound (schema permissiveness + construction strictness). The delta documents it
rather than collapsing it into a single enum. Alternative considered: a single
canonical enum enforced at schema time — rejected as a behavior change out of scope.

### D4: Split Claude Code authority by surface, with --settings as the selection mechanism

The two Claude Code specs are reconciled by assigning each a distinct surface:
`claude-code-provider-routing` owns the launcher functions, and
`claude-code-provider-profile-resolution` owns the persistent settings/profile files.
Verified against the live `~/.zshrc` launchers: each launcher invokes
`claude --settings <profile.json> --model <alias>` inside a subshell that unsets
`ANTHROPIC_AUTH_TOKEN` and exports only `ANTHROPIC_BASE_URL` — model selection is
carried by the `--settings` profile and the `--model` flag, NOT by subshell
`ANTHROPIC_MODEL` env vars (the archived `claude-code-provider-profile-resolution`
change documented that subshell env vars do not take precedence over settings.json).
The precedence rule is therefore: explicit `--model` flag > `--settings` profile >
global `~/.claude/settings.json`. Alternative considered: merge the two specs —
rejected to keep the delta minimal and avoid a large spec rewrite.

### D5: Correct the credential spec's field name and mechanism, keep the registry requirement

The `register-custom-provider-credentials` spec's registry entries are correct and
live (18 entries, sealed, loaded at import). Only its scenarios are stale: they name
the retired `api_key_env` field and a `credential_entry()` resolution path with zero
callers. Verified: `resolve_agent_profile()` builds `CredentialAvailability` from
`provider.auth_env` (agent_profile.py:788), and runtime validation happens in
`CredentialResolver.resolve()` over provider-bound route references. Alternative
considered: delete the spec as obsolete — rejected because the registration
requirement (entries with secret classification and provider binding) is still true
and enforced by the registry contents.

## Risks / Trade-offs

- [Spec text drifts again if code changes] → Each delta scenario is testable;
  future code changes to these enums/fields should update the spec in the same change.
- [Purpose edit is a direct main-spec edit, not a delta] → The registry-claim fix and
  the TBD Purpose fix touch `## Purpose` sections, which deltas cannot modify. These
  two edits are applied directly to `openspec/specs/<capability>/spec.md` during apply.

## Migration Plan

No migration — spec-text-only. Rollback = revert the spec edits.

## Open Questions

None.
