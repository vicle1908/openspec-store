## Why

A post-change consistency audit of the live Hermes MoA profile, canonical OpenSpec contract, maintained governance runbook, and Hermes skill references found the active topology aligned, but found one stale maintained reference: `references/hermes-moa-configuration.md` still instructed operators to put `context_length: 1000000` inside every MoA reference and aggregator slot. The live contract and canonical spec intentionally keep context ownership at `providers.<name>.context_length` and do not duplicate it in MoA slots.

The audit also verified that the current default, deep, and fast aggregators, reasoning efforts, references, tuning values, provider defaults, fallback order, privacy setting, and one-million-token provider contexts are aligned. No canonical spec delta is required; this is a maintained-documentation correction and verification record.

## What Changes

- Correct the maintained OpenSpec MoA reference so its example, tuning table, and pitfall guidance place context ownership at provider/model configuration rather than MoA slots.
- Clarify that leaf setters are the normal configuration path and any atomic YAML replacement is an agent-only recovery path after a verified backup and shape check, avoiding conflict with Hermes' user-facing no-hand-edit rule.
- Preserve the already-aligned canonical MoA specification and governance runbook without rewriting archived historical changes.
- Record sanitized live configuration, provider health, structural validation, stale-reference classification, and commit/remote evidence.

## Scope

Owned maintained surface:

- `/Users/androidteam/.hermes/skills/software-development/openspec-workflow/references/hermes-moa-configuration.md`

Reviewed, unchanged surfaces:

- `/Users/androidteam/Developer/openspec-store/openspec/specs/hermes-moa-configuration/spec.md`
- `/Users/androidteam/Developer/openspec-store/docs/governance/hermes-moa-configuration.md`
- `/Users/androidteam/.hermes/skills/autonomous-ai-agents/hermes-agent/references/configuration.md`
- `/Users/androidteam/.hermes/skills/autonomous-ai-agents/hermes-agent/references/providers-and-models.md`

Historical archived changes remain immutable and are classified as historical evidence.

## Non-Goals

- Do not change live `~/.hermes/config.yaml`; its current topology already matches the canonical contract.
- Do not modify Hermes source, providers, credentials, cron jobs, or fallback configuration.
- Do not rewrite archived changes merely because they describe superseded topology.
- Do not stage or modify unrelated active OpenSpec changes or untracked directories.
