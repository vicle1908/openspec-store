# ECC Harness Alignment — Proposal

## Why

The TDT ecosystem runs Claude Code with `ecc@everything-claude-code` v2.0.0 alongside a 103-skill TDT overlay. ECC ships a broad surface — 262 skills, 84 commands, 64 agents, 30+ hooks, 22 rule dirs — most of which is **load-bearing for nobody** in our setup. The disposition of each entry is currently implicit; only ~15 hooks have been explicitly disabled via the `ECC_DISABLED_HOOKS` env var in `~/.claude/settings.json`. ECC ships monthly (`1.10.0` → `2.0.0` → `Unreleased` already in CHANGELOG.md), and `extraKnownMarketplaces.everything-claude-code.autoUpdate: true` means we can wake up to a new surface area overnight with no review.

The result: silent noise in our session (broad-match hooks firing on every Edit), an open question every time we read a new skill ("do we use this?"), and no repeatable procedure for handling the next release.

## What Changes

- **Add 7 new specs** (38 requirements, 39 scenarios) under `openspec/specs/` codifying the disposition criteria for each ECC surface (skills, commands, agents, hooks, rules dirs)
- **Codify the audit methodology** as a release-audit playbook at `tdt-meta/docs/ecc-harness/playbook.md`
- **Update `~/.claude/settings.json`**:
  - Set `env.ECC_DISABLED_HOOKS` to the canonical 15-hook disabled string
  - Set `extraKnownMarketplaces.everything-claude-code.autoUpdate: false` (pin v2.0.0 with quarterly review)
- **Generate static disposition tables** in `openspec/changes/archive/2026-06-27-ecc-harness-alignment/audit/` (one per surface)
- **Cross-link** the new ECC section from `tdt-meta/AGENTS.md`

## Problem

The TDT ecosystem runs Claude Code with `ecc@everything-claude-code` v2.0.0 alongside a 103-skill TDT overlay. ECC ships a broad surface — 262 skills, 84 commands, 64 agents, 30+ hooks, 22 rule dirs — most of which is **load-bearing for nobody** in our setup. The disposition of each entry is currently implicit; only ~15 hooks have been explicitly disabled via the `ECC_DISABLED_HOOKS` env var in `~/.claude/settings.json`. ECC ships monthly (`1.10.0` → `2.0.0` → `Unreleased` already in CHANGELOG.md), and `extraKnownMarketplaces.everything-claude-code.autoUpdate: true` means we can wake up to a new surface area overnight with no review.

The result: silent noise in our session (broad-match hooks firing on every Edit), an open question every time we read a new skill ("do we use this?"), and no repeatable procedure for handling the next release.

## Change

Produce a curated disposition for every entry in the ECC v2.0.0 surface, codified as a single OpenSpec change with seven RFC 2119 specs. Codify the methodology as a **release-audit playbook** that runs on every future ECC release without requiring another design brainstorm. Update `~/.claude/settings.json` `ECC_DISABLED_HOOKS` to the canonical value and decide the marketplace pin policy.

## Scope

In scope: skills, commands, agents, hooks, rules dirs, marketplace pin policy — full harness audit (per user choice).

Out of scope: TDT overlay edits, our own hooks (agentmemory/gitnexus/ccg), new TDT-side services, mass uninstall of ECC, ECC's `ecc2/` alpha control plane, cross-harness manifests.

## Non-goals

- No changes to TDT skills themselves. TDT overlay is treated as read-only input.
- No replacement of our own hooks. The policy only governs when *both* an ECC hook and our hook fire.
- No new TDT-side scripts or services. Audit produces static artifacts (markdown tables + shell snippets).
- No commits inside `~/.claude/plugins/cache/...`. All output lives in `tdt-meta/`.
- No mass uninstall of the ECC plugin. Even disabled hooks stay installed.

## Success criteria

1. All 262 skills, 84 commands, 64 agents, 30+ hooks, 22 rule dirs have a final classification.
2. `~/.claude/settings.json` `ECC_DISABLED_HOOKS` matches the canonical value in `specs/hooks-policy/spec.md`.
3. The playbook (`tdt-meta/docs/ecc-harness/playbook.md`) can be re-run by another agent on the next ECC release without additional design work.
4. `/opsx:verify` passes; change archives cleanly.
5. Cross-references in `tdt-meta/.agents/skills/SKILLS_INDEX.md` for any TDT-skill that replaced an ECC-skill are updated.
6. Marketplace pin/unpin decision recorded in `audit/marketplace-baseline.txt` and reflected in `~/.claude/settings.json`.

