# jira-ticket-intelligence

**Status:** Sections 1-4 Complete | Section 5 Complete  
**Version:** 1.0.0 (shipped canonical contract) + additive Section 5 analyzer/CLI pipeline on the current v1 surface  
**Date:** 2026-06-07

## Overview

Shared ticket intelligence bundle contract for analyzing Jira issues across TDT ecosystem tools.

**Normative source of truth for the shipped canonical contract:** `../../specs/ticket-intelligence-core/spec.md`

This change directory exists to hold:

- rollout and implementation history for the shipped v1 canonical bundle
- SDK-first extension history for RCA, fix-status, filter collection, Sheets output, and analyzer-level additive RCA/fix-status bundle outputs

## Quick Links

| Document | Path |
| -------- | ---- |
| Permanent spec | [../../specs/ticket-intelligence-core/spec.md](../../specs/ticket-intelligence-core/spec.md) |
| Proposal | [proposal.md](proposal.md) |
| Design | [design.md](design.md) |
| Tasks | [tasks.md](tasks.md) |
| Bundle | [../../../jira-skill/docs/bundle-contract.md](../../../jira-skill/docs/bundle-contract.md) |
| Skill | [../../../tdt-meta/.agents/skills/jira-ticket-intelligence/SKILL.md](../../../tdt-meta/.agents/skills/jira-ticket-intelligence/SKILL.md) |

## How to Use This Spec Set

- Read the permanent spec first for shipped behavior.
- Read `tasks.md` Section 5 for SDK-first migration work.
- Use `design.md` for migration rationale, trade-offs, and extension context.
- Treat this README as navigation, not as a second normative contract.

## Implementation Status

The canonical v1 contract and its SDK-first analyzer/CLI extensions are implemented.

This change package should be read as historical rollout context plus execution notes, while
`../../specs/ticket-intelligence-core/spec.md` remains the authoritative contract for shipped
behavior.

## Execution Starting Point

If implementation follow-up begins now, start with **verification/polish work** from the completed Section 5 surface:

- keep secondary docs/skills aligned with the current analyzer contract
- tighten `SheetsWriter` field expectations against the canonical bundle shape
- expand tests only for behavior the current analyzer/bundle path actually emits
- avoid inventing a parallel post-v1 contract unless a truly breaking change is intended

The analyzer-level RCA/FixStatus bundle expansion is already implemented. Follow-up work should focus on verification, fixture/doc consistency, and any intentionally additive refinements rather than treating those fields as future work.

## Test Summary

Verification should be taken from the current repo-level test runs and the permanent spec,
not from frozen totals in this navigation README.

## Architecture

- **Deterministic:** same snapshot → same bundle (fixture-testable)
- **Versioned:** semantic versioning with backward compatibility
- **Consumer-agnostic:** portable signals in bundle, local policy in adapters
- **Canonical shared layer:** `jira-skill` owns the bundle contract and snapshot analysis
