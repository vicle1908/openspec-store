# Tasks: Docker Compose Stack Stability

- [x] 1. Reproduce the local verification issues and capture exact logs.
- [x] 2. Confirm effective GitHub job permissions and GHCR selective failure scope.
- [x] 3. Remove the catalog Redis host-port collision.
- [x] 4. Add/retain Compose model regression assertions for Redis and one-shot
      initializer behavior.
- [x] 5. Add OTel dependency-ordering changes, run the focused shipping test,
      and revert the hard dependency when the focused topology proved not to
      include `otel-collector`.
- [x] 6. Run `make compose-validate`, collector validation, and diff checks.
- [x] 7. Push the fix branch and create PR #33.
- [x] 8. Re-run real GitHub checks after the focused-test correction.
- [ ] 9. Merge PR #33 after all required checks pass.
- [ ] 10. Verify the merged main branch with a fresh full stack and update the
       operational evidence manifest.
- [ ] 11. Archive this OpenSpec change and validate the complete store.

## Evidence

- Initial PR #33 shipping-focused failure: `no such service: otel-collector`.
- Corrected PR #33 shipping-focused rerun: passing.
- Corrected PR #33 service-integration: passing.
- Corrected PR #33 Gitleaks and deployment validation: passing.
