---
guide_id: REFAPP-CAPABILITIES
title: Capability Coverage and Reference Domain
status: experimental
audience: human-and-ai
read_when:
  - Selecting the capability tier, reference domain, feature set, or proof that the app demonstrates the parent blueprint.
skip_when:
  - Implementing one already-mapped vertical slice.
depends_on:
  - README.md
  - ../05-semantic-pattern-selection.md
owns:
  - risk-selected reference-application capability tiers
  - FulfillOps reference domain and smaller domain slices
  - domain-substitution and coverage gate
  - preset capability-status and walking-slice coverage mapping
---

# Capability coverage and reference domain

> Demonstrate the smallest capability set justified by system risk. Do not turn an ordinary web app into an enterprise showcase merely to fill a registry.

## Rule `REF-COVERAGE-TIER-01`: risk selects the coverage preset

Choose one primary tier from the current parent system/risk profile. The required set is the union of that tier and any individually added capability. Tiers are not maturity ranks; `REGULATED` can be operationally stricter than `FULL_SHOWCASE` while implementing fewer product archetypes.

| Tier | Select when | Required capability IDs |
| --- | --- | --- |
| `BASIC_WEB` | One bounded web workflow/record lifecycle, ordinary data and no proven tenant/async/vendor/regulatory complexity | `CAP-CRUD`, `CAP-QUERY`, `CAP-ACCESSIBILITY`, `CAP-TEST-FITNESS`, `CAP-OBSERVABILITY`, `CAP-DELIVERY-RECOVERY` |
| `MULTI_TENANT_SAAS` | Organization-scoped data, membership or resource isolation is material | `BASIC_WEB` + `CAP-IDENTITY`, `CAP-TENANCY`, `CAP-TRANSACTION`, `CAP-AUDIT-PRIVACY` |
| `ASYNC_INTEGRATION` | Durable background work or an external protocol has partial-failure/replay risk | `BASIC_WEB` + `CAP-WORKFLOW`, `CAP-ASYNC`, `CAP-INTEGRATION`, `CAP-TRANSACTION`, `CAP-IDEMPOTENCY`, `CAP-RECONCILIATION` |
| `REGULATED` | Sensitive/regulated data, higher identity assurance, retention, audit or recovery obligations dominate | `BASIC_WEB` + `CAP-IDENTITY`, `CAP-TRANSACTION`, `CAP-AUDIT-PRIVACY`; threat/access/data/release artifacts are mandatory and assurance adds `CAP-ADVANCED-IDENTITY` when required |
| `FULL_SHOWCASE` | The explicit goal is to demonstrate every core archetype and control in one coherent product | Every core capability in the registry below; external providers/cache/production readiness remain conditional |

`BASIC_WEB` is the default when no stronger driver is present. If two specialized risks apply, keep the smaller primary tier and add the other capability rows explicitly instead of jumping automatically to `FULL_SHOWCASE`. Every unselected row records `NOT_SELECTED`, owner, rationale and revisit trigger in [templates/capability-coverage.md](templates/capability-coverage.md).

## Rule `REF-COVERAGE-01`: every selected capability has one real proof

Use one implementation and one evidence path for each selected capability. More screens do not increase coverage when they repeat the same contract.

### Core capability registry

