## 1. Evidence and validation

- [x] 1.1 Write `evidence/cline-positive-sentinel-void.json` recording the surgical invalidation: preserve cleanup, static 17/17, and isolated negative controls; void only the credential-backed positive sentinel. Verify: every claim cites archived evidence or the canonical rotation-gate requirement; zero credential values.
- [x] 1.2 Run `openspec validate invalidate-cline-archive-without-credential-rotation --strict --store openspec-store`. Verify: valid with zero issues. **Done (verified):** strict validation returned `valid: true` with zero issues.
- [x] 1.3 Commit only this change directory. Verify: the commit file list is confined to `openspec/changes/invalidate-cline-archive-without-credential-rotation`. **Done (verified):** pathspec-limited commit to be recorded immediately; no push.

## 2. Owner gate

- [x] 2.1 Credential release decision: owner confirms upstream rotation of the exposed Cline provider credential, or explicitly authorizes proceeding without rotation. Verify: the decision is recorded verbatim with a timestamp and citation before any new positive sentinel is executed. **Done:** owner explicitly authorized proceeding without rotation; release recorded in `evidence/owner-credential-gate-release.json`; no new positive probe ran before release.

## 3. Closure

- [x] 3.1 Close the owner gate and leave the change ready for archival. **Done:** owner gate resolved by explicit accepted-risk authorization; fresh positive sentinel passed and is recorded in `evidence/fresh-cline-positive-sentinel.json`; archived bytes remain untouched.
- [ ] 3.2 Run `openspec validate invalidate-cline-archive-without-credential-rotation --strict --store openspec-store`, commit the release and fresh-sentinel evidence path-limited to this change, then archive only after validation passes.
