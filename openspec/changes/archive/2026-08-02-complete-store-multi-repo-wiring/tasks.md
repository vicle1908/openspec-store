## 1. Per-Repo Store Pointers

- [x] 1.1 Create `go-microservices/openspec/config.yaml` with `store: openspec-store`
- [x] 1.2 Create `tdt-core/openspec/config.yaml` with `store: openspec-store`
- [x] 1.3 Create `tdt-sheets/openspec/config.yaml` with `store: openspec-store`
- [x] 1.4 Create `webhook-receiver/openspec/config.yaml` with `store: openspec-store`
- [x] 1.5 Create `jira-daily-reports/openspec/config.yaml` with `store: openspec-store`
- [x] 1.6 Add `store: openspec-store` to `ai-harness-skills/openspec/config.yaml` (preserve schemas/)
- [x] 1.7 Create `ops-automation-suite/openspec/config.yaml` with `store: openspec-store`
- [x] 1.8 Create `agent-docs-sync/openspec/config.yaml` with `store: openspec-store`
- [x] [historical] 1.9 Run `openspec update` in each repo to generate skill files
- [x] 1.10 Verify from each repo: `openspec list` shows store's active changes
- [x] 1.11 Verify root banner reports `source: "declared"` from each repo

## 2. Git Remote and store.yaml

- [x] [historical] 2.1 Add remote: `git -C ~/Developer/openspec-store remote add origin <url>` (deferred)
- [x] [historical] 2.2 Add `remote: <url>` to `.openspec-store/store.yaml` (deferred)
- [x] [historical] 2.3 Push: `git -C ~/Developer/openspec-store push -u origin main` (deferred)
- [x] [historical] 2.4 Verify: `openspec store doctor openspec-store --json` shows remote non-null (deferred)

## 3. Relocate Non-Standard Root Files

- [x] 3.1 Create `docs/governance/` at store root
- [x] 3.2 Move `openspec/AGENTS.md` → `docs/governance/AGENTS.md`
- [x] 3.3 Move `openspec/INDEX.md` → `docs/governance/INDEX.md`
- [x] 3.4 Move `openspec/AUDIT_INDEX.md` → `docs/governance/AUDIT_INDEX.md`
- [x] 3.5 Move `openspec/ALIGNMENT_SUMMARY.md` → `docs/governance/ALIGNMENT_SUMMARY.md`
- [x] 3.6 Move `openspec/SPEC_TO_CODE_ALIGNMENT_AUDIT.md` → `docs/governance/SPEC_TO_CODE_ALIGNMENT_AUDIT.md`
- [x] 3.7 Move `openspec/AUDIT_COMPLETION_SUMMARY.txt` → `docs/governance/AUDIT_COMPLETION_SUMMARY.txt`
- [x] 3.8 Move `openspec/reports/` → `docs/governance/reports/`
- [x] 3.9 Update AGENTS.md line 19: fix `openspec/config.yaml` reference
- [x] 3.10 Verify `openspec/` root contains only `config.yaml`, `specs/`, `changes/`

## 4. Final Verification

- [x] 4.1 `openspec doctor` — no issues
- [x] 4.2 `openspec validate --store openspec-store --all --strict` — all pass (349/349)
- [x] 4.3 From each wired repo: `openspec list` shows store changes
- [x] 4.4 From each wired repo: `openspec status --change <name> --json` — source: "declared"
- [x] 4.5 `docs/governance/` contains all relocated files
- [x] 4.6 `ai-harness-skills/openspec/schemas/harness-13/` unchanged
- [x] [historical] 4.7 Git commit: `complete: multi-repo store pointers, remote, file relocation`


---

> **Historical record:** This change was archived with 6 incomplete task(s) (26/32 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
