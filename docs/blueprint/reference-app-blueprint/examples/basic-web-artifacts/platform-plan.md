---
artifact_id: PLATFORM-READING-001
artifact_type: platform-plan
schema_version: "1.0"
artifact_version: 1
title: Selected platform mechanisms for Reading List
status: in-review
owner: example-web-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - tier:basic-web
source_template: REFAPP-TPL-PLATFORM-PLAN@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List platform plan

> Planning artifact. Mechanism choices are mapped, but no adapter, process, migration, health check, or telemetry result has been observed.

## Artifact control

- Upstream IDs: `SYS-READING-001`, `STACK-READING-001`, `COVERAGE-READING-001`.
- Selected capabilities/modules: `CAP-CRUD`, `CAP-QUERY`, `CAP-OBSERVABILITY`, `CAP-DELIVERY-RECOVERY`; `MOD-BOOKS`.
- Status remains `in-review` until `EVID-STACK-001` resolves the exact runtime and driver set.

## Capability and adapter matrix

| Capability | Owning need/module | Application-owned port | Local | Test | Preview/demo | Production starter | Replacement seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Config | Web/migration/test roots | Typed settings boundary | Local-safe settings | Isolated test settings | Not selected | Not selected | Configuration object injected at composition |
| Database | `MOD-BOOKS` | `BookStore`, transaction capability | PostgreSQL adapter | Isolated PostgreSQL adapter | Not selected | Not selected | Application-owned port |
| Telemetry | Web root + Books | Safe log/correlation contract | Structured console | Captured structured output | Not selected | Not selected | Exporter adapter |
| Identity, HTTP vendor, storage, email, jobs, cache, flags | Not selected | None | Absent | Controlled absence | Not selected | Not selected | New capability decision required |

## Executable composition

| Root | Selected by capability | Runtime/deploy unit | Concrete adapters | Startup/shutdown | Health/owner |
| --- | --- | --- | --- | --- | --- |
| Web | Baseline CRUD/query | Synchronous Django process | Settings, logs, PostgreSQL Books adapter | Validate/start; process drain | Local liveness; web team |
| Migration | `CAP-DELIVERY-RECOVERY` | Management command | Settings, PostgreSQL migrations | Apply and exit | Exit status; data owner |
| Test | `CAP-TEST-FITNESS` | Isolated test runner | Deterministic fixtures and test DB | Create/reset/close | Test report; quality owner |
| Worker/lab | Not selected | Absent | None | None | Revisit on async/operated capability |

## Configuration and trust

| Config/secret class | Server/public | Environments | Validation/rotation | Trust boundary | Owner |
| --- | --- | --- | --- | --- | --- |
| Database connection | Server secret | Local/test | Required, parsed once; example credential only | Process -> PostgreSQL | Platform DB owner |
| Debug/host mode | Server config | Local/test | Explicit local-safe allowlist | Browser -> web process | Web owner |
| Browser public config | None | None | No serialized environment | Server/browser | Web owner |

## Failure and operations evidence

| Mechanism | Failure policy | Required evidence | Telemetry/runbook | Status/owner |
| --- | --- | --- | --- | --- |
| Config | Fail startup on missing/invalid required value | `EVID-STACK-001` | Safe startup error | `PLANNED`; web owner |
| Database | Bounded connection/transaction; safe dependency error | `EVID-DB-001`, `EVID-MIG-001` | Correlation, no payload | `PLANNED`; data owner |
| Telemetry | Logging failure must not fabricate success | `EVID-OBS-001` | Local output only | `PLANNED`; web owner |

## Acceptance

- Provider/ORM/framework containment: designed; verification `EVID-ARCH-001` is planned.
- Demo side effects: no external side-effect adapter selected.
- Migration path: planned, not proven.
- Blocking gap: exact compatible runtime/driver lock and all observed evidence.
