---
artifact_id: PLAN-READING-001
artifact_type: reference-app-plan
schema_version: "1.0"
artifact_version: 1
title: Consolidated BASIC_WEB Reading List plan
status: draft
owner: example-web-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - tier:basic-web
source_template: REFAPP-TPL-REFERENCE-APP-PLAN@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List reference application plan

> Decision-complete illustration, intentionally `draft`. No source application, build, runtime, deployment, or verified `EVID-*` exists.

## Artifact control

- Goal/target: local `BASIC_WEB` showcase.
- Selected capabilities: `CAP-CRUD`, `CAP-QUERY`, `CAP-ACCESSIBILITY`, `CAP-TEST-FITNESS`, `CAP-OBSERVABILITY`, `CAP-DELIVERY-RECOVERY`.
- Blocking upstream statuses: `SYS-READING-001` draft; `STACK-READING-001` and `PLATFORM-READING-001` in-review; test/release plans draft.

## Artifact registry

| Artifact/applicability | Status | Locator | Decision |
| --- | --- | --- | --- |
| `REGISTRY-READING-001` | draft | [registry](artifact-registry.md) | Canonical example index |
| `SYS-READING-001` | draft | [system](system-profile.md) | Human acceptance absent |
| `STACK-READING-001` | in-review | [stack](stack-profile.md) | Compatibility spike planned |
| `COVERAGE-READING-001` | accepted | [coverage](capability-coverage.md) | `BASIC_WEB`, no additions |
| `DATA-READING-001` | accepted | [data](data-model.md) | One `DATA-BOOKS` authority |
| Shared plan | not-required | Applicability decision | One module, no promoted shared contract; revisit on second semantic consumer |
| `PLATFORM-READING-001` | in-review | [platform](platform-plan.md) | Config/database/telemetry only |
| `FEATURE-READING-BOOKS-001` | accepted | [feature](feature-books.md) | Books contract design |
| `ROUTES-READING-001` | accepted | [routes](route-map.md) | One `JRN-BOOK-MAINTAIN` |
| `TEST-READING-001` | draft | [tests](test-strategy.md) | All checks planned |
| SLO/access/threat artifacts | not-required | Applicability decision | Local synthetic scope; revisit before exposure/identity/sensitive data |
| `RELEASE-READING-001` | draft | [release](release-plan.md) | Bounded local handoff only |
| `ASSESSMENT-READING-001` | draft | [assessment](readiness-assessment.md), [JSON](readiness.json) | All 40 controls score `0.00` |

## End-to-end traceability

| Capability | Module/artifacts | Route/journey/slice | Evidence/status | Candidate parent consumers |
| --- | --- | --- | --- | --- |
| `CAP-CRUD` | `MOD-BOOKS`; feature/data/platform | Book create/edit/archive; `JRN-BOOK-MAINTAIN`; `SLICE-BOOKS-001` | `EVID-APP-001`, `EVID-DB-001`, `EVID-WEB-001` `PLANNED` | `CTL-ARCH-MODULES-01`, `CTL-CONTRACT-OWNERSHIP-01`, `CTL-CONTRACT-SHAPES-01`, `GATE-GREENFIELD-01` |
| `CAP-QUERY` | `MOD-BOOKS`; feature/data | `ROUTE-BOOK-LIST`; `JRN-BOOK-MAINTAIN`; `SLICE-BOOKS-001` | `EVID-DB-002`, `EVID-WEB-001` `PLANNED` | `CTL-DATA-INTEGRITY-01`, `CTL-UX-CAPACITY-01` |
| `CAP-ACCESSIBILITY` | Books presentation/routes | Selected journey; `SLICE-BOOKS-001` | `EVID-A11Y-001` `PLANNED` | `CTL-UX-NATIVE-01`, `CTL-UX-BUDGET-01`, `GATE-GREENFIELD-01` |
| `CAP-TEST-FITNESS` | Test strategy/tooling | All slices | `EVID-ARCH-001`, `EVID-CI-001` `PLANNED` | `CTL-TEST-RISK-01`, `CTL-TEST-LAYERS-01`, `CTL-TEST-DATA-01`, `CTL-TEST-FITNESS-01` |
| `CAP-OBSERVABILITY` | Platform + Books | Web path; all slices | `EVID-OBS-001` `PLANNED` | `CTL-OPS-TELEMETRY-01` |
| `CAP-DELIVERY-RECOVERY` | System/platform/release | `SLICE-FOUNDATION-001`, `SLICE-HANDOFF-001` | `EVID-STACK-001`, `EVID-MIG-001`, `EVID-RELEASE-001` `PLANNED` | `CTL-DELIVERY-ONBOARD-01`, `CTL-DELIVERY-CI-01`, `CTL-DELIVERY-ARTIFACT-01`, `CTL-DELIVERY-RELEASE-01`, `GATE-GREENFIELD-01` |

