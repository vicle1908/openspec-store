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
- [x] 12. Resolve current kind, Kubernetes/kubectl, kubeconform, and External
       Secrets releases from upstream APIs.
- [x] 13. Update tool pins, kind node digest, External Secrets immutable CRD URL
       and checksum, validator fixture, and operator documentation.
- [x] 14. Install the updated toolchain with the checksum-verifying repository
       installer and pass preflight using the repo-local tool directory.
- [ ] 15. Create the toolchain upgrade PR and require every executed PR check to
       pass before merge.
- [x] 16. Diagnose the toolchain PR Gitleaks failure as an immutable CRD checksum
       false positive and add a narrow expiring fingerprint waiver.
- [x] 17. Diagnose shipping-focused evidence showing two concurrent `201`
       responses and no in-progress code.
- [x] 18. Add a bounded focused stub delay and unit regression test.
- [ ] 19. Pass the real focused Shipping cohort and all remaining PR checks on
       the corrected commit.

## Evidence

- Initial PR #33 shipping-focused failure: `no such service: otel-collector`.
- Corrected PR #33 shipping-focused rerun: passing.
- Corrected PR #33 service-integration: passing.
- Corrected PR #33 Gitleaks and deployment validation: passing.
