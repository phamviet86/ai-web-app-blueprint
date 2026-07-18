---
guide_id: SKEL-DATA-LIFECYCLE
title: Data Lifecycle, Migrations, and Recovery
status: experimental
audience: human-and-ai
read_when:
  - Designing or changing schemas, storage, data classification, retention, deletion, tenant isolation, migrations, backfills, backups, or disaster recovery.
  - Establishing production data-safety requirements for a new repository.
skip_when:
  - The change preserves every stored-data shape, lifecycle, access boundary, and recovery contract.
depends_on:
  - README.md
owns:
  - data inventory and classification
  - retention and deletion lifecycle
  - storage and environment isolation
  - task-scoped data-access modes and mutation guards
  - schema migration and backfill safety
  - recovery objectives, backups, and restore drills
  - proportionate multi-store failover, fencing, and failback
---

# Data lifecycle, migrations, and recovery

> Core rule: data safety spans collection through verified disposal and recovery. A backup file, generated migration, or successful command is not evidence that the system can preserve or restore the required business state.

## Rule `DATA-INVENTORY-01`: every authoritative or sensitive data set has an owner

Maintain an inventory for databases, object stores, caches, search indexes, queues, analytics, logs, audit stores, backups, exports, and vendor-held copies.

For each data set, record:

- business owner and technical owner;
- authoritative source and derived copies;
- purpose and critical business invariants;
- subjects/tenants and isolation key;
- classification and sensitive fields;
- producers, consumers, integrations, and locations;
- retention, deletion, backup, and recovery expectations;
- acceptable staleness and reconciliation source.

An architecture diagram may summarize flows, but the inventory must identify where a lifecycle action or incident response actually needs to operate.

## Rule `DATA-CLASSIFICATION-01`: handling follows sensitivity and criticality

Use a small repository-defined classification model such as public, internal, confidential, and restricted. Add regulated categories only when applicable.

Classification determines at least:

- allowed identities, services, and environments;
- transport/storage encryption and key ownership;
- logging, telemetry, fixture, and support-tool handling;
- masking/tokenization requirements;
- export and vendor-transfer controls;
- retention, backup, restore, and secure-deletion handling;
- incident severity and notification routing.

Classify by the most sensitive meaningful combination, not by one field in isolation. A large aggregate or identity-linked data set may be more sensitive than each attribute separately.

## Rule `DATA-LIFECYCLE-01`: retention and deletion cover every copy

For each governed data class, define:

```text
collect -> validate -> use -> derive/share -> retain/archive -> delete or legal hold
```

- Collect only what the declared purpose needs.
- Give retention a trigger, duration, owner, and executable deletion/archive mechanism.
- Distinguish soft delete, reversible archive, anonymization, and irreversible deletion.
- Define referential, audit, financial, and legal-hold exceptions explicitly.
- Propagate deletion/expiry to caches, search, analytics, files, queues, materialized data, vendors, and replicas.
- Document how expired data ages out of backups and what happens if an older backup is restored.
- Verify scheduled lifecycle work; a written retention period without an executing job is not a control.

Do not use soft delete as permanent retention by default. Do not promise immediate erasure from immutable backups when the real contract is expiry plus access restriction and re-deletion after restore.

## Rule `DATA-ISOLATION-01`: environments, tenants, and workloads do not share trust accidentally

- Production and non-production use separate identities, secrets, endpoints, and data stores unless an approved design proves otherwise.
- Production-sensitive data entering a lower environment is masked, minimized, or synthesized first.
- Tenant scope applies consistently to records, indexes, files, caches, events, exports, jobs, uniqueness rules, and restores.
- Application, migration, backup, reporting, and administrative identities receive distinct least-privilege access where risk warrants it.
- Encryption keys and recovery access are separated from the protected data and from routine application access.
- Break-glass access is time-bounded where possible and audited.

Select row, schema, database, account, region, or deployment isolation from the system profile. Test the selected boundary; folder naming or a `tenantId` column alone is not proof.

## Rule `DATA-ACCESS-MODE-01`: every task declares one data authority

Each task envelope selects exactly one mode, names the target, allowed interface, guard evidence, and stop condition:

| Mode | Allowed purpose | Required boundary |
| --- | --- | --- |
| `NONE` | Code/docs/static work needing no data access | No database or live-data connection |
| `LIVE_READ` | Bounded inspection of current data/schema | Approved least-privilege read-only interface; prove read-only state before the minimum-column query |
| `TEST_MUTATION` | Mutation and assertion reads for executable proof | Disposable isolated target through a repository-owned guarded wrapper |
| `PRODUCTION_HANDOFF` | Prepare an operator-applied production change | Exact reviewed artifact, pre/postchecks, recovery and ownership; no mutation in the handoff task |

