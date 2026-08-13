# Tasks: set-omp-default-giaoduc-and-sync-runtime-docs

Documentation sync: correct stale claims in three main specs. No live configuration changes.

## 1. Ground-truth verification

- [x] 1.1 Live role map verified: `default: giaoduc/Advance`, `smol: shopapikey/fable-5`, `slow: cockpit/gpt-5.6-luna:max`, `plan: cockpit/gpt-5.6-luna:max`, `commit: shopapikey/fable-5`, `task: giaoduc/Advance`
- [x] 1.2 `models.yml` hash unchanged: `747167245051c2fe546636b98beb112a`
- [x] 1.3 `config.yml` hash unchanged: `00539e9fa8b643768fe927e158eba229`
- [x] 1.4 All three context windows at 1,000,000 confirmed
- [x] 1.5 Homebrew-only resolution: `/opt/homebrew/bin/omp` v17.3.0
- [x] 1.6 Native Cockpit endpoint: `http://localhost:51006/v1`, `openai-responses`

## 2. Fresh-shell acceptance

- [x] 2.1 Default role (`giaoduc/Advance`): pong, exit 0
- [x] 2.2 `shopapikey/fable-5`: pong, exit 0
- [x] 2.3 `cockpit/gpt-5.6-luna:high`: pong, exit 0
- [x] 2.4 `cockpit/gpt-5.6-luna:max`: pong, exit 0

## 3. Main-spec Purpose corrections

- [x] 3.1 `omp-provider-routing` Purpose: updated (was TBD)
- [x] 3.2 `omp-fresh-shell-contract` Purpose: updated (was TBD)
- [x] 3.3 `omp-installation-management` Purpose: updated (removed pinned v17.2.15)
- [x] 3.4 `coding-agent-credential-loading` Purpose: updated (was TBD)

## 4. Delta spec corrections

- [x] 4.1 `omp-fresh-shell-contract`: REMOVED Cockpit default + ADDED Giaoduc default
- [x] 4.2 `omp-provider-routing`: MODIFIED role-allocation scenarios (Giaoduc default + task)
- [x] 4.3 `omp-installation-management`: MODIFIED with dynamic version scenario

## 5. Closeout

- [x] 5.1 Strict validation passed
- [x] 5.2 Historical archives left untouched
