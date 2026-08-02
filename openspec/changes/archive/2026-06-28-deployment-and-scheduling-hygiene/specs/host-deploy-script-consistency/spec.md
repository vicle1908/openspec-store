# Capability: host-deploy-script-consistency

## Purpose

The two host-side LaunchAgent deploy scripts (`webhook-receiver/scripts/deploy.sh`
and `ai-review/scripts/deploy.sh`) are structurally similar but have
diverged on three safety properties. This capability brings `ai-review`
into alignment with `webhook-receiver`, and adds a `--require-clean`
opt-in flag to both.

> **Direction reversed 2026-06-27 (VP2-4).** Live `git status` shows
> `webhook-receiver`, `jira-daily-reports`, and `jira-skill` are
> already dirty on `main` today. A default-block gate would break the
> next deploy on those three repos. The capability therefore preserves
> the current default (warn-and-record) and adds an opt-in `--require-clean`
> flag for CI / production deploys that want stricter enforcement.

## ADDED Requirements

### Requirement: Stale uv lock fails the deploy

The `ai-review/scripts/deploy.sh` pre-deploy lock check SHALL exit
non-zero when any source repo's `uv.lock` is stale relative to its
`pyproject.toml`.

#### Scenario: ai-review lock check fails hard

- **GIVEN** `~/Developer/tdt/ai-review/uv.lock` is stale
  (out of sync with `pyproject.toml`)
- **AND** the user runs `bash ai-review/scripts/deploy.sh`
- **WHEN** the script reaches the pre-deploy gate loop
- **THEN** it SHALL print `ERROR: <repo>/uv.lock is stale relative to
  pyproject.toml` followed by the remediation `run 'cd <repo> && uv lock'
  and commit before deploying`
- **AND** it SHALL exit 1
- **AND** the script SHALL NOT copy source, run `uv sync`, regenerate the
  launcher, or restart the LaunchAgent

#### Scenario: ai-review lock check passes silently

- **GIVEN** every source repo's `uv.lock` is consistent with its
  `pyproject.toml`
- **WHEN** the pre-deploy gate loop completes
- **THEN** the script SHALL print `all source lockfiles consistent`
- **AND** it SHALL proceed to the source copy step

### Requirement: Snapshot covers every copied path dep

The `ai-review/scripts/deploy.sh` SHALL compute and diff SHA-256
snapshots for every repo that the copy loop places into
`$DEPLOYMENT_ROOT/deps/`.

#### Scenario: A path dep source change is caught

- **GIVEN** the deploy script copies the following repos into
  `$DEPLOYMENT_ROOT/deps/`: `tdt-core`, `jira-daily-reports`, `jira-skill`,
  `tdt-sheets`, `webhook-receiver`, plus the app itself
- **WHEN** the snapshot+diff phase runs
- **THEN** snapshots SHALL exist for all 6 source/runtime pairs
- **AND** if any pair's source SHA-256 differs from its runtime SHA-256
  the script SHALL exit 1 with `runtime copy does not match source
  worktree snapshot: <pair>`
- **AND** the deployment manifest SHALL record the SHA-256 of each pair

#### Scenario: No path deps changed

- **GIVEN** every dep's source tree is unchanged since the last deploy
- **WHEN** the snapshot+diff phase runs
- **THEN** all 6 pairs SHALL match
- **AND** the script SHALL proceed to the `sed` rewrite + `uv sync` steps

### Requirement: Deploy script SHALL fail fast when `--require-clean` is passed and worktree is dirty

SHALL print a warning when the source worktree has uncommitted changes,
and SHALL exit non-zero **only when** `--require-clean` is passed on the
command line. The default behavior (warn-and-record) is preserved for
backward compatibility with the existing production dirty-worktrees.
Both `webhook-receiver/scripts/deploy.sh` and `ai-review/scripts/deploy.sh`
SHALL implement this behavior.

#### Scenario: Clean worktree, no flag

- **GIVEN** `git -C $SRC status --porcelain` is empty
- **AND** the deploy script is invoked with no flags
- **WHEN** the dirty-worktree gate runs
- **THEN** the gate SHALL pass silently
- **AND** the deployment manifest SHALL record `"source_dirty": false`
  and `"gate_require_clean": false`
- **AND** the script SHALL proceed

#### Scenario: Dirty worktree, no flag (current production behavior)

- **GIVEN** `git -C $SRC status --porcelain` is non-empty
- **AND** the deploy script is invoked with no flags
- **WHEN** the dirty-worktree gate runs
- **THEN** the script SHALL print
  `WARNING: source worktree has uncommitted changes; continuing (use --require-clean to fail)`
  followed by the `git status --short` output
- **AND** the deployment manifest SHALL record `"source_dirty": true`
  and `"gate_require_clean": false`
- **AND** the script SHALL proceed (current behavior preserved)

#### Scenario: Dirty worktree, --require-clean

- **GIVEN** `git -C $SRC status --porcelain` is non-empty
- **AND** the deploy script is invoked with `--require-clean`
- **WHEN** the dirty-worktree gate runs
- **THEN** the script SHALL print `ERROR: source worktree has uncommitted
  changes: <list>` followed by the remediation `commit, stash, or remove
  --require-clean`
- **AND** exit 1
- **AND** the deployment manifest SHALL NOT be written (deploy did not
  happen)

#### Scenario: Clean worktree, --require-clean

- **GIVEN** `git -C $SRC status --porcelain` is empty
- **AND** the deploy script is invoked with `--require-clean`
- **WHEN** the dirty-worktree gate runs
- **THEN** the gate SHALL pass
- **AND** the deployment manifest SHALL record `"source_dirty": false`
  and `"gate_require_clean": true`
- **AND** the script SHALL proceed

### Requirement: Manifest records the gate state

Both deploy scripts SHALL include a `gate_require_clean` field in
`$STATE_DIR/deployment-manifest.json` indicating whether the deploy was
run with the stricter cleanliness gate enabled.

#### Scenario: Deployment manifest post-deploy

- **WHEN** a deploy completes successfully
- **THEN** `$STATE_DIR/deployment-manifest.json` SHALL be valid JSON
- **AND** it SHALL contain `"gate_require_clean": <bool>` (always emitted)
- **AND** it SHALL contain `"source_dirty": <bool>` (always emitted)
- **AND** it SHALL contain `"source_head_sha": <40-char-sha>` or `null`
