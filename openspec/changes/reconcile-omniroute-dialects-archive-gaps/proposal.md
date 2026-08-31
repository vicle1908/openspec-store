## Why

The change `reconcile-omniroute-native-dialects` was archived on 2026-08-31 (`openspec/changes/archive/2026-08-31-reconcile-omniroute-native-dialects/`) while gates its own task 6.6 contract required to be green were still open ("Archive only if every required applied route is green; otherwise leave the change active with explicit blocker tasks and preserved evidence"). The archived closure carries verifiable defects: the Kimi/Cline credential-rotation security gate was never released yet both files were applied and their verification tasks ticked; the closure manifest cites the wrong SH model ID (`sh/Claude-Fable` in SH rows where the change's routes require `sh/gpt-5.6-sol`); the post-apply manifest omits the Grok apply that happened at 11:29:04 (20 minutes after the manifest was written); an omp file mode was tightened 0644→0600 without the named approval its own policy required; and a `new_files` label maps to no verified target. The archive's safety lock forbids editing the archived copy, so this corrective change reconciles the gaps in a new active ledger that references the archive read-only.

## What Changes

- Reopens, as explicit blocked tasks, the gates the archive closed over:
  - Kimi/Cline credential-rotation gate: the Kimi live route sentinel and the literal-key preservation metadata proof stay BLOCKED pending explicit user confirmation that the exposed credentials were rotated upstream, or written authorization to proceed without rotation. No live calls through credential-carrying configs until released.
  - omp `~/.omp/agent/models.yml` mode change 0644→0600 ratification: owner decision to ratify or revert; no further mode tightening without a pre-recorded named approval.
  - cline live sentinel: remains FBC-5 blocked (requires a cline auth session, user-owned); config-level route-contract evidence stands.
- Records a corrective closure register as new evidence under this change (archived artifacts referenced read-only, never edited):
  - Corrected model-ID register: SH route model `sh/gpt-5.6-sol`, PM route model `pm/Claude-Fable`, superseding the archived final-evidence-manifest's SH rows citing `sh/Claude-Fable`.
  - Complete applied-surface register covering all 11 applied files including Grok `~/.grok/config.toml` (applied 2026-08-31 11:29:04, backup `8626abe9ec687fcf-config.toml` in the backup root) and the verified created files (codex omniroute profile `~/.codex/omniroute.config.toml`, goose `~/.config/goose/custom_providers/custom_omniroute_anthropic.json`), each with backup reference and rollback command.
  - Target-label reconciliation for the archived `new_files` entry labeled `~/.Claude-Fable`, which maps to no verified apply target and requires owner reconciliation.
  - Archive-invalidity report enumerating the closure defects (tick/evidence/disk contradictions) with line-number citations from the archived artifacts.
- Freezes a value-blind current-state register (sha256 + mode) of the 11 applied surfaces and the preservation set, reconciled against the archived pre-apply manifest baselines.
- Runs a value-blind credential-shape scan over every new evidence file this change produces; zero literal credentials; redaction on any hit.
- Adds spec requirements (see Capabilities) that make these closure integrity rules durable.

## Non-Goals

- No mutation of any live CLI configuration, credential, gateway, or archived artifact. The applied configs are verified live on disk; re-applying or rolling them back is out of scope.
- No editing of the archived change directory or canonical specs directly (spec changes only via this change's delta and a later archive).
- No expansion to the `add-ntu-ai-keynote-deck` change; its tasks 4.1/5.1/5.2 are external human gates (editorial sign-off, venue rehearsal, release tag) and cannot be performed or fabricated centrally.
- No push; any commit is store-local with pathspec-limited staging.

## Capabilities

### Modified Capabilities

- `omniroute-agent-cli-routing`: adds closure-integrity requirements — closure evidence SHALL cite the canonical route model IDs (`sh/gpt-5.6-sol` SH, `pm/Claude-Fable` PM); the applied-surface register SHALL match the final on-disk state with per-file backup/rollback metadata; mode tightenings SHALL be named-approved before apply; live verification through credential-carrying configs SHALL be rotation-gated.

## Ownership Boundaries

- Archived change `2026-08-31-reconcile-omniroute-native-dialects` (read-only reference; its safety lock forbids edits).
- This change directory (sole write root for evidence and ledger).
- Live CLI configurations and backups root `~/.hermes/backups/reconcile-omniroute-native-dialects/` (read-only, value-blind metadata only).
- User-owned decisions: credential rotation confirmation, omp mode ratification, cline auth session.
