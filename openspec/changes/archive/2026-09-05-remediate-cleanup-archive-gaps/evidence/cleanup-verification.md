# Remediation Summary for Cleanup Archive Gaps

**Change:** remediate-cleanup-archive-gaps
**Generated:** 2026-09-05T01:24:53Z
**Mode:** read-only corrective evidence; no mutation of applications, repositories, worktrees, or archived change files

## Evidence Artifacts

| Artifact | SHA-256 |
|---|---|
| `evidence/cleanup-verification.json` | `53b4eadfeed35043871bc828ff8439494a8ce1c2602fd7333196fbf27981b7fa` |
| `evidence/repository-inventory.txt` | `e025d0ef17967da8efe18ab3040f5e62f612bb4c35147bbe0448b7a9816087df` |

JSON syntax: valid (`python3 -m json.tool` passed). Credential-shape scan across `evidence/`: zero matches.

## Archived Ledger Task-Count Reconciliation

| Archive | Checked Tasks | Prior Report Claim | Resolution |
|---|---:|---:|---|
| `2026-09-05-ecosystem-cleanup` | 21 (5+1+6+2+3+1+3) | 20/20 | Corrected to 21/21 |
| `2026-09-04-fix-corrupted-brew-casks` | 17 (1+6+2+3+3+2) | 19/19 | Corrected to 17/17 |

## Ecosystem Cleanup Archive (`5360249`)

Authoritative inventory: 19 repositories (18 from `/Users/androidteam/Developer/AGENTS.md:365-368` + `tdt-scheduler`). All 19 rows recorded in the JSON evidence.

**Verified:**

- All 19 repositories on their default branch (`main`, `hermes-webui` on `master`).
- Worktree count: exactly 1 per repo (its main checkout), 0 extra/stale worktrees. Archive task 7.2's literal "total ≤10 across all repos" is **contradicted** — 19 is the minimum possible with 19 repos each keeping a main checkout. The 7 originally-affected repos total 7 (satisfies ≤10 only under that narrower reading).
- Clean status (task 7.1): 5 repos dirty, each with exactly one untracked `.claude/` path — the archive's own allowed exception. **Verified under its stated exception.**


**Contradicted / since resolved:**

- Archive task 6.1 claimed embedded-copy comparison "produced." Investigation (see `embedded-copies-resolution.md`) found the "embedded copies" were empty untracked stub dirs (0 files), not stale source copies; diff entries were upstream-only files. Current build consumes workspace-root inputs via the allowlist + bind mounts; zero tracked references to the stubs. **Resolved 2026-09-05 by owner decision**: 9 empty stub dirs removed (`rmdir`, fail-safe); tdt-scheduler git status clean; build contract intact.

## Brew Cask Cleanup Archive (`dce0811`)

All 8 target apps verified by **executable-aware** checks (plist CFBundleExecutable declared vs. actual executable path, size, mode) — not the archive's plist-presence-only checks:

- VS Code: `Code`, 67,840 B, `-rwxr-xr-x` ✓
- Ollama: `Ollama`, 52,462,320 B ✓
- Google Chrome: `Google Chrome`, 367,696 B ✓
- Postman: `Postman`, 69,248 B ✓
- Warp: `stable`, 838,416,528 B ✓
- Orca: `com.stablyai.orca` v1.4.197, `Orca`, 53,632 B ✓ (identity + version verified)
- AutoForward Messages: `Runner`, 5,989,504 B, `-rwxr-xr-x`, sha256 `8ef539ac…` ✓
- Nicegram: `Telegram`, 158,624 B, `-rwxr-xr-x`, sha256 `554f9e92…` ✓

The archive's internal contradiction (6.1 "zero corrupted" via plist-only while 5.1–5.2 required missing executables) is **currently resolved on disk**: both sideloaded executables now exist, are nonzero, and carry executable mode. Reinstall gate recorded as **resolved/currently unnecessary** — no provenance claimed.

- Caskroom `orca` present; `.upgrading` directories: 0.
- `brew doctor` exit 1 — but warnings target `cockpit-tools`/`antigravity-cli` Caskroom metadata and unlinked kegs, **not** any of the 6 brew-managed target apps. Recorded as unrelated findings.
- Executable-aware full `/Applications` scan: **0 apps missing their declared executable** (fixes the archive's false-positive plist-only closure).

## Immutability Check

`git status --porcelain` in openspec-store: only untracked `openspec/changes/remediate-cleanup-archive-gaps/`. No archive path modified.

## Remaining Open Items

1. ~~tdt-scheduler embedded copies~~ **RESOLVED 2026-09-05**: empty vestigial stubs removed by owner decision (`evidence/embedded-copies-resolution.md`); no copy sync needed — build uses workspace-root inputs.
2. 5 dirty repos: ownership unknown (likely concurrent sessions); classified, not touched.
3. `brew doctor` Caskroom warnings for `cockpit-tools`/`antigravity-cli`: outside this archive's scope.
4. Cline/provider archive invalidation chain: historical context only; no credential/provider surface changed.
