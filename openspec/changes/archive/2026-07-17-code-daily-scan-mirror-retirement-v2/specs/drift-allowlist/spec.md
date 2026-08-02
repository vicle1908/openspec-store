# Spec: Drift Allowlist File Format

## ADDED Requirements

### Requirement: AL-1 — Allowlist file location and naming

The `.drift-allowlist` file MUST be located at `<mirror_root>/.drift-allowlist`, where `<mirror_root>` is `docs/rules/categories/` within the platform repo.

#### Scenario: Allowlist file is found at correct path
- GIVEN `docs/rules/categories/.drift-allowlist` exists with valid entries
- WHEN `check-docs-drift --platform=android` runs
- THEN the file is read and entries are parsed.

### Requirement: AL-2 — Allowlist line format

Each non-comment, non-empty line in `.drift-allowlist` MUST conform to the following format:

```
<category-stem> <free-text-reason> <YYYY-MM-DD>
```

Where:
- `<category-stem>` is the lowercase stem of the category file (e.g., `state-mutation`, `memory-lifecycle`).
- `<free-text-reason>` is a human-readable explanation (may contain spaces, no line breaks).
- `<YYYY-MM-DD>` is the expiry date in ISO 8601 format.

Lines starting with `#` are treated as comments and ignored. Empty lines are ignored.

#### Scenario: Valid allowlist entry
- GIVEN a line `state-mutation intentionally modified for FEATURE-X 2026-12-31`
- WHEN `check-docs-drift` parses the allowlist
- THEN it MUST record that `state-mutation` is allowlisted until `2026-12-31`.

#### Scenario: Comment lines are ignored
- GIVEN a line `# state-mutation intentionally modified 2026-12-31`
- WHEN `check-docs-drift` parses the allowlist
- THEN it MUST NOT treat this as a valid entry.