## Control and readiness bridge

| Controls/gate | Source capability/artifact | Evidence state | Assessment result |
| --- | --- | --- | --- |
| Architecture/contracts/data | CRUD/query/system/feature/data | Planned IDs only | Catalog rows present, score `0.00` |
| Security/reliability controls without selected feature capability | System profile and explicit `NOT_SELECTED` decisions | No reviewed N/A evidence claimed | Conservatively applicable, score `0.00` |
| UX/testing | Accessibility/query/test strategy | Planned IDs only | Score `0.00` |
| Delivery/operations/governance | System/platform/release/registry | Planned or missing | Score `0.00` |
| `GATE-GREENFIELD-01` | All selected capabilities/slices | Planning reference only; no observed pass | Applicable and failed |
| Other `GATE-*` rows | Operating-mode/target decision | Owned N/A rationale in JSON | Not applicable |

- Complete catalog input: [readiness.json](readiness.json), catalog/scorer `1.0.0`.
- Assessment artifact: `ASSESSMENT-READING-001` version 1.
- Every one of 40 `CTL-*` rows and four `GATE-*` rows is present; no `CAP-* NOT_SELECTED` row deletes a catalog control.

## Architecture and structure

- One modular web application; web/migration/test roots; `MOD-BOOKS` owns `DATA-BOOKS`.
- Django templates/HTMX map full and partial responses; full-page fallback remains required.
- Platform contains only config, PostgreSQL connection/transaction, and safe local logging mechanisms.
- No identity, tenant, worker, provider, file, cache, SLO, or hosted release capability is selected.

## Implementation slices

| Slice | Outcome | Dependencies/delta | Compatibility | Planned evidence | Exit/rollback |
| --- | --- | --- | --- | --- | --- |
| `SLICE-FOUNDATION-001` | Clean local setup and empty app | Stack/platform; initial migration/config | Initial schema only | `EVID-STACK-001`, `EVID-MIG-001`, `EVID-ARCH-001`, `EVID-CI-001` | Blocked until observed; recreate local database |
| `SLICE-BOOKS-001` | Maintain and search books | Feature/data/routes | Public commands/query v1 | `EVID-APP-001`, `EVID-DB-001`, `EVID-DB-002`, `EVID-WEB-001`, `EVID-A11Y-001`, `EVID-OBS-001` | Blocked until observed; revert slice/migration locally |
| `SLICE-HANDOFF-001` | Repeatable local start/smoke/reset | Test/release artifacts | No deployed compatibility window | `EVID-RELEASE-001` | Blocked until observed; no publication |

## Demo and release

- Intended commands are documented in `RELEASE-READING-001` but unresolved until the repository exists.
- Public demo, production deployment, backup restore, SLO/on-call, and real-user safety are explicitly out of scope and prohibited.
- Any hosted target triggers new system, identity/access/threat, SLO, release, and readiness decisions.

## Completion evidence

| Capability/journey | Implementation | Evidence status | Owner | Result |
| --- | --- | --- | --- | --- |
| All six selected `CAP-*`; `JRN-BOOK-MAINTAIN` | Absent | Every `EVID-*` is `PLANNED`; none observed/verified | Example owners above | Gap; not complete |

- Blocking unknown count: runtime/driver lock, every implementation result, every runtime result.
- Showcase-ready decision: no.
- Production readiness: not assessed and prohibited from inference.
