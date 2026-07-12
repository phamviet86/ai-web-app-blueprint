---
template_id: SKEL-TPL-DATA-MIGRATION
template_version: 1.0.0
produces: migration-plan
owner_guide: ../12-data-lifecycle-migrations-and-recovery.md
use_when: Changing schema, ownership, representation, retention, or moving/backfilling data.
---

# Data migration plan: [change]

> Instantiate with schema `1.0` from [README.md](README.md).

- Owner / reviewers / change window:
- Source of truth and affected consumers:
- Data classification / volume / growth:
- Required compatibility window:
- RPO/RTO and rollback limit:

## Phases

| Phase | App/schema behavior | Deploy order | Verification | Abort/next gate |
| --- | --- | --- | --- | --- |
| Expand | Backward-compatible structure/contracts | | | |
| Backfill | Idempotent/resumable batches | | | |
| Compare | Counts/checksums/domain invariants/shadow reads | | | |
| Switch | Read/write authority cutover | | | |
| Contract | Remove old path after compatibility proof | | | |

## Backfill contract

- Stable cursor/checkpoint:
- Batch/concurrency/rate limit:
- Idempotency and retry:
- Handling concurrent writes:
- Progress/lag/failure telemetry:
- Reconciliation and deletion/privacy propagation:

## Production migration safety

- Affected rows/bytes, table/index size, and expected duration:
- Lock level/duration and blocking risk:
- Transaction boundary and transaction-log/WAL impact:
- Rewrite, validation scan, index-build, and constraint behavior:
- Replication, disk, connection-pool, and resource impact:
- Statement/lock timeouts and safe retry behavior:
- Live monitoring, pause/abort criteria, and decision owner:
- Representative-shape rehearsal and pre/post invariants:

## Recovery

- Application rollback/roll-forward:
- Data restoration or compensating correction:
- Evidence required before destructive contract phase:
