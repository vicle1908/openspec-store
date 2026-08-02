# Hooks Policy Specification

## Purpose

Define which ECC hooks are disabled by default, which stay enabled, and the criteria for that decision. Codify the canonical `ECC_DISABLED_HOOKS` value as the single source of truth.

## ADDED Requirements

### Requirement: Canonical `ECC_DISABLED_HOOKS` value MUST be the single source of truth

The system SHALL maintain a single canonical `ECC_DISABLED_HOOKS` string at `audit/hooks-policy.md` top section. The value in `~/.claude/settings.json` MUST match.

#### Scenario: Settings value matches canonical

- **WHEN** the audit completes
- **THEN** the `ECC_DISABLED_HOOKS` value in `~/.claude/settings.json` SHALL equal the canonical value in `audit/hooks-policy.md`

### Requirement: Every hook in `hooks/hooks.json` MUST have a disposition

The system SHALL classify every hook from `~/.claude/plugins/cache/everything-claude-code/ecc/<version>/hooks/hooks.json` into one of three outcomes.

#### Scenario: Hook classification is exhaustive

- **WHEN** an audit runs
- **THEN** every hook id in `hooks.json` SHALL appear exactly once in `audit/hooks-policy.md` with disposition: `disabled-default`, `keep-default`, or `coexist`

### Requirement: `disabled-default` criterion MUST be declared

The system SHALL document, for each `disabled-default` hook, the rationale.

#### Scenario: Every disabled hook has rationale

- **WHEN** a hook is classified `disabled-default`
- **THEN** the row SHALL include a rationale citing one of: (a) overlapping with a TDT-installed hook, (b) broad-matcher on `Bash|Edit|Write|*`, (c) superseded by another hook, (d) no-observed-use over the audit window

### Requirement: `keep-default` hooks SHALL NOT overlap with TDT-installed hooks

The system SHALL flag any `keep-default` hook whose matcher overlaps with a hook installed by `agentmemory`, `gitnexus`, or `ccg` plugins.

#### Scenario: Overlap detection

- **WHEN** an ECC hook with matcher `Edit|Write|MultiEdit` is classified `keep-default`
- **THEN** the system SHALL flag it for manual review if any of `agentmemory`, `gitnexus`, `ccg` also install hooks with those matchers

### Requirement: New hooks in future releases MUST be classified within one release cycle

The system SHALL guarantee that any new hook appearing in a subsequent ECC release receives a classification before the next audit publishes.

#### Scenario: New-hook triage deadline

- **WHEN** a new ECC release ships new hooks
- **THEN** the playbook (see `release-audit-playbook/spec.md`) MUST include a "new hooks" diff step that resolves all new entries to a final classification

### Requirement: Coexist hooks SHALL NOT mutate state our hooks depend on

The system SHALL reject any `coexist` classification if the ECC hook writes to a file that an agentmemory/gitnexus/ccg hook reads.

#### Scenario: State-conflict detection

- **WHEN** an ECC hook is classified `coexist`
- **THEN** the system SHALL check whether the hook writes to `~/.agentmemory/`, `~/.claude/session-data/`, or any `<repo>/.gitnexus/` directory; if yes, reclassify to `disabled-default`