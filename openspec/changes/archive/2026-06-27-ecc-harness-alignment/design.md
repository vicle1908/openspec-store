# ECC Harness Alignment — Design

This file mirrors the brainstorming design spec at `docs/superpowers/specs/2026-06-27-ecc-harness-alignment-design.md`. The doc there is the durable artifact; this mirror keeps OpenSpec self-contained for reviewers who only read the change dir.

## Why one change, not five

The policy is unified: TDT overlay takes precedence; ECC is a substrate we curate. Splitting into per-surface changes would multiply governance overhead without adding decision fidelity. The single change carries seven specs — each has RFC 2119 requirements and can be reviewed independently.

## Methodology — the audit playbook (4 phases)

### Phase 1 — Static manifest diff (every release)

For each surface, walk every entry and apply the classification rubric. Output goes to `audit/<surface>-disposition.md`.

**Skill classification (4 questions in order):**

1. Does TDT have an equivalent? → `redundant-to-tdt-skill:<name>`
2. Language/framework we don't run? → `disabled-default:stack-irrelevant`
3. Load-bearing for ECC-internal flow? → `keep-optional`
4. Otherwise → `investigate` (queue for Phase 2)

**Command classification:** Same four questions. Trigger-point commands (`/docs`, `/plan`, `/tdd`, `/code-review`, `/build-fix`, `/e2e`, `/verify`, `/multi-plan`, `/orchestrate`, `/harness-audit`) get extra scrutiny. If a TDT/OpenSpec workflow covers the trigger → `redundant-to-tdt-workflow`.

**Agent classification (3 buckets):**
- Domain reviewers: keep only matching repos (`python-reviewer` for backend; `swift-reviewer`/`kotlin-reviewer` for mobile).
- Generic specialists: keep all (`code-reviewer`, `code-architect`, `planner`, `security-reviewer`, `build-error-resolver`, `performance-optimizer`, `silent-failure-hunter`, `comment-analyzer`, `e2e-runner`, `tdd-guide`, `code-simplifier`).
- Cross-domain/alpha: keep only domain-relevant (`healthcare-reviewer` for clinical mobile app). Discard `network-*`, `homelab-*`, `gan-*` unless we adopt them.

**Hook classification (3 outcomes):**
- `disabled-default` — broad-matchers and overlays with our hooks.
- `keep-default` — only `Stop evaluate-session` if it feeds continuous-learning loop.
- `coexist` — hooks that don't overlap with agentmemory/gitnexus/ccg.

**Rules classification:** Surface only `python`, `typescript`, `swift`, `kotlin` for current repos. Discard `cpp`, `csharp`, `dart`, `fsharp`, `golang`, `java`, `perl`, `php`, `react`, `ruby`, `rust`, `web`, `arkts`, `angular`. Surface `common/` if globally useful.

### Phase 2 — Targeted usage evidence

For every `investigate` entry and every entry in the **new-since-last-audit** diff (marketplace clone SHA vs `audit/marketplace-baseline.txt`):

- Query `~/.claude/projects/` session JSONL (authoritative).
- Query `~/.claude/cost-tracker.log` (caveat: token usage only, may not reflect skill/command invocations).
- 0 hits + non-trivial description → `keep-optional`.
- 0 hits + generic/redundant description → `disabled-default:no-evidence`.

New v2.0 features with no usage data → 2-day worktree trial.

### Phase 3 — Output

```
tdt-meta/openspec/changes/ecc-harness-alignment/audit/
├── skills-disposition.md
├── commands-disposition.md
├── agents-disposition.md
├── hooks-policy.md
├── rules-policy.md
├── adoption.md
└── marketplace-baseline.txt
```

### Phase 4 — Verification

- All `disabled-default` hook entries in canonical `ECC_DISABLED_HOOKS`.
- All `redundant-to-tdt-skill:<x>` entries point to real TDT skill files.
- All `investigate` entries resolved before archive.
- Playbook dry-run reproduces disposition within ±0 entries.

## Classification enum

```yaml
keep-load-bearing:        # actively used
keep-optional:            # installed, available if asked
disabled-default:         # disabled via ECC_DISABLED_HOOKS or simply not invoked
redundant-to-tdt-skill:   # TDT has an equivalent; prefer TDT
stack-irrelevant:         # language/framework we don't run
domain-irrelevant:        # vertical we don't operate in
no-evidence:              # 0 usage in 90 days; description generic
```

## Spec structure (7 specs)

Each spec follows our OpenSpec style: SHALL/MUST for requirements, scenarios with WHEN/THEN, RFC 2119 enforced.

- `skills-disposition/spec.md` — classification rubric + every skill's disposition table
- `hooks-policy/spec.md` — canonical `ECC_DISABLED_HOOKS` + decision criteria
- `agents-policy/spec.md` — agents bucketing + per-language keep list
- `commands-policy/spec.md` — trigger-point vs passive-helper classification
- `rules-policy/spec.md` — language rule dir surface list
- `adoption/spec.md` — selected v2.0 features + integration plan
- `release-audit-playbook/spec.md` — methodology codified as executable procedure

## Tasks (high-level)

See `tasks.md` for the 1-2 hour chunked breakdown across §1 Discovery through §8 Archive (~12 hours total).

## Risks

- `autoUpdate: true` upgrades ECC mid-audit → pin for change duration.
- Cost-tracker.log doesn't log invocations → fall back to session JSONL.
- TDT overlay incomplete vs ECC coverage → adopt `python-reviewer` agent.
- Marketplace clone advances during change → Phase 1.6 captures baseline SHA.
- TDT duplicate skill names with ECC → verify precedence.

## Full design spec

See `docs/superpowers/specs/2026-06-27-ecc-harness-alignment-design.md` for the canonical brainstorming-session design with full task breakdown, success criteria, and open questions.