## Design

See `design.md` for the full methodology (4 phases) and `docs/superpowers/specs/2026-06-27-ecc-harness-alignment-design.md` for the brainstorming-session design spec.

## Repos touched

- `tdt-meta/` — primary owner of the change artifacts and the playbook.
- `~/.claude/settings.json` — single line edit for `ECC_DISABLED_HOOKS`; possible `extraKnownMarketplaces.everything-claude-code.autoUpdate` flip.
- No source code changes in any other repo.

## Integration with TDT patterns

- Uses `tdt_core.env.load_tdt_env()` if any helper script is added (currently no script — audit is mostly reading).
- Follows OpenSpec v1.4.1 conventions: kebab-case name, `proposal.md` + `design.md` + `specs/` + `tasks.md`, RFC 2119 requirements.
- The 73 prior OpenSpec changes and 22 existing specs serve as templates; this change is consistent in shape with `agent-core-builtin-toolkit` (which produced `specs/builtin-hooks`) and `agent-core-integration-contract`.

## Deployment

- No Docker or launchd changes.
- No DBOS scheduled workflow changes.
- Only settings.json edit; the change can be applied in a single 5-minute window after the audit completes.
- Rollback: restore the prior `ECC_DISABLED_HOOKS` from `~/.claude/settings.json.bak` (auto-created by the update step).

## Timeline

~12 hours of focused work, fits comfortably in 2 sessions. Most chunks are reading + classification; the only writes are §6.1, §6.2, §8.1.

## Open questions (from design §10)

1. Should ECC's `continuous-learning` / `continuous-learning-v2` skills be `keep-default` or `redundant-to-tdt-skill:agentmemory`?
2. Should `healthcare-reviewer` agent be enabled by default for our clinical mobile app, or `keep-optional`?
3. Pinning policy: pin v2.0.0 forever vs pin with quarterly review?
4. Adopt ECC's `hookify-rules` skill given we have `hookify@claude-plugins-official` already?

These were resolved during §4 (Adoption decisions) of the implementation plan. See `audit/adoption.md` for the final answers:

1. `continuous-learning-v2` → `redundant-to-tdt-skill:agentmemory`
2. `healthcare-reviewer` → `keep-optional` (for poems-mobile3-ios/android)
3. Pinning policy → Pin v2.0.0 with quarterly review (next: 2026-09-27)
4. `hookify-rules` → `redundant-to-tdt-skill` (we have `hookify@claude-plugins-official` CLI)

---

## How to Run the Next Audit

When a new ECC release ships (or quarterly, whichever comes first):

1. Read the playbook: `tdt-meta/docs/ecc-harness/playbook.md`
2. Update the marketplace baseline: `audit/marketplace-baseline.txt` (capture new SHA)
3. Run Phase 1–7 of the playbook end-to-end
4. Update `Last updated` and `Last audited ECC version` in the playbook header
5. Add an entry to the playbook's **Audit Log** section
6. Run `/opsx:propose` to start a new change with name `ecc-harness-alignment-<version>` (or similar)
7. Commit all changes to `tdt-meta/`

The playbook is self-contained. **No additional design work is needed for routine ECC releases.** If the change surface is significantly different (e.g., new categories, new hook types), update the playbook itself as part of the audit.

## Final Outcomes (2026-06-27 audit)

- **Skills classified (262 total)**: 48 keep-optional, 4 redundant-to-tdt-skill, 134 disabled-default:no-evidence, 44 disabled-default:stack-irrelevant, 32 disabled-default:domain-irrelevant
- **Commands classified (84 total)**: 4 redundant-to-tdt-skill, 80 keep-optional
- **Agents classified (64 total)**: 50 keep-default, 4 keep-optional, 8 disabled-default:domain-irrelevant, 2 disabled-default:stack-irrelevant
- **Hooks (18 total)**: 15 disabled-default, 2 coexist, 1 keep-default
- **Rules dirs (19 total)**: 5 surface (python, swift, kotlin, typescript, react), 1 surface:common, 13 disabled-default:stack-irrelevant
- **Settings changed**: `ECC_DISABLED_HOOKS` updated (15 hooks), `autoUpdate: false`
- **Version-pin decision**: Pin v2.0.0 with quarterly review (next audit due: 2026-09-27)