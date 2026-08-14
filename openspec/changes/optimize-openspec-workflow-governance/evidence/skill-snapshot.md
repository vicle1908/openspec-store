# Skill snapshot (non-authoritative, local only)

**Date:** 2026-08-13
**OpenSpec:** 1.8.0
**Purpose:** Planning evidence only. This file is not a skill source, manifest, or runtime configuration.

## Hermes-native custom skills

Custom workflow and review skills remain under `~/.hermes/skills/` and are managed by Hermes Agent. The OpenSpec store does not own or install these skills.

| Skill group | Relative path | Files | Approx. size |
|---|---|---:|---:|
| openspec-workflow | `.hermes/skills/software-development/openspec-workflow` | 144 | 829 KB |
| openspec-code-review | `.hermes/skills/openspec-workflow/openspec-code-review` | 3 | 13 KB |
| openspec-plan-review | `.hermes/skills/openspec-workflow/openspec-plan-review` | 3 | 12 KB |
| openspec-review-governance | `.hermes/skills/openspec-workflow/openspec-review-governance` | 11 | 66 KB |

## Store-local adapter surface

The `openspec-store` repository tracks 29 entries under `.hermes/skills/`. They are not assumed to be custom-skill authority. Phase 1 Task 1.4 must classify them as generated OPSX adapters, intentional workspace integrations, stale copies, or unknown before any cleanup is proposed.

**No live skill, Hermes config, or repository-local adapter was moved or deleted during planning.**