| Capability ID | Parent archetype/control | FulfillOps reference proof | Primary journey |
| --- | --- | --- | --- |
| `CAP-CRUD` | `PAT-SIMPLE-CRUD` | Customer or catalog record lifecycle | `JRN-CUSTOMER-CATALOG` |
| `CAP-WORKFLOW` | `PAT-DOMAIN-WORKFLOW` | Order/reservation/payment/shipment states | `JRN-ORDER` |
| `CAP-READMODEL` | `PAT-READMODEL` | Rebuildable order-operations projection | `JRN-OPERATIONS` |
| `CAP-ASYNC` | `PAT-ASYNC-EVENT` | Order outbox/inbox and notification delivery | `JRN-ORDER`, `JRN-NOTIFICATION` |
| `CAP-INTEGRATION` | `PAT-INTEGRATION` | Deterministic payment provider and authenticated webhook | `JRN-PAYMENT` |
| `CAP-BATCH` | `PAT-BATCH-IMPORT` | Resumable catalog/inventory import | `JRN-IMPORT` |
| `CAP-RECONCILIATION` | `PAT-RECONCILIATION` | Payment compare/repair | `JRN-PAYMENT`, `JRN-RECOVERY` |
| `CAP-IDENTITY` | Identity/session boundary | Session lifecycle and trusted subject | `JRN-ONBOARD` |
| `CAP-TENANCY` | Resource authorization/isolation | Membership, tenant-scoped resources and deny paths | `JRN-ONBOARD`, `JRN-TENANT-DENY` |
| `CAP-QUERY` | Query/page/cache boundary | Bounded list/search with stable identity | `JRN-CUSTOMER-CATALOG`, `JRN-OPERATIONS` |
| `CAP-FILES` | File boundary/lifecycle | Product media and import source through `FileStore` | `JRN-CUSTOMER-CATALOG`, `JRN-IMPORT` |
| `CAP-TRANSACTION` | Transaction/concurrency | Membership, stock or invoice invariant | Tier-selected journey |
| `CAP-IDEMPOTENCY` | Command/event/webhook dedupe | Same-key submit and duplicate delivery | `JRN-ORDER`, `JRN-PAYMENT` |
| `CAP-AUDIT-PRIVACY` | Audit/privacy lifecycle | Audit search and customer export/anonymization | `JRN-RECOVERY`, `JRN-TENANT-DENY` |
| `CAP-ACCESSIBILITY` | Accessible runtime states | Selected forms, lists, dialogs and journeys | Every selected browser journey |
| `CAP-TEST-FITNESS` | Tests/architecture fitness | Layered tests and dependency/runtime checks | Every selected journey |
| `CAP-OBSERVABILITY` | Correlation/SLO/telemetry | Selected critical path and operated failure signal | `JRN-OPERATIONS` or tier journey |
| `CAP-DELIVERY-RECOVERY` | CI/release/migration/recovery | Reproducible artifact, migration and bounded recovery proof | `JRN-RECOVERY` or release journey |

### Conditional/extension registry

| Capability ID | Select when | Default |
| --- | --- | --- |
| `CAP-EMAIL-PROVIDER` | Real external email delivery is required | Local/sandbox sink only |
| `CAP-CARRIER-PROVIDER` | A real carrier protocol adds product value | Deterministic internal dispatch |
| `CAP-CACHE` | Measured query/rate need justifies a cache | No business cache |
| `CAP-ADVANCED-IDENTITY` | Assurance requires MFA, passkeys, SSO, SCIM or equivalent | Basic selected identity boundary |
| `CAP-PRODUCTION-READINESS` | Claiming readiness for a real deployment | Not assessed by reference/showcase completion |

## Rule `REF-DOMAIN-01`: scale the FulfillOps domain to the tier

When the user supplies no domain, use the smallest coherent FulfillOps slice:

| Tier | Default modules and outcome |
| --- | --- |
| `BASIC_WEB` | `MOD-CRM` or `MOD-CATALOG`: create, edit, archive, search and view records |
| `MULTI_TENANT_SAAS` | `MOD-WORKSPACES` + `MOD-CRM`: invite/member lifecycle and tenant-scoped customer records |
| `ASYNC_INTEGRATION` | `MOD-ORDERS` + one owned integration/notification adapter; add only data owners needed by the workflow |
| `REGULATED` | `MOD-WORKSPACES` + `MOD-CRM` + `MOD-GOVERNANCE`: governed records, privacy request, privileged audit and recovery |
| `FULL_SHOWCASE` | All FulfillOps modules and closed journeys below |

### FulfillOps module catalog

