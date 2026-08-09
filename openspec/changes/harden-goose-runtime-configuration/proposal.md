# Proposal: Harden Goose Runtime Configuration

## Why

The current goose v1.45.0 setup is functional but over-broad and drift-prone. Evidence gathered on 2026-08-09 proves offline documentation and three providers work, while Omniroute is configured but unavailable. MCP Router is healthy at the protocol boundary and works from goose, but goose startup has also failed intermittently. The default profile enables 17 extensions, uses a mutable MCP package selector, and incurs high token cost for simple work.

A follow-up hardening change is needed to make the configuration least-privilege, reproducible, cost-aware, and accurately documented without changing live settings before review.

## What Changes

1. Establish a durable provider health matrix and remove stale all-provider-healthy claims.
2. Classify MCP Router as healthy transport with intermittent goose initialization; pin the reviewed CLI version only after approval.
3. Define and verify least-privilege invocation profiles for chat/docs, coding, and MCP-dependent work.
4. Harden offline-doc updates with explicit tag fetch, `npm ci`, staging validation, deletion-aware deployment, and rollback.
5. Tighten config and deployment permissions after checking app compatibility.
6. Add deterministic runtime probes that validate expected output and artifacts, not only exit code or `metadata.status`.
7. Reconcile goose skills and verification references with retained evidence.

## Non-Goals

- No provider credential changes in the planning phase.
- No live extension enable/disable mutation before approval.
- No network listener exposure changes.
- No rewriting historical archive evidence; this change supersedes stale claims transparently.

## Compatibility and Rollback

All future mutations SHALL be separately gated. Preserve a timestamped redacted config backup and the prior `/opt/goose-docs` tree before any cutover. Rollback restores the prior config and docs directory, then reruns provider, MCP, and offline-doc probes.
