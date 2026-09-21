# Tasks: migrate-remaining-vds-icloud-projects

## 1. Inventory & Staged Migration Planning

- [ ] 1.1 Perform shallow inventory of `project/vds/` to catalogue sibling projects and root assets
- [ ] 1.2 Prioritize migration order based on project size and dataless status

## 2. Project-by-Project Migration & Hydration

- [ ] 2.1 Migrate and verify `EKYC-project`
- [ ] 2.2 Migrate and verify `SAVING-project`
- [ ] 2.3 Migrate and verify `LIB-project`
- [ ] 2.4 Migrate and verify `DOPS-project`
- [ ] 2.5 Migrate and verify `PAR-project`
- [ ] 2.6 Migrate and verify `LEP-project`
- [ ] 2.7 Migrate and verify `INSURANCE-project`
- [ ] 2.8 Migrate and verify root scripts, docs, and shared assets into `vds-root-assets/`

## 3. Quarantine & Permission Hardening

- [ ] 3.1 Audit sensitive quarantine across all migrated projects (`0700` dirs / `0600` files)

## 4. Final Verification & Gated Deletion

- [ ] 4.1 Perform two-way reconciliation audit across all sibling projects
- [ ] 4.2 Safely unlink verified files and prune empty directories from iCloud Drive
- [ ] 4.3 Validate final destination integrity and archive OpenSpec change
