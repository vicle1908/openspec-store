# Proposal: Cline OmniRoute provider cleanup and route correction

## Why

Cline 3.0.61 retained three provider IDs that were absent from its `models.json` registry and failed explicit resolution with `Unknown or disabled provider`. Its only retained OmniRoute entry, `openai-compatible`, also still had model `sh/codex`, while the source-derived Cline route contract requires `sh/gpt-5.6-sol`. Cleanup4 therefore removes the three stale entries, updates the retained provider’s model to `sh/gpt-5.6-sol`, and repairs `lastUsedProvider` only when it points to a removed stale entry.

A prior archived Cline candidate proves the target provider/model pair in isolation. Cleanup4-specific live sentinel and per-ID negative-control evidence remain open and must be recorded before closure.

## What Changes

- Remove exactly the three stale, unregistered Cline provider entries from `~/.cline/data/settings/providers.json`.
- Retain the working `openai-compatible` provider and update its model from `sh/codex` to the canonical source-derived model `sh/gpt-5.6-sol`.
- Preserve all unrelated settings and `baseUrl http://localhost:20128`.
- Repair `lastUsedProvider` from `openai-omniroute-chat` to `openai-compatible`.
- Record cleanup4-specific backup identity, pre/post modes and hashes, the static 17/17 candidate route-contract result, and the still-pending live sentinel/negative-control gates.
- Add requirements that custom Cline provider IDs must be registry-backed and that the retained OmniRoute provider must use the source-derived canonical model before closure.

## Impact

This is a corrective Cline configuration change. It does not change the OmniRoute server, Cline source, credentials, or unrelated providers. Cleanup4-specific live verification and archive remain blocked pending a positive sentinel, per-ID negative controls, and resolution of the disclosed-credential incident.

## Non-Goals

- Do not add a Cline PM provider without a separately proven native route.
- Do not rotate, print, or copy credential values into Git.
- Do not edit archived OpenSpec artifacts.
