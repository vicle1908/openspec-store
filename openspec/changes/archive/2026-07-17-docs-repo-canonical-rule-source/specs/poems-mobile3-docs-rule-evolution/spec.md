# Spec: `poems-mobile3-docs` — Rule-Evolution Envelope (Cross-Team Contract)

The `poems-mobile3-docs` repository, specifically the folder `20.Developments/40.AI/50.RCA/<platform>/rules/categories/`, is the **single source of truth for the whole team's rulebook** and **will evolve over time**. This spec declares the binding contract under which future rule PRs MUST operate. It is enforced by the AI workflow (`p3-rca-assistant`, `p3-bug-fixing-report`), the daily scanner (`code-daily-scan`), and the team review process.

## ADDED Requirements

### Requirement: E-1 — Version marker (recommended, not required in v1)

Every rule heading MAY carry a version line in the form of an HTML comment immediately after the title. When the marker is present, the scanner MUST parse it; when the marker is absent, the scanner MUST continue loading the rule and emit a one-shot warning.

#### Scenario: Versioned rule is parseable
- GIVEN a markdown file with the comment `<!-- rule:version=3 last_reviewed=2026-07-08 -->` after the title
- WHEN the scanner parses the file
- THEN the rule's effective version MUST be `3` (a future enhancement may surface this in scan output)
- AND the scanner MUST NOT fail when the comment is absent (graceful degradation).

#### Scenario: Unversioned rule logs a one-shot warning
- GIVEN a markdown file with no `rule:version` comment
- WHEN the scanner loads the file
- THEN the scanner MUST emit exactly one `INFO` log line per scan, per file, of the form `unversioned_rule=<file>` 
- AND the load MUST continue (the warning is non-blocking).

#### Scenario: Version marker shape
- A versioned rule looks like this:

```
## C1 — Title
<!-- rule:version=3 last_reviewed=2026-07-08 -->
```

- GIVEN a markdown file with the comment shape above
- WHEN the scanner parses the file
- THEN the rule's effective version MUST be `3`.

### Requirement: E-2 — Rules MAY be marked deprecated (non-removal)

A rule MAY be marked deprecated without removal. The marker SHALL be a fenced HTML comment placed between the title and the priority line.

#### Scenario: Deprecated rule is still loaded but warned
- GIVEN a markdown file with `<!-- rule:deprecated=2026-08-01 replacement=RCA-ARCH-001 -->` after the title
- WHEN the scanner loads the file
- THEN the rule MUST be returned by `load_category()` (deprecation is non-removal)
- AND the scanner MUST emit one `INFO` log line `deprecated_rule=<file>:<rule_id> replacement=<RCA-ARCH-001>`.

### Requirement: E-3 — Cross-platform reference markers are declarative only in v1

A rule MAY declare a cross-platform counterpart with a comment of the form `<!-- rule:cross_platform=<other-platform-folder>/<rule_id> -->`. In v1, the scanner MUST NOT act on this marker beyond logging its presence.

#### Scenario: Cross-platform marker is recognised but not enforced
- GIVEN a markdown file with `<!-- rule:cross_platform=10.iOS/RCA-STATE-001 -->`
- WHEN the scanner loads the file
- THEN the rule MUST be returned unchanged
- AND the scanner MUST emit a `DEBUG` log line `cross_platform_marker=<other>/<id> for=<self>` (v1 only — informational, not enforced).

### Requirement: E-4 — Retired rules live in `categories/.retired/`

A retired rule (no longer relevant, kept for historical reference) SHALL be moved to a sibling `categories/.retired/` subfolder and removed from `categories/`. The scanner MUST NOT load rules from `categories/.retired/` (path glob is `*/categories/*.md`, not recursive).

#### Scenario: Retired rule is not loaded
- GIVEN a markdown file at `categories/.retired/old-c1.md`
- WHEN the scanner resolves the categories directory
- THEN the file MUST NOT be picked up by `*.md` glob
- AND no rule from that file appears in the output.

