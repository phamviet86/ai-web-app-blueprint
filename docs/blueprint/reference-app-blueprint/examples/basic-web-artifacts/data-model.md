---
artifact_id: DATA-READING-001
artifact_type: data-model
schema_version: "1.0"
artifact_version: 1
title: Logical Reading List data model
status: accepted
owner: example-books-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - module:books
source_template: REFAPP-TPL-DATA-MODEL@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List logical data model

> Accepted logical design. No migration, query plan, transaction, restore, or runtime result has been observed.

## Artifact control

- Upstream IDs: `SYS-READING-001`, `STACK-READING-001`, `COVERAGE-READING-001`.
- Selected capabilities/modules: `CAP-CRUD`, `CAP-QUERY`; `MOD-BOOKS`.
- Stack mapping: Django ORM adapter over PostgreSQL; exact driver remains unresolved in `STACK-READING-001`.
- Isolation: guarded local/test database only; no tenant scope.

| Data ID | Write owner | Purpose/grain | Key fields | Constraints/index | Classification/retention | Source/freshness |
| --- | --- | --- | --- | --- | --- | --- |
| `DATA-BOOKS` | `MOD-BOOKS` | One book record | Opaque ID, title, author, status, version, timestamps | Nonblank title/author; bounded status; optimistic version; normalized title/author index | Public synthetic; active/archived; resettable local data | Authoritative row; current transaction |

## Relationships and invariants

| Invariant | Enforcement | Transaction/concurrency policy | Evidence |
| --- | --- | --- | --- |
| Title and author are nonblank after normalization | Boundary/application validation plus database nonblank constraint | One command transaction | `EVID-APP-001`, `EVID-DB-001` `PLANNED` |
| Archived book is not editable without a future restore command | Application rule | Expected version check | `EVID-APP-001` `PLANNED` |
| Concurrent update cannot silently overwrite | Version column and conditional update | One bounded `transaction.atomic()` | `EVID-DB-001` `PLANNED` |

## Lifecycle and isolation

| Dataset/copy | Authority | Isolation | Retention/deletion/export | Backup/restore |
| --- | --- | --- | --- | --- |
| Local books | `DATA-BOOKS` | Dedicated guarded database | Archive only in product contract; reset entire example database | Recreate from migrations/seed; no production backup claim |
| Test books | Per-test fixture | Isolated test database/transaction | Reset after test | Deterministic fixture recreation |
| Logs | Not a book copy | Local process output | No payload/title/author logging | No recovery role |

## Durable work and integrations

No durable job, outbox, inbox, webhook, provider, file, cache, projection, or reconciliation store is selected. Adding one requires a new capability and data-contract revision.

## Seed scenarios

| Scenario | Records/state | Deterministic assertion | Reset |
| --- | --- | --- | --- |
| Active and archived search | Five synthetic books across both statuses | Stable title/ID order; active filter excludes archived | Guarded seed command is idempotent or recreates local database |
| Concurrent edit fixture | One active book at known version | Stale version returns conflict | Test transaction/reset |

## Migration sequence

| Phase | Schema/app compatibility | Data/backfill/compare | Abort/recovery | Evidence |
| --- | --- | --- | --- | --- |
| Initial expand | Create book table/index before serving | Deterministic seed only | Drop/recreate local example database | `EVID-MIG-001` `PLANNED` |
| Future changes | Expand -> backfill -> compare -> switch -> contract | Not yet selected | New reviewed plan required | No observed evidence |