If the approved live-read interface is unavailable or its read-only state is unproved, stop; never fall back to application credentials, an ad hoc direct connection, a backup, or another wider interface. Reject write-like functions and analysis forms that execute statements under `LIVE_READ` even if their syntax begins as a read.

For `TEST_MUTATION`, the wrapper that launches the mutating process validates the complete normalized target identity, proves it is disposable and distinct from every live target, and requires the repository's explicit test acknowledgement immediately before execution. A separate preflight, shell override, filename convention, or environment name is not a guard. Run setup, mutation, migration replay, and assertion reads through that guarded path; never copy live data to make the test pass.

Changing mode changes authority and therefore creates a dependent task with a new envelope. In particular, close guarded test proof before creating a production handoff; do not silently turn inspection into mutation or execute handoff instructions on behalf of the operator.

## Rule `SCHEMA-HISTORY-01`: versioned migration history is the schema source of truth

The accepted stack profile selects the migration mechanism and file format. Core requires these observable outcomes rather than prescribing a tool:

- Commit ordered schema migrations and any required data transformation logic.
- Verify canonical order and content integrity before execution; fail on missing, reordered, duplicated, or altered applied entries.
- Review generated SQL/DDL before it reaches a persistent environment.
- Never edit or delete an already-applied migration as routine repair.
- Detect and reconcile drift rather than normalizing undocumented manual changes.
- Make empty-database bootstrap and upgrade from supported existing versions explicit contracts.
- Use one controlled migration executor per environment; concurrent deploys must not race schema changes.
- Record the application versions compatible with each transition.

Prototype synchronization/reset commands are not production migration strategies. Production change uses reviewed, repeatable, observable steps.

## Rule `MIGRATION-COMPAT-01`: evolve with expand, migrate, and contract

Use [templates/data-migration.md](templates/data-migration.md) for a material schema/data/ownership transition.

For a breaking schema or meaning change:

```text
EXPAND
  add backward-compatible schema/capability
MIGRATE
  deploy compatible code, backfill/reconcile, observe adoption
CONTRACT
  remove legacy reads/writes/schema only after evidence shows no consumer remains
```

Requirements:

- old and new application versions can coexist during the deployment window;
- the deploy order for schema, readers, writers, workers, and vendors is explicit;
- dual-read/write is temporary, owned, observable, and has a removal condition;
- contract steps wait for usage, queue, replica, and rollback windows to clear;
- API/event/data consumers receive a compatibility or versioning plan;
- destructive cleanup is a separate reviewed change.

Prefer roll-forward repair after data mutation. A code rollback is not automatically a data rollback and must not depend on a column/table already removed.

## Rule `MIGRATION-SAFETY-01`: estimate lock, time, and failure impact before execution

For each production migration, inspect:

- affected rows/bytes, table/index size, and expected duration;
- lock level and blocking risk;
- transaction boundaries and transaction-log/WAL growth;
- full-table rewrites, validation scans, index builds, and constraint timing;
- replication, connection-pool, disk, and resource impact;
- statement/lock timeout, pause/abort criteria, and safe retry behavior;
- pre/post invariants, counts, checksums, samples, and monitoring;
- rollback versus roll-forward procedure.

Test on a representative data shape when cost can scale materially. Schedule, throttle, or split the operation when the normal deployment window cannot safely contain it.

A backup is a recovery control, not permission to run an unreviewed destructive command.

## Rule `BACKFILL-RESUMABLE-01`: large data changes are bounded, idempotent, and observable

Design a backfill with:

- stable chunk key/order and bounded batch size;
- durable checkpoint or safely repeatable selection;
- idempotent per-record transformation;
- concurrency/ownership strategy when live writes continue;
- rate and resource limits;
- retry classification and terminal-failure capture;
- progress, error, age, and reconciliation metrics;
- pause, resume, cancel, and restart behavior;
- source-versus-target verification before contract cleanup.

Avoid one unbounded transaction. Do not paginate mutable work by deep offset when rows can move between pages. If dual writes are required, define which source wins, how divergence is detected, and how repair occurs.

## Rule `RECOVERY-OBJECTIVES-01`: business impact sets RPO and RTO

For each critical data/service contract, define:

- **RPO:** maximum acceptable committed-data loss;
- **RTO:** maximum acceptable time to restore the required service level;
- recovery scope and dependency order;
- minimum usable state versus full restoration;
- accountable decision maker and communication path.

