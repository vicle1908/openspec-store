# Publish NTU Keynote to Google Drive

## Why

The latest NTU keynote is complete and committed in `~/Developer/ntu-keynote` at `72cf4aa2db7e6d1e3f5e99fb8ba157e0038ac742`. The public package needs a durable Drive copy for access and handoff, together with a repeatable sync-up command that does not delete or overwrite unrelated Drive content.

Hermes-managed Google OAuth/gws access is currently revoked (`invalid_grant`), but the configured `gdrive-tdt` rclone remote has working read access. The publication will therefore use the already configured rclone remote, with no credential changes or credential values written to the repository.

## What Changes

- Create a Drive folder `NTU AI Keynote` if it does not already exist.
- Upload exactly the seven public package files, not evidence, tests, scripts, Git metadata, OpenSpec files, or worktree data.
- Store the upload in an immutable versioned child path named from the committed source SHA and canonical package digest prefix.
- Add a repository script `scripts/sync-to-gdrive.sh` that performs a one-way, versioned sync-up using `rclone copy`, explicit public-file allowlisting, checksum comparison, and post-copy read-back.
- Support `--dry-run` for safe preview and reject dirty source worktrees unless explicitly overridden.
- Record the Drive destination path, source commit, package digest, file count, and verification result in the central acceptance evidence for this change.

## Scope and Ownership

- Implementation owner: `~/Developer/ntu-keynote`.
- Planning/acceptance owner: `~/Developer/openspec-store`.
- Drive destination owner: the authenticated `gdrive-tdt` remote; no sharing permissions are changed.
- The script owns only versioned child paths under `gdrive-tdt:NTU AI Keynote/`; it never deletes remote files and never modifies the prior keynote OpenSpec change.

## Safety

- No credentials, OAuth tokens, or remote configuration values are committed.
- `rclone copy` is used instead of `rclone sync` so the mechanism cannot delete remote files.
- `--immutable` is used for version folders so an existing same-name remote object cannot be silently replaced with different bytes.
- The public seven-file allowlist is explicit and verified before upload.
- The destination is a versioned folder derived from a committed SHA and digest, making reruns idempotent.

## Acceptance

The change is accepted only when:

1. rclone read access and the destination folder are verified.
2. The seven-file package is uploaded to the versioned destination.
3. Remote read-back confirms names, sizes, and SHA-256 values.
4. A dry-run of `scripts/sync-to-gdrive.sh` reports no unintended files and no deletion plan.
5. The central OpenSpec change records exact source/destination identities and the gws OAuth limitation.

Creation of a Drive folder and upload are external side effects explicitly requested by the user. No public sharing is performed.

## Non-Goals

- Re-authorizing gws/OAuth.
- Sharing the folder or files.
- Deleting or replacing existing Drive files.
- Bidirectional synchronization or remote-to-local overwrite.
- Uploading private evidence or OpenSpec planning files.
- Creating a release tag or archiving the keynote changes.