| Module ID | Owns | Selected when |
| --- | --- | --- |
| `MOD-WORKSPACES` | Organization, membership, invitations and current-subject capabilities | Tenancy or governed identity |
| `MOD-CRM` | Customers, addresses and privacy requests | Basic record or regulated data slice |
| `MOD-CATALOG` | Sellable definitions, pricing and product-media links | Catalog/files/import slice |
| `MOD-INVENTORY` | Warehouses, stock ledger, availability and reservations | Contested inventory workflow |
| `MOD-ORDERS` | Order intent, snapshots, totals and lifecycle coordination | Workflow/async slice |
| `MOD-BILLING` | Invoices, payment intents and reconciliation | Payment integration/full showcase |
| `MOD-FULFILLMENT` | Shipment state and optional carrier policy | Fulfillment/full showcase |
| `MOD-NOTIFICATIONS` | Notification and delivery intent/state | Selected notification/async capability |
| `MOD-DATA-EXCHANGE` | Stored-file metadata and import/export lifecycle | File or batch capability |
| `MOD-INSIGHTS` | Read-only projections | Read-model capability |
| `MOD-GOVERNANCE` | Audit queries, system roles and privileged operations routing | Regulated/full governance capability |

Platform owns mechanisms; selected modules own policy. Unselected modules, tables, routes, jobs and providers are absent—not empty placeholders.

## Closed journey registry

1. `JRN-ONBOARD`: sign in -> create/select organization -> invite/member change when tenancy is selected.
2. `JRN-CUSTOMER-CATALOG`: create -> validate -> persist -> bounded search/detail -> archive.
3. `JRN-ORDER`: create/edit/submit -> durable allocation result when workflow/async is selected.
4. `JRN-PAYMENT`: issue invoice -> signed duplicate webhook -> one balance effect -> reconcile ambiguity.
5. `JRN-FULFILLMENT`: dispatch eligibility -> consume reservation -> deliver or exception.
6. `JRN-NOTIFICATION`: business event -> delivery intent -> failure inspection/replay.
7. `JRN-IMPORT`: upload -> preview -> checkpointed rows -> partial error -> resume.
8. `JRN-OPERATIONS`: selected query/projection freshness -> correlated operational evidence.
9. `JRN-RECOVERY`: selected failure -> alert/runbook -> repair, replay or restore evidence.
10. `JRN-TENANT-DENY`: wrong tenant, stale role and disabled-member direct-call denial.

Only journeys needed by selected capabilities are critical. `FULL_SHOWCASE` closes all ten; other tiers record unselected journeys with rationale instead of fake screens or tests.

## Rule `REF-PRESET-COVERAGE-01`: preset support and application selection are separate

An `AUTHOR_PRESET` maps its reusable capabilities in [preset-contract](templates/preset-contract.md) with one of four states:

| Status | Meaning |
| --- | --- |
| `provided` | Code/contract exists, but the complete exact-version flow is not yet proven |
| `verified` | A clean-room walking slice proves the complete selected inter-layer flow |
| `conditional` | Support depends on a named environment, provider, risk decision or unresolved gate |
| `unsupported` | The preset intentionally omits the capability and its placeholder code |

At minimum classify starter/runtime, shared UI surfaces, query/data, auth/session, feature/app composition and verification capabilities. Optional table/list/calendar/file/async/provider capabilities receive separate rows so one passing CRUD path cannot certify all surfaces.

`INSTANTIATE_PRESET` still selects application `CAP-*` rows from the current risk profile. A preset's `verified` row means the combination can support that flow; it does not select the capability for the app, prove the app implemented it or remove any readiness control. Every app-selected capability retains its own owner, journey and evidence.

## Domain substitution

A custom domain is accepted after the `COVERAGE-*` artifact maps every selected capability to:

- one coherent user/operator outcome and `JRN-*`;
- one owner `MOD-*` and authoritative data owner;
- one route/job/entrypoint;
- the lowest sufficient planned `EVID-*` path;
- conditional `NOT_SELECTED` decisions with owner and revisit trigger.

The substitute may combine modules differently. It does not need workflow, batch, vendor, tenancy or reconciliation when the selected union does not require them.

## Stop conditions

Stop when preset support is confused with app selection, a `verified` preset row lacks an exact-version walking slice, the tier is chosen from desired code volume rather than risk, `FULL_SHOWCASE` is used as the ordinary default, a selected capability has no journey/owner/evidence, unselected capabilities leave placeholder infrastructure, modules are named after screens/libraries, features share write ownership, or documentation/mocked UI is counted as implementation proof.
