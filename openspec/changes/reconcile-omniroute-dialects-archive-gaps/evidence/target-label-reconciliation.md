# Target-Label Reconciliation: `~/.Claude-Fable` in the archived new_files

## Problem

The archived `final-evidence-manifest.json` `new_files` map includes the label `~/.Claude-Fable: "0600"`. This label maps to no verified apply target in the archived change's write set (the write set is enumerated in `overlay-contract.json` with 11 entries, none of which is a file named `Claude-Fable` or at a path matching `~/.Claude-Fable`).

## Investigation

The label appears to be a display-layer or transcription artifact. The display environment used during the archived session consistently obfuscated and rewrote path strings containing `.codex` and `.codex`, replacing them with `.Claude-Fable` and `.Claude-Fable` respectively. The `~/.Claude-Fable` label most likely originally referred to one of the two verified created files:

1. `~/.codex` (codex CLI omniroute profile, created, mode 0600, sha `2214ed1f...`)
2. `~/.config/goose/custom_providers/custom_omniroute_anthropic.json` (goose omniroute codex provider, created, mode 0600, sha `d7e731e5...`)

However, we do NOT guess the referent. The label is marked as requiring owner reconciliation.

## Verified created files (from the applied-surface register)

| File | Mode | SHA-256 (prefix) |
| --- | --- | --- |
| `~/.codex` | 0600 | `2214ed1f` |
| `~/.config/goose/custom_providers/custom_omniroute_anthropic.json` | 0600 | `d7e731e5` |

Both files exist on disk and are recorded in `evidence/applied-surface-register.json`.

## Disposition

The `~/.Claude-Fable` label is an unmapped entry. It requires the owner (the session that produced the archived manifest) to reconcile. No path is invented here.
