# commands-policy Specification

## Purpose
TBD - created by archiving change ecc-harness-alignment. Update Purpose after archive.
## Requirements
### Requirement: Every ECC command MUST have a disposition

The system SHALL classify every entry in `~/.claude/plugins/cache/everything-claude-code/ecc/<version>/commands/` against the canonical classification enum.

#### Scenario: Command classification is exhaustive

- **WHEN** an audit runs
- **THEN** every command appears exactly once in `audit/commands-disposition.md` with a non-null classification

### Requirement: Trigger-point commands MUST be cross-referenced with TDT/OpenSpec workflows

The system SHALL identify trigger-point commands (`/docs`, `/plan`, `/tdd`, `/code-review`, `/build-fix`, `/e2e`, `/verify`, `/multi-plan`, `/orchestrate`, `/harness-audit`, `/loop-start`, `/loop-status`, `/claw`) and classify them by whether a TDT or OpenSpec workflow covers the same intent.

#### Scenario: Trigger-point routing

- **WHEN** a trigger-point command `C` matches an OpenSpec workflow `W`
- **THEN** `C` SHALL be classified `redundant-to-tdt-workflow:W`; otherwise `keep-default`

Initial mapping from this rule:

- `/plan` → `keep-default` (no exact TDT equivalent; OpenSpec `propose` covers higher-level planning)
- `/tdd` → `keep-default` (we use it for new TDT code)
- `/code-review` → `keep-default` (general-purpose)
- `/build-fix` → `keep-default` (general-purpose)
- `/e2e` → `keep-default` (general-purpose)
- `/verify` → `keep-default` (OpenSpec `verify-change` is per-change, not session-wide)
- `/multi-plan`, `/multi-workflow`, `/multi-backend`, `/multi-frontend`, `/multi-execute`, `/orchestrate`, `/devfleet` → `keep-optional` (parallel orchestration; not in active TDT use today)
- `/loop-start`, `/loop-status` → `keep-optional` (loop operator pattern; not in active TDT use today)

### Requirement: Documentation commands MUST prefer TDT equivalents

The system SHALL prefer TDT equivalents for documentation, code review, and verification commands.

#### Scenario: Documentation overlap

- **WHEN** an ECC command overlaps with a TDT skill (e.g., `/docs` ↔ `tdt-meta/.agents/skills/ctx7/`)
- **THEN** the ECC command SHALL be classified `redundant-to-tdt-skill:<name>`; otherwise `keep-default`

Initial mapping:

- `/docs` → `redundant-to-tdt-skill:ctx7` (prefer our ctx7 CLI wrapper)
- `/code-review` → `keep-default` (no TDT equivalent; cross-cutting)

### Requirement: Session management commands MUST coexist with TDT equivalents

The system SHALL allow both ECC's session commands and TDT's `recall` / `remember` / `recap` / `handoff` skills to coexist.

#### Scenario: Session commands coexist

- **WHEN** an ECC command overlaps with a TDT session skill but the use case differs (e.g., `/save-session` vs `recap`)
- **THEN** the ECC command SHALL be classified `coexist` rather than `redundant-to-tdt-skill`

### Requirement: Update commands SHALL NOT auto-mutate TDT repos

The system SHALL reject any `keep-default` command that auto-mutates files inside `~/Developer/tdt/<repo>/` without explicit confirmation.

#### Scenario: Auto-mutation guard

- **WHEN** an ECC command (e.g., `/update-docs`, `/update-codemaps`) would auto-write to a TDT repo
- **THEN** it SHALL be classified `keep-optional` with a documented requirement that the user pre-confirms the target repo before invocation

