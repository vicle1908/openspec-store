# Design: verify-npm-audit-remediation

## Context
This is a central-governance change in openspec-store whose subject matter lives in four external repositories (mcp-router, goose-docs, prime-agent, realtime/frontend). Per the multi-root governance rule, `allowedEditRoots` resolves to openspec-store only; external repositories are verified, not edited, by central apply. External bug fixes triggered by verification are executed as explicit external-evidence gates in this change.

## Goals
1. Independent re-execution of every audit/build/test claim made by the 2026-09-03 remediation session, in fresh processes, from current working-tree state.
2. Structural protection against literal-corruption defects: all version literals cited in evidence are read back from lockfiles/manifests programmatically, never hand-typed from memory.
3. Value-blind verification: evidence records store command, exit code, and observed output; no narrative claims without a corresponding command run in this verification pass.

## Non-Goals
- Re-doing or re-scoping the remediation itself.
- Upgrading unpatched upstream packages (image-size <=2.0.2, extract-zip <=2.0.1 in Electron Forge chains) — no patched versions exist at time of writing.
- Committing or pushing anything; single-writer repo serialization ends at the working tree.

## Decisions
- **Verification executor**: parallel task subagents, one per repository, read-only posture except where a verification run reveals a bug to fix (fixes are in-scope per proposal). This mirrors the remediation's parallel decomposition and respects per-repo single-writer rules (one worker per repo).
- **Gate semantics**: each task gate is satisfied by verifiable evidence (command + exit code + output excerpt recorded to evidence files), not by narrative. The mcp-router gate requires pnpm-only mutations (no package-lock.json may exist there).
- **Expected residual audits**: mcp-router 3 high, goose-docs/ui 1 high, goose-docs/documentation 18 high — all image-size/extract-zip unpatched-upstream chains, which must be byte-identified as such in evidence (patched_versions <0.0.0 or equivalent no-fix marker) rather than counted silently.
- **Bug-fix policy**: a bug is anything that makes a verification command fail that passed during remediation, or a defect in the migration code itself (e.g., wrong upstream literal, broken handler). Fixes stay minimal and scoped to the remediation surface; anything structural goes back to the owner.

## Risks / Trade-offs
- **Pre-existing failures unrelated to the remediation** (e.g., missing built workspace declarations in prime-agent) must be distinguished from regressions; evidence records must separate them explicitly rather than blocking the gate on unrelated breakage.
- **Audit counts drift over time** as new advisories publish; gates compare against the remediation session's recorded outcomes and explain any delta (new advisory vs. regression).
- **Concurrent writer session** is active in this store historically (fabrication pattern in memory); evidence must be file+line anchored and every gate tick re-derivable from the evidence files alone.

## Open Questions
None — the remediation outcomes are recorded in-session and each expected value is enumerated in tasks.md.
