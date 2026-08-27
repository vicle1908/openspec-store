# Design — Versioned Drive Publication and Sync-Up

## Source contract

- Source repository: `/Users/androidteam/Developer/ntu-keynote`
- Source branch: `main`
- Source commit: `72cf4aa2db7e6d1e3f5e99fb8ba157e0038ac742`
- Package digest: `3f299c8763409b4030a2f48d3c6cec1ad7b1d1b3e92b172552918d045ff7d030`
- Public files: exactly the seven paths in `evidence/venue-package-allowlist.json`

## Destination layout

```text
gdrive-tdt:NTU AI Keynote/
└── bb7a4d58a735-3f299c876340/
    ├── README.md
    ├── index.html
    ├── keynote-fallback.pdf
    └── assets/
        ├── ntu-logo.png
        └── fonts/
            ├── be-vietnam-pro-400.woff2
            ├── be-vietnam-pro-600.woff2
            └── be-vietnam-pro-800.woff2
```

The folder name uses the first 12 characters of the committed SHA and first 12 characters of the canonical package digest. A subsequent source commit produces a separate child path; no remote version is overwritten.

## Sync-up mechanism

`~/Developer/ntu-keynote/scripts/sync-to-gdrive.sh` SHALL:

1. Resolve its repository root from the script location.
2. Require `git rev-parse --show-toplevel` and a committed HEAD.
3. Reject a dirty worktree by default; `--allow-dirty` is not supported in the first version.
4. Verify all seven allowlisted source files exist.
5. Read the canonical digest from `evidence/release-manifest.json` and verify it is a 64-character lowercase SHA-256.
6. Create the root folder with `rclone mkdir`.
7. Run `rclone copy` from the repository root to the versioned child path with `--files-from-raw`, `--checksum`, and `--immutable`.
8. Never call `rclone sync`, `rclone delete`, `rclone purge`, or Drive permission commands.
9. Read back the remote listing with `rclone lsjson --recursive`, confirm exactly seven relative paths, and compare remote sizes with local sizes.
10. Print a redacted summary containing remote path, source commit, digest prefix, file count, and verification result.

`--dry-run` performs all local validation and displays the planned copy without mutating Drive. `--remote` and `--folder` may override the defaults only when supplied explicitly; the default remains `gdrive-tdt` and `NTU AI Keynote`.

## Conflict policy

- Existing exact version path with identical files: idempotent success.
- Existing exact version path with differing files: fail closed through `--immutable`.
- Existing unrelated root/child folders: preserve.
- Remote files not in the current version folder: preserve.

## Verification

The upload verifier compares the seven local files against the seven remote objects by relative path and byte size. Because rclone's remote listing does not provide a portable SHA-256 for every Drive object, the local canonical digest plus exact remote object sizes and count are recorded. If a remote checksum is available, the script reports it but does not substitute an MD5/Drive hash for the canonical package digest.

## Rollback

The operation has no destructive rollback: remove nothing. If a bad package is uploaded, leave the versioned object for audit and publish a corrected source commit to a new versioned path. Any manual Drive deletion is outside this change and requires separate user authorization.

## Credential boundary

The script reads the configured rclone remote by name. It never reads, prints, or writes OAuth tokens, client secrets, access tokens, or rclone config contents. gws remains a separate currently revoked OAuth path and is not modified by this change.
