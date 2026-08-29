## 1. Correct model references

- [x] 1.1 Replace every stale Phanmemvip and Cockpit model reference in the canonical fresh-shell contract with the exact registered catalog IDs; verify no stale identifiers remain.
- [x] 1.2 Preserve all requirement and scenario names while changing only provider/model identifiers; verify strict OpenSpec delta validation.

## 2. Verify without runtime mutation

- [x] 2.1 Confirm the exact registered IDs are present in the read-only OMP catalog; do not modify `~/.omp/agent/config.yml` or `models.yml`.
- [x] 2.2 Run clean `zsh -c` and `zsh -lc` presence/length checks without printing credentials.
- [x] 2.3 Do not run live Phanmemvip inference while the retained exposed key remains security-blocked.

## 3. Review and delivery

- [x] 3.1 Run strict OpenSpec validation, confirm the runtime `:xhigh` versus canonical `:max` drift is documented/deferred, and review the scoped diff for unintended configuration or credential changes.
