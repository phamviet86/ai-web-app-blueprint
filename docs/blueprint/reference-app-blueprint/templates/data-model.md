---
template_id: REFAPP-TPL-DATA-MODEL
template_version: 1.0.0
produces: data-model
owner_guide: ../03-database-blueprint.md
use_when: Mapping the tier-selected FulfillOps slice or substitute domain into the selected database/ORM.
---

# Reference application data model

## Artifact control

Instantiate through [schema mapping](README.md) as `artifact_type: data-model`; replace this definition frontmatter with schema `1.0` instance frontmatter. The fields below must agree with it.

- Artifact ID: `DATA-*`
- Status: `draft` / `in-review` / `accepted` / `superseded` / `rejected`
- Owner / reviewer / decision date:
- Revision / supersedes / superseded by:
- Refresh or invalidation trigger:
- Upstream IDs: optional `PRESET-*`, `SYS-*`, `STACK-*`, `COVERAGE-*`
- Selected `CAP-*` / owning `MOD-*` scope:

- Stack profile:
- Tenant/isolation strategy:
- ID/time/money/status/version conventions:
- Migration/backup/restore policy links:

| `DATA-*` table/projection | Single write/schema owner | Purpose/grain | Key fields | PK/FK/unique/check/index | Classification/retention | Source/freshness |
| --- | --- | --- | --- | --- | --- | --- |

## Relationships and invariants

| Invariant | Enforcement | Transaction/concurrency policy | Planned/result `EVID-*` |
| --- | --- | --- | --- |

## Dynamic query contract

| Public alias | Value type | Search/filter/sort/range | Allowed operators | Column/relation/join expression | Mandatory access scope | Projection/index/budget | `EVID-*` |
| --- | --- | --- | --- | --- | --- | --- | --- |

Unknown aliases/operators and invalid values are rejected rather than ignored. Record stable tie-breaker, maximum page/range size, total/count policy and canonical query identity.

## Surface query and result shapes

| Surface | Request parts | Page/cursor/range result | Stable ordering | `as_of`/freshness | Empty/error/degraded contract |
| --- | --- | --- | --- | --- | --- |

## Join, view, and calculated reads

| Read contract | Join / view / materialized view / projection | Source authority | Calculated filter/sort/page semantics | Freshness/rebuild/compare | Query-plan `EVID-*` |
| --- | --- | --- | --- | --- | --- |

## Lifecycle and isolation

| Dataset/copy | Authority | Tenant/environment isolation | Retention/deletion/export | Backup/restore |
| --- | --- | --- | --- | --- |

## Durable work and integrations

| Flow | Idempotency | Outbox/inbox/job state | Webhook/provider state | Reconciliation |
| --- | --- | --- | --- | --- |

## Seed/fixture scenarios

| Scenario/persona | Required records/state | Deterministic assertion | Reset/cleanup |
| --- | --- | --- | --- |

## Migration sequence

| Phase | Schema/app compatibility | Data/backfill/compare | Abort/recovery | `EVID-*` / status |
| --- | --- | --- | --- | --- |
