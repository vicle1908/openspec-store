# Independent plan review — Round 2, reviewer-apply-safety (sub-0c1bc92d)

Reviewer completed analysis without delivering a parent-reply message (transcript recovered by parent
from the child session artifacts; findings verbatim from the reviewer's final reasoning pass).
Review scope: overlay-contract.json (11 entries), pre-apply-manifest.json, manifest-check.py,
overlay-contract-check.py, sentinel-fixtures.json, default-probe-matrix.json + contract checker,
value-blindness scan of evidence checkers, store hygiene, tasks.md sections 4-6 executability.

## VERDICT: FAIL (2 MAJOR, 6 MINOR — no BLOCKER; all fixable without touching live configs)

## FINDINGS

1. **MAJOR — Claude Code ownership contradiction.** tasks.md §3.1/§4.1 apply the Claude Code
   profile/helper/launcher in this change, but overlay-contract.json's description says Claude Code
   "is satisfied by the separately owned active change add-claude-code-omniroute-pm-launcher and has
   no entries here". Dual-writer risk on `~/.claude/profiles/omniroute.json` + helpers violates the
   change's own single-writer principle. Fix: strike 3.1/4.1 from this change (Claude surface is
   already applied and verified by the archived change) or add explicit overlay entries.

2. **MAJOR — Pi overlay collision.** overlay-contract.json entry 6 merge_key `providers.omniroute`
   collides with the existing live provider in `~/.pi/agent/models.json` (6 models +
   `compat.supportsLongCacheRetention`); the overlay carries 1 model. Merge-depth for the provider
   object / models array is undefined; manifest-check.py cannot detect intra-provider model loss
   (v1 baseline has no model_ids). Fix: define object-level merge preserving sibling models/compat,
   or rename keys like prime (`omniroute-responses`), or pin an explicit model_ids baseline for pi.

3. **MINOR — Codex protected path naming.** Entry 1 protected_baseline_paths includes
   `~/.Claude-Fable:providers`, but the live key is `model_providers`. A path-based guard would
   protect nothing. Fix: rename to `model_providers`.

4. **MINOR — Claude-Fable merge_key wildcard.** Entry 2 merge_key contains `model.*`, ambiguous between
   "all entries under [model]" and the two named template entries. Fix: enumerate
   `model.omniroute-sol`, `model.omniroute-claude-fable`.

5. **MINOR — Factory/Droid upsert depth.** `upsert-custom-models-by-id` semantics undefined for
   sibling fields; live `custom:OmniRoute-Claude-Fable` has `index: 5` which the overlay omits.
   Fix: state whole-object replace or field-merge explicitly.

6. **MINOR — Rollback shape for baseline-absent files.** pre-apply-manifest.json rollback marks new
   files (omniroute.config.toml, custom_omniroute_anthropic.json, omniroute-key.sh, omniroute.json)
   backup_required:true / restore-style, but manifest-check.py's candidate contract requires new
   files to roll back by delete-created-file with backup_required false. Fix: baseline rollback
   entries for non-existent files must switch to delete-on-rollback semantics.

7. **MINOR — "12 mutate targets" count unexplained.** Task 2.4 wording and apply_safety say 12, the
   overlay lists 11, Claude Code is disclaimed by the overlay contract. Fix: enumerate the exact
   mutate-target list (11 overlay targets; Claude surface owned by the archived change).

8. **MINOR — Default-probe runner unspecified.** default-probe-matrix.json rows do not conform to
   cli-probe-runner.py's row schema (cwd vs working_directory, endpoint_path, env_allow); the
   executing runner for task 5.4 is unstated. Fix: name the runner or extend the schema mapping.

## NOTES

- Cline overlay correctly avoids unproven `pm/Claude-Fable` (checker enforces); sh/Claude-Fable over
  chat is consistent with disposition FBC-5.
- "unused-local-keyless" placeholders are deliberate for the keyless loopback inference; probe-proven.
- Sentinel fixtures, default-probe static contract, value-blindness of retained checkers, store
  hygiene (no credential literals, no backup files in change dir): all verified PASS.
- route-contract-check.py and capture-manifest.py value-blindness was spot-checked, not fully read
  (reviewer's own caveat).
