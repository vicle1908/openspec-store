# disk-reclaim-2026-09

Reclaim stale disk resources: orphaned Docker anonymous volumes, unused/rebuildable Docker images, stale build cache, and Go module cache. Preserves data volumes, rollback images, and active services.

## Result (2026-09-05)

Executed via OpenSpec workflow (skip_specs: true — operational cleanup).

| Metric | Before | After |
| --- | --- | --- |
| Data volume free space | 49 GiB | 70 GiB (+21 GiB) |
| Docker.raw actual size | 33 G | 13 G |
| Docker images | 25 (20.09GB, 14.65GB reclaimable) | 5 (6.37GB — active + rollback + redis target) |
| Docker volumes | 60 (50 anonymous orphans) | 10 (all named, 2 active, 8 tdt experiment data) |
| Build cache | 10.7GB | 34MB |
| Go module cache | 1.2 GiB | 0 |

Reclaim breakdown: 2.107GB anonymous volumes + ~13.7GB images (149 untag/delete
ops) + 10.66GB build cache + 1.2GiB go modcache ≈ 27.7GB inside Docker/Go
(net host free-space delta +21GiB, remainder is sparse-file accounting).

Two research corrections caught by in-flight verification:

1. `redis:7-alpine` was kept (not removed as originally listed) — the ACTIVE
   omniroute-redis container runs on redis:7-alpine, not 8.10.1.
2. The "dangling diegosouzapw/omniroute" image and `omniroute:rollback-3.8.49-*`
   are the SAME image (sha256:4205701…) — nothing extra to delete; rollback
   capability preserved per update.sh convention.

Verification gates: 3/3 containers healthy; OmniRoute /v1/models → 401
(documented healthy signature); 10/10 named volumes preserved; rollback image
present; free-space delta 21GiB ≥ 15GiB gate.

Owner-decision items surfaced, NOT actioned (see design.md Non-Goals):
`~/jenkins_home` (1.8GiB, untouched since Oct 2025) and
`/Library/Developer/CoreSimulator` (11GiB iOS simulator runtimes).
