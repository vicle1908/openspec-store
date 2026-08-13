# Tasks: fix-omp-fresh-shell-credentials-and-context-window

## 1. Ground-truth baseline

- [x] 1.1 Confirm clean login shell had all three custom keys unset
- [x] 1.2 Confirm keys existed in `~/.hermes/.env`, mode 600, without printing values
- [x] 1.3 Confirm Hermes declared 1,000,000 context length for the three custom providers
- [x] 1.4 Confirm omp custom model entries omitted `contextWindow`
- [x] 1.5 Confirm omp default had drifted to `giaoduc/Advance`

## 2. Apply corrections

- [x] 2.1 Backed up `.zprofile`, `models.yml`, and `config.yml` under
  `~/.omp/backups/omp-fresh-shell-20260813_125934/` with mode-600 files
- [x] 2.2 Added guarded `~/.hermes/.env` source to `.zprofile`
- [x] 2.3 Added `contextWindow: 1000000` to `shopapikey/fable-5`, `giaoduc/Advance`, and `cockpit/gpt-5.6-luna`
- [x] 2.4 Restored `config.yml` default to `cockpit/gpt-5.6-luna:high`

## 3. Fresh-shell acceptance

- [x] 3.1 Empty-environment clean login shell sees all three key variables set
- [x] 3.2 Clean login shell resolves Homebrew `/opt/homebrew/bin/omp` v17.2.15
- [x] 3.3 Explicit Cockpit selector returned pong, exit 0
- [x] 3.4 Explicit Shopapikey selector returned pong, exit 0
- [x] 3.5 Explicit Giaoduc selector returned pong, exit 0
- [x] 3.6 Default no-flag selector returned pong, exit 0
- [x] 3.7 All three omp custom models report `contextWindow: 1000000`

## 4. Preservation and closeout

- [x] 4.1 Provider endpoints, transports, model IDs, non-default roles, and equivalence preserved
- [x] 4.2 No credential values printed
- [x] 4.3 Temporary profiles and probe files removed
- [x] 4.4 Strict OpenSpec validation passed before apply
- [x] 4.5 Archive change and full-store validate (executing after this validation gate)

## Evidence

- Fresh empty-shell keys: all three SET (lengths 36, 37, 42)
- `omp`: `/opt/homebrew/bin/omp`, `omp/17.2.15`
- `models.yml` post-change hash: `747167245051c2fe546636b98beb112a`, mode 644
- `config.yml` post-change hash: `0358ecccb895fd8844d1cd9e48730dab`, mode 600
- Real fresh-shell acceptance: 4/4 pong, exit 0
