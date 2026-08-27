# Implementation Tasks

- [ ] 1.1 Obtain approved NBS logo asset with verified provenance. **Evidence:** asset file in `assets/nbs-logo.png` (or `.svg`), provenance record in `evidence/source-inspection.json` or equivalent with source URL, retrieval date, dimensions, alpha, SHA-256, and provenance classification. **Depends on:** none (blocked on user providing the asset or confirming an official source). **Verify:** provenance record exists; classification is not `unknown`; file parses as valid image.

- [ ] 1.2 Freeze the pre-implementation baseline. **Evidence:** `acceptance/nbs-baseline.json` — current main HEAD (`97a0236...`), current package digest (`8a96ed4f...`), per-file SHA-256 for all seven current public files, clean worktree status. **Depends on:** 1.1. **Verify:** baseline file exists; digest matches current manifest; worktree is clean.

- [ ] 2.1 Create an isolated worktree (`feat/nbs-co-branding`) from main. **Evidence:** `git worktree add` command output; branch exists; worktree status clean. **Depends on:** 1.2. **Verify:** separate worktree; main untouched.

- [ ] 2.2 Record the NBS asset in the evidence register. **Evidence:** `evidence/assets.json` gains an entry for `assets/nbs-logo.png` with `media_type`, `format`, `size_bytes`, `sha256`, `width`, `height`, `has_alpha`, `verification_status: "passed"`. **Depends on:** 2.1. **Verify:** asset entry present; hash matches file on disk.

- [ ] 2.3 Update the venue-package allowlist to include the NBS asset. **Evidence:** `evidence/venue-package-allowlist.json` `include` array gains `assets/nbs-logo.png` (or the full assets directory is already included via `assets/`). **Depends on:** 2.1. **Verify:** allowlist includes the file; `tests/test_wave9_manifest_and_neutral_gate.py` still passes.

- [ ] 2.4 Implement the brand lockup in `index.html`. **Changes:** (a) Expand `.brand-layer` CSS: width auto/max 340px, flex row, align-items center; (b) Add `.brand-divider` CSS; (c) Reduce NTU img width to 140px, set max-height 48px for NBS img; (d) Update HTML: add divider `<span>` and NBS `<img>` with `data-brand-asset="nbs-logo"`, Vietnamese alt text; (e) Add `role="group"` and `aria-label` to `.brand-layer`. **Depends on:** 2.3. **Verify:** structural assertions (exactly 2 brand-asset images, 1 divider); no external URLs in brand-layer; no content/timing changes.

- [ ] 2.5 Add focused automated tests. **Tests:** exactly 1 NTU + 1 NBS logo in `.brand-layer`; local `assets/` paths only; Vietnamese alt text present; no external URLs in `.brand-layer`; safe-area bounds (top+height ≤ 144px, left ≥ 64px, right ≤ 1216px); NTU rendered width ≥ NBS rendered width; no overlap with slide-1 title area; all 17 slides present; full/short routes unchanged; timing unchanged. **Depends on:** 2.4. **Verify:** new tests pass; full suite green.

- [ ] 3.1 Run browser qualification. **Evidence:** Chrome computed styles at 1280×720 for lockup; viewport checks at 1920×1080, 1440×900, 1366×768, 1024×768 with `overflow: false`; print media check confirms lockup visible. **Depends on:** 2.5. **Verify:** all viewports pass; no clipping; no console errors.

- [ ] 3.2 Regenerate `keynote-fallback.pdf` and rebind `evidence/pdf-binding.json`. **Evidence:** PDF has 17 pages; page 1 shows both logos; binding hashes match new candidate files; generation base commit matches. **Depends on:** 3.1. **Verify:** pdfinfo shows 17 pages; pdftotext confirms Vietnamese glyphs; binding round-trips.

- [ ] 3.3 Recompute package digest, per-file SHA-256, checksums, and release manifest. **Evidence:** digest differs from `8a96ed4f...`; `checksums.sha256` has all entries passing; manifest carries new digest, new file list, `status: blocked-automated`, human gates open. **Depends on:** 3.2. **Verify:** `shasum -a 256 -c checksums.sha256` exits 0; manifest non-self-referential.

- [ ] 4.1 Create acceptance artifacts under `acceptance/`: intake.json (new candidate identity, new digest, NBS asset provenance summary), verification.json (per-requirement evidence). **Depends on:** 3.3. **Verify:** intake digest matches manifest; all requirement rows have evidence.

- [ ] 4.2 Upload new package to Drive. **Evidence:** `scripts/sync-to-gdrive.sh` output; new version folder created; prior version folder untouched; read-back passes. **Depends on:** 4.1. **Verify:** new version path differs from `97a0236259d8-8a96ed4f9614`; prior folder still present.

- [ ] 5.1 Final validation battery. **Checks:** strict OpenSpec validation; full test suite (green); static verifier 11/11; checksums 75+/75+; stale-token sweep (no `NVIDIA`, no stale digest); store doctor clean. **Depends on:** 4.2. **Verify:** all exit codes 0.

- [ ] 5.2 Integrate to main. **Evidence:** fast-forward merge; main clean; worktree and branch removed; central store ledger updated; unrelated dirty paths preserved. Human gates remain OPEN (brand/editorial approval, Safari, venue rehearsal, release decision). No tag, no archive. **Depends on:** 5.1. **Verify:** main at merged HEAD; full suite passes on main; manifest status blocked-automated.