Derive backup frequency, point-in-time capability, replication, retention, staffing, and runbooks from these objectives. Do not copy one RPO/RTO across systems with different impact.

## Rule `BACKUP-RESTORE-01`: backups are isolated, protected, monitored, and restorable

Backup design covers applicable databases, objects/files, schemas, configuration, encryption/key dependencies, and vendor/export state needed for recovery.

- Automate backup creation and failure alerting.
- Encrypt in transit and at rest; restrict and audit restore/delete access.
- Keep recovery copies in an independent failure/security domain appropriate to risk.
- Define retention, immutability/tamper resistance, and deletion policy.
- Use point-in-time recovery when the RPO requires it.
- Track backup age, completeness, and integrity evidence.
- Prevent an application compromise from silently deleting every recovery copy.

A green backup job proves only that an artifact was produced. Restore tests prove whether it is usable.

## Rule `RECOVERY-DRILL-01`: rehearse recovery in an isolated environment

A recovery drill must:

1. select a declared failure and recovery point;
2. restore without overwriting the source environment;
3. re-establish required identity, key, configuration, schema, and dependency state;
4. run structural and business-invariant verification;
5. measure actual data loss and elapsed recovery time;
6. exercise cutover/failback or document why it is excluded;
7. record gaps, owners, deadlines, and updated runbooks.

Run drills at a frequency justified by criticality and after material topology/recovery changes. Include scenarios such as operator deletion, bad migration, credential compromise, regional/provider loss, or corrupted data when applicable.

## Rule `MULTI-STORE-DR-01`: replicated recovery prevents split brain and proves failback

Adopt cross-region, cross-provider, or multiple-writable-store recovery only when declared failure modes and RPO/RTO cannot be met more simply. Record why restore, same-provider standby, or a single writer is insufficient; active-active is not a default maturity badge.

When a critical contract can move between stores or regions:

- define the authoritative writer and use a monotonic epoch/fencing token, provider control, or equivalent write-admission mechanism so the old writer cannot resume after promotion; DNS or load-balancer routing alone is not fencing;
- declare replication mode, measurable lag, data-loss window, consistency across database/object/event/config/key dependencies, and behavior for an incomplete dependency set;
- give failover a decision owner, health/lag gates, old-writer isolation step, promotion order, invariant verification, traffic ramp, and abort/repair path;
- make jobs, webhooks, schedulers, locks, idempotency records, and external side effects safe when ownership moves;
- treat failback as a separate migration: stop or fence conflicting writes, compare and reconcile divergence, rebuild replication, rotate the ownership epoch, ramp traffic, and observe before retiring the temporary topology;
- rehearse both directions with representative data and measure achieved RPO/RTO, duplicate/lost effects, reconciliation time, and operator access.

If several authoritative stores cannot share one recovery point, document the allowed inconsistent state and business reconciliation order. Stop if two sites can accept the same non-commutative write without fencing, promotion can proceed with unknown lag, or failback means simply reversing traffic.

## Acceptance evidence

- [ ] Data inventory covers authoritative, derived, queued, logged, backed-up, exported, and vendor-held data.
- [ ] Classification drives environment, access, masking, encryption, retention, and incident handling.
- [ ] Retention/deletion jobs and propagation paths have deterministic verification.
- [ ] Tenant and environment isolation have automated negative evidence.
- [ ] Every data-touching task records one mode; live reads have no direct fallback and test mutations cannot bypass the in-process target guard.
- [ ] Migration history can bootstrap an empty store and upgrade every supported baseline.
- [ ] Breaking changes have an expand-migrate-contract sequence and compatibility/removal gates.
- [ ] Large backfills are bounded, resumable, idempotent, observable, and reconciled.
- [ ] Critical data contracts declare RPO/RTO and a dependency-aware recovery order.
- [ ] Backup monitoring and access controls are active.
- [ ] A recent isolated restore drill measured recovery and verified business invariants.
- [ ] Where multi-store/regional failover is required, a recent drill proves fencing, dependency order, measured data loss, reconciliation, and controlled failback; otherwise the simpler recovery choice and rationale are recorded.

## Stop conditions

Stop and redesign when no authoritative source is known, a data mode or guarded target is ambiguous, live inspection needs a direct fallback, tenant or environment isolation depends on caller discipline, retention has no executable deletion path, an applied migration must be rewritten, a breaking schema change assumes instantaneous deploy, a backfill cannot resume safely, migration lock/size impact is unknown on a large store, RPO/RTO are unstated, every backup shares the production failure domain, multi-store promotion lacks fencing/failback proof, or no restore has ever been verified.