### Requirement: E-5 — Docs-repo rule edits are exempt from the OpenSpec pre-edit gate

The pre-edit OpenSpec gate (which applies to Python TDT sub-repos) does NOT apply to edits of `poems-mobile3-docs/50.RCA/<platform>/rules/categories/*.md`. Every docs-repo rule PR is NOT required to ship its own OpenSpec change. The E-1..E-4 envelope is the lightweight governance that takes its place.

#### Scenario: A small rule append is shipped without an OpenSpec change
- GIVEN a developer or `p3-rca-assistant` agent adds a new `RCA-STATE-004` rule to `20.AOS/rules/categories/state-mutation.md`
- WHEN the PR is raised
- THEN the change is mergeable without an accompanying OpenSpec proposal
- AND the changelog `50.RCA/changelog.md` `[Unreleased]` section is the only required governance record.

## MODIFIED Requirements

### Requirement: S-1 — 9-category taxonomy is fixed (no implicit additions)

The set of category filenames under each platform's `rules/categories/` folder SHALL be exactly these nine, in this naming convention:

| Filename | Internal `category` string |
|---|---|
| `crash-runtime.md` | `Crash` |
| `memory-lifecycle.md` | `Memory Leak` |
| `performance-resource-usage.md` | `Performance` |
| `architecture-maintainability.md` | `Architecture` |
| `security-network-hardening.md` | `Security` |
| `state-mutation.md` | `State Mutation` |
| `pattern-consistency.md` | `Pattern Consistency` |
| `naming-readability.md` | `Naming & Readability` |
| `testing-coverage.md` | `Testing Coverage` |

