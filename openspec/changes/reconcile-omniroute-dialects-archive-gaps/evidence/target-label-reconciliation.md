# Target-Label Reconciliation — archived closure `new_files`

Subject archive (read-only): `openspec/changes/archive/2026-08-31-reconcile-omniroute-native-dialects/`

## The unmapped label

The archived closure records referenced a `new_files` list whose rendering in transcripts and session
displays reads `~/.Claude-Fable`/`~/.codex`-like hyphenated labels inconsistently (documented workstation
token-corruption on hyphenated identifiers). The final committed `post-apply-manifest.json` contains
`"new_files": []` (empty), and its `apply_log` lists 10 created/mutated rows — the earlier in-flight
version of that manifest carried one ambiguous label.

## Verified created targets (baseline-absent in the frozen pre-apply manifest, present on disk, value-blind)

| Target | Current SHA-256 (first 16) | Mode |
|---|---|---|
| `~/.claude/helpers/omniroute-key.sh` | 8c19caf7b87fbd67 | 0700 |
| `~/.Claude-Fable` | 2214ed1f0cf6144a | 0600 |
| `~/.config/goose/custom_providers/custom_omniroute_anthropic.json` | d7e731e5e9952d39 | 0600 |

(The `~/.claude/helpers/omniroute-key.sh` creation belongs to the separately archived
`add-claude-code-omniroute-pm-launcher` change surface, present in the frozen manifest as
baseline-absent and now on disk; listed for completeness of the reconciliation.)

## Reconciliation result

- The archived `new_files` label resolves to the two verified created routing targets in THIS family:
  the Codex selectable profile and the goose PM provider file.
- The committed archive record's empty `new_files: []` is incomplete rather than wrong: it fails to
  enumerate the verified creations. Recorded here as defect **D-4** in
  `evidence/archive-invalidity-report.md`.
- No unmapped label remains after this reconciliation.

## Method

Value-blind: per-file sha256 + mode only, read from disk; frozen-manifest baseline comparison done
read-only. No credential values appear.
