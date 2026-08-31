# Tasks: fix-storewide-spec-purpose-placeholders

- [x] 1.1 Enumerate specs with TBD Purpose placeholders (54 found, value-blind).
- [x] 1.2 Derive and write a real Purpose for each from its own first requirement (53 fixed, 1 already clean).
- [x] 1.3 Re-run `openspec validate --all --strict --store openspec-store`: 400 passed / 1 failed
      (pre-existing 55 → 1; the residual is an archived-change CLI quirk, not a spec defect).
- [x] 1.4 Pathspec-limited commit (`openspec/specs/` + this change dir); no push.