#### Scenario: 10th category file triggers the 9/10 incomplete check
- GIVEN a docs-repo `20.AOS/rules/categories/` folder with all 9 listed files plus an unexpected 10th file
- WHEN the scanner resolves the folder
- THEN the scanner MUST log `docs_repo_unexpected_file=<filename>`
- AND MUST NOT treat the 10th file as a load target (the loader's glob is the canonical 9).

#### Scenario: A canonical 9 file is missing
- GIVEN a docs-repo `20.AOS/rules/categories/` folder that is missing `state-mutation.md`
- WHEN the scanner resolves the folder
- THEN the scanner MUST log `docs_repo_incomplete=true missing=[state-mutation.md]`
- AND MUST fall back to the local mirror for that specific category (not the whole folder)
- AND the `resolved_source=` log line for that category MUST say `local_mirror:` even if the rest of the categories come from `docs_repo:`.

#### Scenario: Renaming a category file is an evolution event
- GIVEN a PR that renames `architecture-maintainability.md` to `clean-architecture.md`
- WHEN the PR is reviewed
- THEN the PR is REJECTED (this is an S-1 contract violation; the 9 filenames are fixed)
- AND the rejection message points to this requirement.

### Requirement: S-2 — Rule IDs conform to a known regex

Rule IDs MUST match one of:

| Pattern | Examples |
|---|---|
| `^[A-Z]+(?:-[A-Z]+)?-\d{3}$` | `RCA-STATE-001`, `RCA-ARCH-001`, `RCA-PAT-001` |
| `^[A-Z]\d+$` | `C1`, `P4`, `A7`, `S2`, `L6` |

#### Scenario: ID outside the pattern is rejected with warning
- GIVEN a markdown file with `## MY-BAD-ID-9 — Title`
- WHEN the scanner parses the file
- THEN the scanner MUST emit a `WARNING` log line `invalid_rule_id=<id> file=<file>`
- AND the rule MUST be skipped (not added to `RulePattern` list).

### Requirement: S-3 — `scan-output-schema.md` enumerates all 9 categories

The `50.RCA/<platform>/technical-debt-scan/scan-output-schema.md` files MUST list all 9 internal `category` values from S-1 as the allowed enum for scan findings. The current 7-value enum is a known gap that this change requires an evolution PR to close.

#### Scenario: Schema file lists 9 categories
- GIVEN the v1 evolution PR has been merged
- WHEN an operator opens `50.RCA/20.AOS/technical-debt-scan/scan-output-schema.md`
- THEN the `category` enum section MUST list all 9 values from S-1
- AND a `category_mapping_notes.md` reference MAY be added to explain scanner-dispatch remapping.

#### Scenario: AI agent and scanner agree on category vocabulary
- GIVEN the scanner returns a `RulePattern` with `category="State Mutation"`
- WHEN the `p3-scan-technical-debt` skill formats a finding for the same rule
- THEN the `category` field in the formatted finding MUST be `State Mutation`
- AND MUST match the enum from `scan-output-schema.md`.

### Requirement: S-4 — `changelog.md` is the canonical evolution log

The top-level `50.RCA/changelog.md` SHALL be the single place where evolution events (category add/remove, rule add/deprecate, contract change) are recorded. Each entry MUST include: version tag, date, and a short rationale. The `[Unreleased]` section is the working buffer.

#### Scenario: v1 of this change adds an `[Unreleased]` entry
- GIVEN the v1 evolution PR has been merged
- WHEN an operator opens `50.RCA/changelog.md`
- THEN the top section MUST be `## [Unreleased]` and MUST contain a `### Changed` entry noting the scanner's docs-repo wiring
- AND the previous v1.1.0 entry MUST remain unchanged.

### Requirement: S-5 — Provenance markers (recommended)

Each rule SHOULD (NOT MUST) carry a `<!-- rule:source=... -->` comment. The value is one of:

- A Jira ticket: `rule:source=STABI-1234`
- A short commit SHA: `rule:source=f8ec84a`
- An `issue-reports/<ticket>.md` filename: `rule:source=issue-reports/SR-2647.md`

#### Scenario: Source marker is logged but not enforced
- GIVEN a rule with `<!-- rule:source=STABI-1234 -->`
- WHEN the scanner parses the rule
- THEN the scanner MUST emit a `DEBUG` log line `rule_source=<id>:<source_value>`
- AND a rule without a source marker MUST NOT fail to load (graceful degradation).

### Requirement: S-6 — Cross-platform name-collision is NOT rule identity

A rule ID like `C4` MAY exist on both platforms with different titles. Name-collision SHALL NOT be interpreted as rule identity. The optional `<!-- rule:cross_platform=... -->` (E-3) is the only sanctioned way to declare cross-platform rule identity. Anything else is treated as coincidence.

#### Scenario: AOS `C4` and iOS `C4` are distinct rules
- GIVEN AOS `crash-runtime.md` defines `## C4 — Unsafe list or array indexing`
- AND iOS `crash-runtime.md` defines `## C4 — Unsafe array or collection indexing`
- WHEN the scanner loads each platform's rules
- THEN the resulting `RulePattern` lists MUST be independent (no implicit merge)
- AND the scanner MUST emit `INFO` log line `name_collision=<id> aos=<title1> ios=<title2>` (informational; aids reviewers in spotting future cross-platform alignments).

### Requirement: S-7 — `p3-rca-assistant` agent is the canonical rule-producer

Rule production (adding new rules to `poems-mobile3-docs/50.RCA/<platform>/rules/categories/*.md`) MUST be performed by the `p3-rca-assistant` agent when triggered by an "RCA Handoff Block" emitted by `p3-bug-fixing-report`. The agent is not yet present in the docs repo (as of the v1.1.0 freeze, 2026-06-18) and MUST be introduced as part of the docs-repo evolution PR (tasks §11.7).

#### Scenario: `p3-rca-assistant` agent file is missing
- GIVEN the v1.1.0 docs-repo state
- WHEN an operator runs `find poems-mobile3-docs -name 'p3-rca-assistant.md'`
- THEN the file is NOT found (this is the current state)
- AND the docs-repo evolution PR (tasks §11.7) is REQUIRED before any AI agent can produce rules automatically.

#### Scenario: Agent file present after evolution PR lands
- GIVEN tasks §11.7 has shipped
- WHEN a developer pastes an RCA Handoff Block into the agent
- THEN the agent MUST append a new rule to the appropriate `rules/categories/<category>.md` file
- AND MUST populate the `<!-- rule:source=<ticket> -->` marker (S-5)
- AND MUST append a dated entry to `50.RCA/changelog.md` `[Unreleased]` (S-4)
- AND MUST add a row to `issue-reports/<ticket>.md` under "New Rules Generated"
- AND MUST update `todos/{gaps|partial-fixes|new-open}.md` if the gap analysis produces follow-up work
- AND MUST honour E-1..E-4 envelope markers when editing the rule file.

#### Scenario: Agent is advisory, not authoritative, in v1
- GIVEN the agent file exists but a developer chooses to author a rule by hand
- WHEN the PR is raised
- THEN the PR is mergeable without invoking the agent (the E-1..E-4 envelope is the contract; the agent is one way to comply with it)
- AND the `[Unreleased]` changelog entry is still required (S-4).

### Requirement: S-8 — MUST/SHOULD/MAY discipline

This spec uses RFC 2119 keywords with the following strict meanings. Any requirement that does not contain at least one of **MUST** / **SHALL** / **SHOULD** / **MAY** in its first paragraph is invalid and MUST be rejected by `openspec validate --strict`.

- **MUST** / **SHALL** — required for the change to be considered complete. A failure to satisfy a MUST is a release blocker.
- **SHOULD** — recommended for the change to be considered "production-grade." A failure to satisfy a SHOULD is a release warning, not a blocker.
- **MAY** — optional. The change MAY include or exclude the feature; both are acceptable.

#### Scenario: Authoring a MUST requirement
- GIVEN a requirement that constrains scanner behaviour with no opt-out (e.g. "the scanner MUST emit one log line per category")
- WHEN the requirement is authored
- THEN the prose MUST use the keyword **MUST** (or **SHALL**)
- AND `openspec validate --strict` MUST accept the change as valid.

#### Scenario: Authoring a SHOULD requirement
- GIVEN a requirement that recommends a behaviour but allows opt-out (e.g. "the docs repo SHOULD add `<!-- rule:version=... -->` markers")
- WHEN the requirement is authored
- THEN the prose MUST use the keyword **SHOULD** (or **RECOMMENDED**)
- AND the absence of the recommended behaviour MUST NOT be a release blocker.

#### Scenario: Authoring a MAY requirement
- GIVEN a requirement that documents optional behaviour (e.g. "the scanner MAY add a SHA-keyed cache in a follow-up")
- WHEN the requirement is authored
- THEN the prose MUST use the keyword **MAY** (or **OPTIONAL**)
- AND both including and excluding the behaviour MUST be acceptable.

#### Scenario: Detecting a requirement with no keyword
- GIVEN a requirement whose first paragraph contains none of MUST / SHALL / SHOULD / MAY
- WHEN the change is validated
- THEN `openspec validate --strict` MUST reject the change
- AND the error message MUST point to the offending requirement.

## Cross-references

- Internal: `code_daily_scan.plugins.android.rules_loader.AndroidRulesLoader` (L3 wiring)
- Internal: `code_daily_scan.plugins.ios.rules_loader.IOSRulesLoader` (L3 wiring)
- Internal: `code_daily_scan.config.PlatformConfig` (L3 wiring)
- External: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/10.iOS/rules/categories/`
- External: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/20.AOS/rules/categories/`
- External: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/<platform>/technical-debt-scan/scan-output-schema.md` (S-3)
- External: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/changelog.md` (S-4)
- External AI workflow: `poems-mobile3-docs/20.Developments/40.AI/30.AOS/agents/p3-bug-fixing-report.md` (RCA Handoff Block producer)
- External AI workflow: `poems-mobile3-docs/20.Developments/40.AI/<platform>/skills/p3-workflow/p3-scan-technical-debt/SKILL.md` (consumer)
- OpenSpec workspace rule: `.agents/modules/openspec.md` (E-5 explicit gate-removal)
