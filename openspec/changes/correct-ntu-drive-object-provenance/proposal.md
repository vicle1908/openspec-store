# Correct NTU Drive Object Provenance

## Why

The post-archive consistency audit of the three completed NTU keynote changes found one provenance error and one documentation drift:

1. The archived `enhance-ntu-keynote-visual-storytelling` verification record (`acceptance/verification.json`, JSON path `drive_publication.remote_objects[4].id`) lists a stale Google Drive object ID for `assets/ntu-logo.png`: `1Q3sC13sq-jhYjhl85Y2TZPkW1Fn36J2v`. That ID belongs to the intermediate worktree upload into `gdrive-tdt:NTU AI Keynote/b0b44ffcd53f-795d4f53c317`, which was superseded by the final main-integrated publication into `gdrive-tdt:NTU AI Keynote/a7f24085935a-795d4f53c317`. The authoritative logo object ID in the final destination is `1jdZDPNUlHcLigpCWr4rNJSDXfwCeli5n`, confirmed by a fresh Drive read-back.
2. `ntu-keynote/docs/drive-sync.md` still references the pre-archive active change path `publish-ntu-keynote-to-google-drive`, which no longer exists as an active change.

## What Changes

- Add an immutable correction record under this change's acceptance evidence. It supersedes the stale object ID by documentation, citing the exact archived file, JSON path, stale value, authoritative replacement, and fresh read-back evidence. The archived record itself is NOT mutated.
- Update `ntu-keynote/docs/drive-sync.md` to reference the archived change path and the completed publication state.
- No spec changes (documentation/provenance correction only): `skip_specs: true`.
- No public package changes: `README.md`, `index.html`, `keynote-fallback.pdf`, and assets remain byte-identical; no Tier-1 evidence refresh is required. `docs/` is not in the public seven-file package or `checksums.sha256`.

## Impact

- Affected specs: none
- Affected code: `ntu-keynote/docs/drive-sync.md` only (private, not published)
- Archived evidence: read-only, preserved intact per the immutability policy
