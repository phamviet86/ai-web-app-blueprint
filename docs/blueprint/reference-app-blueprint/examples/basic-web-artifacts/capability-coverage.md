---
artifact_id: COVERAGE-READING-001
artifact_type: capability-coverage
schema_version: "1.0"
artifact_version: 1
title: BASIC_WEB capability coverage for Reading List
status: accepted
owner: example-product-owner
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:reading-list
  - tier:basic-web
source_template: REFAPP-TPL-CAPABILITY-COVERAGE@1.0.0
supersedes: []
superseded_by: null
review_by: 2026-08-12
expires_at: null
---

# Example only: Reading List capability coverage

> Accepted planning decision, not implementation evidence. `PLANNED` rows support no readiness score above `0.00`.

## Selection gate

- Primary tier: `BASIC_WEB`.
- Additive capabilities: none.
- Domain: one `MOD-BOOKS` record lifecycle.
- Tier rationale: local, single-scope, synchronous CRUD/query with ordinary synthetic data.
- [x] The primary tier is the smallest preset covering current risks.
- [x] Every selected row has an owner, journey, planned `EVID-*`, and candidate `CTL-*`/`GATE-*` consumer.
- [x] Every unselected row has an owner and revisit trigger; none removes a catalog control.
- [x] All evidence is honestly `PLANNED` and supports readiness score `0.00` only.

| Capability | Decision and rationale | Owner / dependency / journey | Planned evidence | Parent bridge | N/A owner/revisit |
| --- | --- | --- | --- | --- | --- |
| `CAP-CRUD` | `SELECTED`; tier baseline | `MOD-BOOKS`; `DATA-BOOKS`; book routes; `JRN-BOOK-MAINTAIN` | `EVID-APP-001`, `EVID-DB-001`, `EVID-WEB-001` `PLANNED` | `CTL-ARCH-MODULES-01`, `CTL-CONTRACT-OWNERSHIP-01`, `CTL-CONTRACT-SHAPES-01`, `GATE-GREENFIELD-01` | — |
| `CAP-WORKFLOW` | `NOT_SELECTED`; no state graph/high-value workflow | Product owner | None | Does not make reliability controls N/A | Product owner; revisit on stateful workflow |
| `CAP-READMODEL` | `NOT_SELECTED`; bounded owner query suffices | Product owner | None | `CTL-DATA-INTEGRITY-01` still assessed | Product owner; revisit on different grain/freshness |
| `CAP-ASYNC` | `NOT_SELECTED`; no durable deferred work | Product owner | None | Does not make `CTL-REL-ASYNC-01` N/A automatically | Product owner; revisit on durable work |
| `CAP-INTEGRATION` | `NOT_SELECTED`; no external protocol | Product owner | None | Does not make `CTL-REL-INTEGRATION-01` N/A automatically | Product owner; revisit on vendor/protocol |
| `CAP-BATCH` | `NOT_SELECTED`; no bulk submission | Product owner | None | Catalog row remains in readiness input | Product owner; revisit on bulk import |
| `CAP-RECONCILIATION` | `NOT_SELECTED`; one authority | Product owner | None | Catalog row remains in readiness input | Product owner; revisit on multiple representations |
| `CAP-IDENTITY` | `NOT_SELECTED`; localhost only | Security owner | None | `CTL-SEC-AUTHZ-01` remains score `0.00` until applicability evidence | Security owner; revisit before exposure |
| `CAP-TENANCY` | `NOT_SELECTED`; one local dataset | Security/data owners | None | Tenant-related controls remain assessed | Security owner; revisit on organization scope |
| `CAP-QUERY` | `SELECTED`; tier baseline | `MOD-BOOKS`; `DATA-BOOKS`; `ROUTE-BOOK-LIST`; `JRN-BOOK-MAINTAIN` | `EVID-DB-002`, `EVID-WEB-001` `PLANNED` | `CTL-CONTRACT-OWNERSHIP-01`, `CTL-DATA-INTEGRITY-01`, `CTL-UX-CAPACITY-01` | — |
| `CAP-FILES` | `NOT_SELECTED`; no upload | Product owner | None | File/security controls are not removed | Product owner; revisit on upload |
| `CAP-TRANSACTION` | `NOT_SELECTED`; no contested multi-owner invariant | Books owner | None | Basic command atomicity remains under contract/data controls | Books owner; revisit on contested invariant |
| `CAP-IDEMPOTENCY` | `NOT_SELECTED`; no replayable external/durable command | Books owner | None | Reliability controls remain assessed | Books owner; revisit on replay/retry |
| `CAP-AUDIT-PRIVACY` | `NOT_SELECTED`; synthetic public metadata | Data owner | None | `CTL-SEC-LIFECYCLE-01` and governance controls remain assessed | Data owner; revisit on personal/sensitive data |
| `CAP-ACCESSIBILITY` | `SELECTED`; tier baseline | Books presentation; all book routes; `JRN-BOOK-MAINTAIN` | `EVID-A11Y-001` `PLANNED` | `CTL-UX-NATIVE-01`, `CTL-UX-BUDGET-01`, `GATE-GREENFIELD-01` | — |
| `CAP-TEST-FITNESS` | `SELECTED`; tier baseline | Repository tooling; selected journey | `EVID-ARCH-001`, `EVID-CI-001` `PLANNED` | `CTL-TEST-RISK-01`, `CTL-TEST-LAYERS-01`, `CTL-TEST-DATA-01`, `CTL-TEST-FITNESS-01` | — |
| `CAP-OBSERVABILITY` | `SELECTED`; tier baseline | `PLATFORM-READING-001`; selected journey | `EVID-OBS-001` `PLANNED` | `CTL-OPS-TELEMETRY-01` | — |
| `CAP-DELIVERY-RECOVERY` | `SELECTED`; bounded local handoff | Repository/operations; local journey | `EVID-MIG-001`, `EVID-RELEASE-001` `PLANNED` | `CTL-DELIVERY-ONBOARD-01`, `CTL-DELIVERY-CI-01`, `CTL-DELIVERY-ARTIFACT-01`, `CTL-DELIVERY-RELEASE-01`, `CTL-DATA-RECOVERY-01`, `GATE-GREENFIELD-01` | — |
| `CAP-EMAIL-PROVIDER` | `NOT_SELECTED`; no recipient effect | Product owner | None | No control removed | Product owner; revisit on email |
| `CAP-CARRIER-PROVIDER` | `NOT_SELECTED`; no fulfillment | Product owner | None | No control removed | Product owner; revisit on carrier |
| `CAP-CACHE` | `NOT_SELECTED`; no measured cache need | Data owner | None | `CTL-UX-CAPACITY-01` still assessed | Data owner; revisit after measurement |
| `CAP-ADVANCED-IDENTITY` | `NOT_SELECTED`; no identity boundary | Security owner | None | Security catalog rows remain assessed | Security owner; revisit with assurance requirement |
| `CAP-PRODUCTION-READINESS` | `NOT_SELECTED`; local planning example | Operations owner | None | `GATE-RELEASE-01` is N/A with owned rationale; baseline controls remain | Operations owner; revisit on deployment target |

## Coverage reconciliation

- Missing selected capability: none in the decision map; implementation remains absent.
- Selected row represented only by planning evidence: all six selected rows, so completion is blocked.
- Duplicate implementation: none because there is no implementation.
- Control bridge: [readiness input](readiness.json) contains all 40 controls and four gates.
- Decision: tier selection accepted for example planning; reference application is not ready.
