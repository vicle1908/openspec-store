# Ecosystem index freshness verification evidence

Date: 2026-08-15
Change: `ecosystem-index-freshness-automation`

## Provider evidence

- GitNexus: `1.6.9`
- Graphify upstream: `https://github.com/Graphify-Labs/graphify`
- Graphify package: `graphifyy[all,postgres]==0.9.42`
- Graphify CLI: `graphify 0.9.42`
- Graphify Python: `Python 3.12.13`
- OpenSpec CLI: `1.9.0`
- Inventory SHA-256: `d01a8bce9c7247571961ffc31183440997f75f52820043d4a05baed2431bf90b`

No credentials, API keys, or credential-bearing URLs are included in this artifact.

## Functional evidence

- Disposable refresh guard fixture: path escape rejected; unlisted repository emitted `skipped_unlisted` without provider execution.
- Disposable dirty/merge fixture: dirty repository emitted `skipped_dirty`; merge-state repository emitted `skipped_merge_state`.
- Live-owner lock fixture: canonical path-derived lock emitted `lock_busy` and did not steal the live PID.
- Dead-owner lock fixture: dead PID lock was reclaimed and removed after refresh.
- GitNexus wrapper fixture: root-relative `gitnexus analyze . --index-only --default-branch main` completed with the local `nomic-embed-text` 768-dimensional endpoint; indexed SHA was verified.
- Superseded fixture: a commit made during analysis emitted `superseded` with the pre/post HEAD transition.
- Graphify fixture: `graphify update` completed; corrupt graph repair completed through isolated `graphify extract . --code-only --out <temporary-output>` and restored valid JSON.
- Watcher fixture: active `graphify watch <root>` emitted `watcher_active` and skipped scheduled refresh.
- Hook installer: 19/19 approved repositories processed; second run reported `Updated: 0`, `Errors: 0`; all hooks have exactly one managed block and pass `bash -n`.
- Status JSON: valid JSON, 19 unique inventory repositories, provider versions, inventory digest, indexed/current SHA fields, and lock-owner fields.
- LaunchAgent: `plutil -lint` passed; `launchctl print` showed loaded service; three kickstarts completed with `last exit code = 0`.

## Known limitation

`post-merge` covers local merge and merge-pull operations only. It does not run for remote GitHub PR merges or `git pull --rebase`. Dirty repositories and active Graphify watchers are intentionally skipped by the central refresh.
